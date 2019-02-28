# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Union, Sequence, List
import logging

from ezdxf.lldxf.const import DXFStructureError, DXFAttributeError, DXFBlockInUseError, DXFTableEntryError
from ezdxf.lldxf import const
from ezdxf.entities.dxfgfx import entity_linker
from ezdxf.layouts.blocklayout import BlockLayout

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from ezdxf.drawing2 import Drawing
    from ezdxf.entitydb import EntityDB
    from ezdxf.entities.dxfentity import DXFEntity, DXFTagStorage
    from ezdxf.entities.factory import EntityFactory
    from ezdxf.entities.blockrecord import BlockRecord
    from ezdxf.entities.block import Block, EndBlk
    from ezdxf.sections.tables2 import Table


class BlocksSection:
    """
    Manages BLOCK definitions in a dict(). Since v0.8.5 ezdxf uses a lower case key. 'Test' == 'TEST', to behave
    like AutoCAD.

    """
    def __init__(self, doc: 'Drawing' = None, entities: List['DXFEntity'] = None, block_records: 'Table' = None):
        # Mapping of BlockLayouts, for dict() order of blocks is random,
        # if turns out later, that blocks order is important: use an OrderedDict().
        self._block_layouts = dict()
        self.doc = doc
        if entities is not None:
            self.load(entities, block_records)
        self._anonymous_block_counter = 0

    def __len__(self):
        return len(self._block_layouts)

    @staticmethod
    def key(entity: Union[str, 'BlockLayout']) -> str:
        if not isinstance(entity, str):
            entity = entity.name
        return entity.lower()  # block key is lower case

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    @property
    def dxffactory(self) -> 'EntityFactory':
        return self.doc.dxffactory

    def load(self, entities: List['DXFEntity'], block_records: 'Table') -> None:

        def build_block_layout(block_entities: Sequence['DXFEntity']) -> 'BlockLayout':
            block = block_entities[0]  # type: Block
            endblk = block_entities[-1]  # type: EndBlk

            try:
                block_record = block_records.get(block.dxf.name)  # type: BlockRecord
            except DXFTableEntryError:  # special case DXF R12 - not block record exists
                block_record = block_records.new(block.dxf.name)  # type: BlockRecord
                block.dxf.owner = block_record.dxf.handle
                endblk.dxf.owner = block_record.dxf.handle

            block_layout = BlockLayout(block_record, block, endblk, self.doc)
            for entity in block_entities[1:-1]:
                block_layout.add_entity(entity)
            return block_layout

        def link_entities() -> Iterable['DXFEntity']:
            linked = entity_linker()
            for entity in entities:
                if not linked(entity):  # don't store linked entities (VERTEX, ATTRIB, SEQEND) in block layout
                    yield entity

        section_head = entities[0]  # type: DXFTagStorage
        if section_head.dxftype() != 'SECTION' or section_head.base_class[1] != (2, 'BLOCKS'):
            raise DXFStructureError("Critical structure error in BLOCKS section.")
        del entities[0]  # remove SECTION entity
        block_entities = []
        for entity in link_entities():
            block_entities.append(entity)
            if entity.dxftype() == 'ENDBLK':
                block_layout = build_block_layout(block_entities)
                try:
                    name = block_layout.name
                except DXFAttributeError:
                    raise
                if name in self:
                    logger.warning(
                        'Warning! Multiple block definitions with name "{}", replacing previous definition'.format(
                            block_layout.name))
                self.add(block_layout)
                block_entities = []

    def add(self, block_layout: 'BlockLayout') -> None:
        """
        Add or replace a block object.

        Args:
            block_layout: BlockLayout() object

        """
        self._block_layouts[self.key(block_layout.name)] = block_layout

    def __iter__(self) -> Iterable['BlockLayout']:
        return iter(self._block_layouts.values())

    def __contains__(self, name: str) -> bool:
        return self.key(name) in self._block_layouts

    def __getitem__(self, name: str) -> 'BlockLayout':
        return self._block_layouts[self.key(name)]

    def __delitem__(self, name: str) -> None:
        del self._block_layouts[self.key(name)]

    def get(self, name: str, default=None) -> 'BlockLayout':
        try:
            return self.__getitem__(name)
        except KeyError:  # internal exception
            return default

    def get_block_layout_by_handle(self, block_record_handle: str) -> 'BlockLayout':
        """
        Returns a block layout by block record handle.

        """
        block_record = self.doc.entitydb[block_record_handle]
        return self.get(block_record.dxf.name)

    def new(self, name: str, base_point: Sequence[float] = (0, 0), dxfattribs: dict = None) -> 'BlockLayout':
        """
        Create a new named block.

        """
        block_record = self.doc.block_records.new(name)  # type: BlockRecord

        dxfattribs = dxfattribs or {}
        dxfattribs['owner'] = block_record.dxf.handle
        dxfattribs['name'] = name
        dxfattribs['name2'] = name
        dxfattribs['base_point'] = base_point

        head = self.dxffactory.create_db_entry('BLOCK', dxfattribs)  # type: Block
        tail = self.dxffactory.create_db_entry('ENDBLK', {'owner': block_record.dxf.handle})  # type: EndBlk
        block_layout = BlockLayout(block_record, head, tail, self.doc)
        self.add(block_layout)
        return block_layout

    def new_anonymous_block(self, type_char: str = 'U', base_point: Sequence[float] = (0, 0)) -> 'BlockLayout':
        blockname = self.anonymous_blockname(type_char)
        block = self.new(blockname, base_point, {'flags': const.BLK_ANONYMOUS})
        return block

    def anonymous_blockname(self, type_char: str) -> str:
        """
        Create name for an anonymous block.

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
        """
        Renames the block and the associated block record.

        """
        block_layout = self.get(old_name)  # block key is lower case
        block_layout.name = new_name

        if self.doc.dxfversion > 'AC1009':
            block_record = self.doc.block_records.get(old_name)
            block_record.dxf.name = new_name
        self.__delitem__(old_name)
        self.add(block_layout)  # add new dict entry

    def delete_block(self, name: str, safe: bool = True) -> None:
        """
        Delete block. If save is True, check if block is still referenced.

        Args:
            name: block name (case insensitive)
            safe: check if block is still referenced

        Raises:
            DXFKeyError() if block not exists
            DXFValueError() if block is still referenced, and save is True

        """
        if safe:
            block_refs = self.doc.query("INSERT[name=='{}']i".format(name))  # ignore case
            if len(block_refs):
                raise DXFBlockInUseError(
                    'Block "{}" is still in use and can not deleted. (Hint: block name is case insensitive!)'.format(
                        name))
        block_layout = self[name]
        block_layout.destroy()
        self.__delitem__(name)

    def delete_all_blocks(self, safe: bool = True) -> None:
        """
        Delete all blocks except layout blocks (model space or paper space).

        Args:
            safe: check if block is still referenced and ignore them if so

        """
        if safe:
            # block names are case insensitive
            references = set(entity.dxf.name.lower() for entity in self.doc.query('INSERT'))

        def is_save(name: str) -> bool:
            return name.lower() not in references if safe else True

        # do not delete blocks defined for layouts
        if self.doc.dxfversion > 'AC1009':
            layout_keys = set(layout.layout_key for layout in self.doc.layouts)
            for block in list(self):
                name = block.name
                if block.block_record_handle not in layout_keys and is_save(name):
                    # safety check is already done
                    self.delete_block(name, safe=False)
        else:
            for block_name in list(self._block_layouts.keys()):
                if block_name not in ('$model_space', '$paper_space') and is_save(block_name):
                    # safety check is already done
                    self.delete_block(block_name, safe=False)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str("  0\nSECTION\n  2\nBLOCKS\n")
        for block in self._block_layouts.values():
            block.export_dxf(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

    def new_layout_block(self) -> 'BlockLayout':

        def block_name(_count):
            return "*Paper_Space%d" % _count

        count = 0
        while block_name(count) in self:
            count += 1

        block_layout = self.new(block_name(count))
        return block_layout
