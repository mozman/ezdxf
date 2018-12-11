# Purpose: blocks section
# Created: 14.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Union, Iterator, Sequence
import logging

from ezdxf.lldxf.const import DXFStructureError, DXFAttributeError, DXFBlockInUseError
from ezdxf.lldxf import const
from ezdxf.lldxf.extendedtags import get_xtags_linker

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, BlockLayout, ExtendedTags, DXFFactoryType, EntityDB, TagWriter


class BlocksSection:
    """
    Manages BLOCK definitions in a dict(). Since v0.8.5 ezdxf uses a lower case key. 'Test' == 'TEST', to behave
    like AutoCAD.

    """
    name = 'BLOCKS'

    def __init__(self, entities: Iterable['ExtendedTags'], drawing: 'Drawing'):
        # Mapping of BlockLayouts, for dict() order of blocks is random,
        # if turns out later, that blocks order is important: use an OrderedDict().
        self._block_layouts = dict()
        self.drawing = drawing
        if entities is not None:
            self._build(iter(entities))
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
        return self.drawing.entitydb

    @property
    def dxffactory(self) -> 'DXFFactoryType':
        return self.drawing.dxffactory

    def _build(self, entities: Iterator['ExtendedTags']) -> None:
        def build_block_layout(handles: Sequence[str]) -> 'BlockLayout':
            block = self.dxffactory.new_block_layout(
                block_handle=handles[0],
                endblk_handle=handles[-1],
            )
            for handle in handles[1:-1]:
                block.add_handle(handle)
            return block

        def link_entities() -> Iterable['ExtendedTags']:
            linked_tags = get_xtags_linker()
            for entity in entities:
                if not linked_tags(entity):  # don't store linked entities (VERTEX, ATTRIB, SEQEND) in block layout
                    yield entity

        section_head = next(entities)
        if section_head[0] != (0, 'SECTION') or section_head[1] != (2, 'BLOCKS'):
            raise DXFStructureError("Critical structure error in BLOCKS section.")

        handles = []
        for xtags in link_entities():
            handles.append(xtags.get_handle())
            if xtags.dxftype() == 'ENDBLK':
                block_layout = build_block_layout(handles)
                try:
                    name = block_layout.name
                except DXFAttributeError:
                    raise
                if block_layout.name in self:
                    logger.warning(
                        'Warning! Multiple block definitions with name "{}", replacing previous definition'.format(
                            block_layout.name))
                self.add(block_layout)
                handles = []

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

    def new(self, name: str, base_point: Sequence[float] = (0, 0), dxfattribs: dict = None) -> 'BlockLayout':
        """
        Create a new named block.

        """
        dxfattribs = dxfattribs or {}
        dxfattribs['name'] = name
        dxfattribs['name2'] = name
        dxfattribs['base_point'] = base_point
        head = self.dxffactory.create_db_entry('BLOCK', dxfattribs)
        tail = self.dxffactory.create_db_entry('ENDBLK', {})
        block_layout = self.dxffactory.new_block_layout(head.dxf.handle, tail.dxf.handle)
        self.dxffactory.create_block_entry_in_block_records_table(block_layout)
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

        if self.drawing.dxfversion > 'AC1009':
            block_record = self.drawing.block_records.get(old_name)
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
            block_refs = self.drawing.query("INSERT[name=='{}']i".format(name))  # ignore case
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
            references = set(entity.dxf.name.lower() for entity in self.drawing.query('INSERT'))

        def is_save(name: str) -> bool:
            return name.lower() not in references if safe else True

        # do not delete blocks defined for layouts
        if self.drawing.dxfversion > 'AC1009':
            layout_keys = set(layout.layout_key for layout in self.drawing.layouts)
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

    def write(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str("  0\nSECTION\n  2\nBLOCKS\n")
        for block in self._block_layouts.values():
            block.write(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

    def new_layout_block(self) -> 'BlockLayout':

        def block_name(_count):
            return "*Paper_Space%d" % _count

        count = 0
        while block_name(count) in self:
            count += 1

        block_layout = self.new(block_name(count))
        return block_layout
