# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Union, Sequence, List
import logging

from ezdxf.lldxf.const import DXFStructureError, DXFAttributeError, DXFBlockInUseError, DXFTableEntryError, DXFKeyError
from ezdxf.lldxf import const
from ezdxf.entities.dxfgfx import entity_linker
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.render.arrows import ARROWS

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, EntityDB, DXFEntity, DXFTagStorage, Table
    from ezdxf.eztypes import EntityFactory, BlockRecord, Block, EndBlk


def is_special_block(name: str) -> bool:
    name = name.upper()
    # Anonymous dimension, groups and table blocks do not have explicit references by INSERT entity
    if name.startswith('*D') or name.startswith('*A') or name.startswith('*T'):
        return True

    # Arrow blocks maybe used in LEADER override without INSERT reference.
    if ARROWS.is_ezdxf_arrow(name):
        return True
    if name.startswith('_'):
        if ARROWS.is_acad_arrow(ARROWS.arrow_name(name)):
            return True

    return False


class BlocksSection:
    """
    Manages BLOCK definitions in a dict(). Since v0.8.5 ezdxf uses a lower case key. 'Test' == 'TEST', to behave
    like AutoCAD.

    """

    def __init__(self, doc: 'Drawing' = None, entities: List['DXFEntity'] = None):
        # BlockLayouts stored as block_layout attribute in the BlockRecord object
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
        Load DXF entities into BlockLayouts. `entities` is a stream of entity tags, separated by BLOCK and ENDBLK
        entities into block layouts.

        """

        def load_block_record(block_entities: Sequence['DXFEntity']) -> 'BlockRecord':
            block = block_entities[0]  # type: Block
            endblk = block_entities[-1]  # type: EndBlk

            try:
                block_record = block_records.get(block.dxf.name)  # type: BlockRecord
            except DXFTableEntryError:  # special case DXF R12 - not block record exists
                block_record = block_records.new(block.dxf.name, dxfattribs={'scale': 0})  # type: BlockRecord

            # block_record stores all the information about a block definition
            block_record.set_block(block, endblk)
            for entity in block_entities[1:-1]:
                block_record.add_entity(entity)
                # block_record.add_entity(entity)  # add to block_record?
            return block_record

        def link_entities() -> Iterable['DXFEntity']:
            linked = entity_linker()
            for entity in entities:
                if not linked(entity):  # don't store linked entities (VERTEX, ATTRIB, SEQEND) in block layout
                    yield entity

        block_records = self.block_records
        section_head = entities[0]  # type: DXFTagStorage
        if section_head.dxftype() != 'SECTION' or section_head.base_class[1] != (2, 'BLOCKS'):
            raise DXFStructureError("Critical structure error in BLOCKS section.")
        del entities[0]  # remove SECTION entity
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
                block = self.doc.dxffactory.create_db_entry('BLOCK', dxfattribs={
                    'name': block_record.dxf.name,
                    'name2': block_record.dxf.name,
                    'base_point': (0, 0, 0),
                })
                endblk = self.doc.dxffactory.create_db_entry('ENDBLK', dxfattribs={})
                block_record.set_block(block, endblk)
                self.add(block_record)

    def add(self, block_record: 'BlockRecord') -> 'BlockLayout':
        """ Add or replace a block layout object defined by its block record.
        """
        block_layout = BlockLayout(block_record)
        block_record.block_layout = block_layout
        assert self.block_records.has_entry(block_record.dxf.name)
        return block_layout

    def __iter__(self) -> Iterable['BlockLayout']:
        return (block_record.block_layout for block_record in self.block_records)

    def __contains__(self, name: str) -> bool:
        return self.block_records.has_entry(name)

    def __getitem__(self, name: str) -> 'BlockLayout':
        try:
            block_record = self.block_records.get(name)  # type: BlockRecord
            return block_record.block_layout
        except DXFTableEntryError:
            raise DXFKeyError(name)

    def __delitem__(self, name: str) -> None:
        self.block_records.remove(name)

    def get(self, name: str, default=None) -> 'BlockLayout':
        try:
            return self.__getitem__(name)
        except DXFKeyError:
            return default

    def get_block_layout_by_handle(self, block_record_handle: str) -> 'BlockLayout':
        """ Returns a block layout by block record handle.
        """
        block_record = self.doc.entitydb[block_record_handle]  # type: BlockRecord
        return block_record.block_layout

    def new(self, name: str, base_point: Sequence[float] = (0, 0), dxfattribs: dict = None) -> 'BlockLayout':
        """ Create a new named block.
        """
        block_record = self.doc.block_records.new(name)  # type: BlockRecord

        dxfattribs = dxfattribs or {}
        dxfattribs['owner'] = block_record.dxf.handle
        dxfattribs['name'] = name
        dxfattribs['name2'] = name
        dxfattribs['base_point'] = base_point
        head = self.dxffactory.create_db_entry('BLOCK', dxfattribs)  # type: Block
        tail = self.dxffactory.create_db_entry('ENDBLK', {'owner': block_record.dxf.handle})  # type: EndBlk
        block_record.set_block(head, tail)
        return self.add(block_record)

    def new_anonymous_block(self, type_char: str = 'U', base_point: Sequence[float] = (0, 0)) -> 'BlockLayout':
        blockname = self.anonymous_blockname(type_char)
        block = self.new(blockname, base_point, {'flags': const.BLK_ANONYMOUS})
        return block

    def anonymous_blockname(self, type_char: str) -> str:
        """ Create name for an anonymous block.

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
            blockname = "*%s%d" % (type_char, self._anonymous_block_counter)
            if not self.__contains__(blockname):
                return blockname

    def rename_block(self, old_name: str, new_name: str) -> None:
        """ Renames the block and the associated block record.
        """
        block_record = self.block_records.get(old_name)  # type: BlockRecord
        block_record.rename(new_name)
        self.block_records.replace(old_name, block_record)
        self.add(block_record)

    def delete_block(self, name: str, safe: bool = True) -> None:
        """
        Delete block. If save is True, check if block is still referenced.

        Args:
            name: block name (case insensitive)
            safe: check if block is still referenced or special block without explicit references

        Raises:
            DXFKeyError() if block not exists
            DXFValueError() if block is still referenced, and save is True

        """
        if safe:
            if is_special_block(name):
                raise DXFBlockInUseError('Special block "{}" maybe used without explicit INSERT entity.'.format(name))

            block_refs = self.doc.query("INSERT[name=='{}']i".format(name))  # ignore case
            if len(block_refs):
                raise DXFBlockInUseError(
                    'Block "{}" is still in use and can not deleted. (Hint: block name is case insensitive!)'.format(
                        name))
        self.__delitem__(name)

    def delete_all_blocks(self, safe: bool = True) -> None:
        """
        Delete all blocks except layout blocks (model space or paper space).

        Args:
            safe: check if block is still referenced or special block without explicit references

        """
        if safe:
            # block names are case insensitive
            references = set(entity.dxf.name.lower() for entity in self.doc.query('INSERT'))

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
