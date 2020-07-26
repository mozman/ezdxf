# Copyright (c) 2011-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Union, Sequence, List, cast
import logging

from ezdxf.lldxf.const import (
    DXFStructureError, DXFBlockInUseError, DXFTableEntryError, DXFKeyError,
)
from ezdxf.lldxf import const
from ezdxf.entities.dxfgfx import entity_linker
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.render.arrows import ARROWS

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter, Drawing, EntityDB, DXFEntity, DXFTagStorage, Table,
        EntityFactory, BlockRecord, Block, EndBlk,
    )


def is_special_block(name: str) -> bool:
    name = name.upper()
    # Anonymous dimension, groups and table blocks do not have explicit
    # references by an INSERT entity:
    if name.startswith('*D') or name.startswith('*A') or name.startswith('*T'):
        return True

    # Arrow blocks maybe used in DIMENSION or LEADER override without an
    # INSERT reference:
    if ARROWS.is_ezdxf_arrow(name):
        return True
    if name.startswith('_'):
        if ARROWS.is_acad_arrow(ARROWS.arrow_name(name)):
            return True

    return False


class BlocksSection:
    """
    Manages BLOCK definitions in a dict(), block names are case insensitive
    e.g. 'Test' == 'TEST'.

    """

    def __init__(self, doc: 'Drawing' = None,
                 entities: List['DXFEntity'] = None):
        self.doc = doc
        if entities is not None:
            self.load(entities)
        self._reconstruct_orphaned_block_records()
        self._anonymous_block_counter = 0

    def __len__(self):
        return len(self.block_records)

    @staticmethod
    def key(entity: Union[str, 'BlockLayout']) -> str:
        if not isinstance(entity, str):
            entity = entity.name
        return entity.lower()  # block key is lower case

    @property
    def block_records(self) -> 'Table':
        return self.doc.block_records

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    @property
    def dxffactory(self) -> 'EntityFactory':
        return self.doc.dxffactory

    def load(self, entities: List['DXFEntity']) -> None:
        """
        Load DXF entities into BlockLayouts. `entities` is a list of
        entity tags, separated by BLOCK and ENDBLK entities.

        """

        def load_block_record(
                block_entities: Sequence['DXFEntity']) -> 'BlockRecord':
            block = cast('Block', block_entities[0])
            endblk = cast('EndBlk', block_entities[-1])

            try:
                block_record = cast('BlockRecord',
                                    block_records.get(block.dxf.name))
            except DXFTableEntryError:  # special case DXF R12 - not block record exists
                block_record = cast('BlockRecord',
                                    block_records.new(block.dxf.name,
                                                      dxfattribs={'scale': 0}))

            # The BLOCK_RECORD is the central object which stores all the
            # information about a BLOCK and also owns all the entities of
            # this block definition.
            block_record.set_block(block, endblk)
            for entity in block_entities[1:-1]:
                block_record.add_entity(entity)
            return block_record

        def link_entities() -> Iterable['DXFEntity']:
            linked = entity_linker()
            for entity in entities:
                # Do not store linked entities (VERTEX, ATTRIB, SEQEND) in
                # the block layout, linked entities ares stored in their
                # parent entity e.g. VERTEX -> POLYLINE:
                if not linked(entity):
                    yield entity

        block_records = self.block_records
        section_head: 'DXFTagStorage' = cast('DXFTagStorage', entities[0])
        if section_head.dxftype() != 'SECTION' or \
                section_head.base_class[1] != (2, 'BLOCKS'):
            raise DXFStructureError(
                "Critical structure error in BLOCKS section."
            )
        # Remove SECTION entity
        del entities[0]
        block_entities = []
        for entity in link_entities():
            block_entities.append(entity)
            if entity.dxftype() == 'ENDBLK':
                block_record = load_block_record(block_entities)
                self.add(block_record)
                block_entities = []

    def _reconstruct_orphaned_block_records(self):
        """
        Find BLOCK_RECORD entries without block definition in the blocks section and create block definitions for this
        orphaned block records.

        """
        for block_record in self.block_records:  # type: BlockRecord
            if block_record.block is None:
                block = self.doc.dxffactory.create_db_entry('BLOCK',
                                                            dxfattribs={
                                                                'name': block_record.dxf.name,
                                                                'name2': block_record.dxf.name,
                                                                'base_point': (
                                                                    0, 0, 0),
                                                            })
                endblk = self.doc.dxffactory.create_db_entry('ENDBLK',
                                                             dxfattribs={})
                block_record.set_block(block, endblk)
                self.add(block_record)

    def add(self, block_record: 'BlockRecord') -> 'BlockLayout':
        """ Add or replace a block layout object defined by its block record. (internal API)
        """
        block_layout = BlockLayout(block_record)
        block_record.block_layout = block_layout
        assert self.block_records.has_entry(block_record.dxf.name)
        return block_layout

    def __iter__(self) -> Iterable['BlockLayout']:
        """ Iterable of all :class:`~ezdxf.layouts.BlockLayout` objects. """
        return (block_record.block_layout for block_record in
                self.block_records)

    def __contains__(self, name: str) -> bool:
        """ Returns ``True`` if :class:`~ezdxf.layouts.BlockLayout` `name` exist. """
        return self.block_records.has_entry(name)

    def __getitem__(self, name: str) -> 'BlockLayout':
        """ Returns :class:`~ezdxf.layouts.BlockLayout` `name`, raises :class:`DXFKeyError` if `name` not exist. """
        try:
            block_record = cast('BlockRecord', self.block_records.get(name))
            return block_record.block_layout
        except DXFTableEntryError:
            raise DXFKeyError(name)

    def __delitem__(self, name: str) -> None:
        """ Deletes :class:`~ezdxf.layouts.BlockLayout` `name` and all of its content, raises
        :class:`DXFKeyError` if `name` not exist.
        """
        if name in self:
            self.block_records.remove(name)
        else:
            raise DXFKeyError(name)

    def get(self, name: str, default=None) -> 'BlockLayout':
        """ Returns :class:`~ezdxf.layouts.BlockLayout` `name`, returns `default` if `name` not exist. """
        try:
            return self.__getitem__(name)
        except DXFKeyError:
            return default

    def get_block_layout_by_handle(self,
                                   block_record_handle: str) -> 'BlockLayout':
        """ Returns a block layout by block record handle. (internal API)
        """
        return self.doc.entitydb[block_record_handle].block_layout

    def new(self, name: str, base_point: Sequence[float] = (0, 0),
            dxfattribs: dict = None) -> 'BlockLayout':
        """ Create and add a new :class:`~ezdxf.layouts.BlockLayout`, `name` is the BLOCK name, `base_point` is the
        insertion point of the BLOCK.
        """
        block_record = self.doc.block_records.new(name)

        dxfattribs = dxfattribs or {}
        dxfattribs['owner'] = block_record.dxf.handle
        dxfattribs['name'] = name
        dxfattribs['name2'] = name
        dxfattribs['base_point'] = base_point
        head = self.dxffactory.create_db_entry('BLOCK', dxfattribs)
        tail = self.dxffactory.create_db_entry('ENDBLK', {
            'owner': block_record.dxf.handle})
        block_record.set_block(head, tail)
        return self.add(block_record)

    def new_anonymous_block(self, type_char: str = 'U',
                            base_point: Sequence[float] = (
                                    0, 0)) -> 'BlockLayout':
        """ Create and add a new anonymous :class:`~ezdxf.layouts.BlockLayout`, `type_char` is the BLOCK type,
        `base_point` is the insertion point of the BLOCK.

            ========= ==========
            type_char Anonymous Block Type
            ========= ==========
            ``'U'``   ``'*U###'`` anonymous BLOCK
            ``'E'``   ``'*E###'`` anonymous non-uniformly scaled BLOCK
            ``'X'``   ``'*X###'`` anonymous HATCH graphic
            ``'D'``   ``'*D###'`` anonymous DIMENSION graphic
            ``'A'``   ``'*A###'`` anonymous GROUP
            ``'T'``   ``'*T###'`` anonymous block for ACAD_TABLE content
            ========= ==========

        """
        blockname = self.anonymous_blockname(type_char)
        block = self.new(blockname, base_point, {'flags': const.BLK_ANONYMOUS})
        return block

    def anonymous_blockname(self, type_char: str) -> str:
        """ Create name for an anonymous block. (internal API)

        Args:
            type_char: letter

                U = *U### anonymous blocks
                E = *E### anonymous non-uniformly scaled blocks
                X = *X### anonymous hatches
                D = *D### anonymous dimensions
                A = *A### anonymous groups
                T = *T### anonymous ACAD_TABLE content

        """
        while True:
            self._anonymous_block_counter += 1
            blockname = f"*{type_char}{self._anonymous_block_counter}"
            if not self.__contains__(blockname):
                return blockname

    def rename_block(self, old_name: str, new_name: str) -> None:
        """ Rename :class:`~ezdxf.layouts.BlockLayout` `old_name` to `new_name` """
        block_record: 'BlockRecord' = self.block_records.get(old_name)
        block_record.rename(new_name)
        self.block_records.replace(old_name, block_record)
        self.add(block_record)

    def delete_block(self, name: str, safe: bool = True) -> None:
        """
        Delete block. If `save` is ``True``, check if block is still referenced.

        Args:
            name: block name (case insensitive)
            safe: check if block is still referenced or special block without explicit references

        Raises:
            DXFKeyError() if block not exists
            DXFBlockInUseError() if block is still referenced, and save is True

        """
        if safe:
            if is_special_block(name):
                raise DXFBlockInUseError(
                    f'Special block "{name}" maybe used without explicit INSERT entity.')

            block_refs = self.doc.query(
                f"INSERT[name=='{name}']i")  # ignore case
            if len(block_refs):
                raise DXFBlockInUseError(
                    f'Block "{name}" is still in use and can not deleted.')
        self.__delitem__(name)

    def delete_all_blocks(self, safe: bool = True) -> None:
        """
        Delete all blocks except layout blocks (modelspace or paperspace).
        In safe mode, protected blocks are ignored silently.

        Args:
            safe: check if block is still referenced or special block without
            explicit references

        """
        if safe:
            # block names are case insensitive
            references = set(
                entity.dxf.name.lower() for entity in self.doc.query('INSERT'))

        def is_save(name: str) -> bool:
            if safe and is_special_block(name):
                return False
            return name.lower() not in references if safe else True

        # do not delete blocks defined for layouts
        layout_keys = set(layout.layout_key for layout in self.doc.layouts)
        for block in list(self):
            name = block.name
            if block.block_record_handle not in layout_keys and is_save(name):
                # safety check is already done
                self.delete_block(name, safe=False)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str("  0\nSECTION\n  2\nBLOCKS\n")
        for block_record in self.block_records:  # type: BlockRecord
            block_record.export_block_definition(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")
