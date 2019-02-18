# Created: 2019-02-18
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Sequence, Optional
from ezdxf.lldxf.const import LAYOUT_NAMES
from ezdxf.entitydb import EntitySpace
from .base import BaseLayout

if TYPE_CHECKING:
    from ezdxf.lldxf.tagwriter import TagWriter
    from ezdxf.drawing2 import Drawing
    from ezdxf.entities.blockrecord import BlockRecord
    from ezdxf.entities.block import Block, EndBlk
    from ezdxf.entities.dxfentity import DXFEntity


class BlockLayout(BaseLayout):
    """
    BlockLayout has the same factory-function as Layout, but is managed
    in the BlocksSection() class. It represents a DXF Block definition.

    Attributes:
        block:  BLOCK entity
        endblk: ENDBLK entity

    """

    def __init__(self,
                 block_record: 'BlockRecord',
                 block: 'Block',
                 endblk: 'EndBlk',
                 doc: 'Drawing' = None, ):
        super().__init__(block_record, doc, EntitySpace())
        self.block = block
        self.endblk = endblk

    def __contains__(self, entity: 'DXFEntity') -> bool:
        """
        Returns True if block contains entity else False. *entity* can be a handle-string, Tags(),
        ExtendedTags() or a wrapped entity.

        """
        if isinstance(entity, str):
            entity = self.entitydb[entity]
        return entity in self.entity_space

    @property
    def name(self) -> str:
        """ Get block name """
        return self.block.dxf.name

    @name.setter
    def name(self, new_name) -> None:
        """ Set block name """
        block = self.block
        block.dxf.name = new_name
        block.dxf.name2 = new_name

    @property
    def is_layout_block(self) -> bool:
        """
        True if block is a model space or paper space block definition.

        """
        return self.block.is_layout_block

    def get_entity_space(self) -> EntitySpace:
        return self.entity_space

    def set_entity_space(self, entity_space: EntitySpace) -> None:
        self.entity_space = entity_space

    def add_attdef(self, tag: str, insert: Sequence[float] = (0, 0), text: str = '',
                   dxfattribs: dict = None) -> 'DXFEntity':
        """
        Add an :class:`Attdef` entity.

        Set position and alignment by the idiom::

            myblock.add_attdef('NAME').set_pos((2, 3), align='MIDDLE_CENTER')

        Args:
            tag: attribute name (tag) as string without spaces
            insert: attribute insert point relative to block origin (0, 0, 0)
            text: preset text for attribute

        """
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['tag'] = tag
        dxfattribs['insert'] = insert
        dxfattribs['text'] = text
        return self.new_entity('ATTDEF', dxfattribs)

    def attdefs(self) -> Iterable['DXFEntity']:
        """
        Iterate for all :class:`Attdef` entities.

        """
        return (entity for entity in self if entity.dxftype() == 'ATTDEF')

    def has_attdef(self, tag: str) -> bool:
        """
        Returns `True` if an :class:`Attdef` for `tag` exists else `False`.

        Args:
            tag: tag name

        """
        return self.get_attdef(tag) is not None

    def get_attdef(self, tag: str) -> Optional['DXFEntity']:
        """
        Get attached :class:`Attdef` entity by `tag`.

        Args:
            tag: tag name

        Returns: :class:`Attdef`

        """
        for attdef in self.attdefs():
            if tag == attdef.dxf.tag:
                return attdef

    def get_attdef_text(self, tag: str, default: str = None) -> str:
        """
        Get content text for :class:`Attdef` `tag` as string or returns `default` if no :class:`Attdef` for `tag` exists.

        Args:
            tag: tag name
            default: default value if tag is absent

        """
        attdef = self.get_attdef(tag)
        if attdef is None:
            return default
        return attdef.dxf.text

    # end of public interface

    def add_entity(self, entity: 'DXFEntity') -> None:
        """
        Add an existing DXF entity to a layout, but be sure to unlink (:meth:`~Layout.unlink_entity()`) first the entity
        from the previous owner layout.

        Args:
            entity: :class:`DXFEntity`

        """
        # set a model space, because paper space layout is a different class
        entity.set_owner(self.block_record_handle, paperspace=0)
        self.entity_space.add(entity)

    def add_handle(self, handle: str) -> None:
        """
        Add entity by handle to the block entity space.

        """
        self.add_entity(self.entitydb[handle])

    def export_dxf_block(self, tagwriter: 'TagWriter') -> None:
        self.block.export_dxf(tagwriter)
        self.entity_space.export_dxf(tagwriter)
        self.endblk.export_dxf(tagwriter)

    def export_dxf(self, tagwriter: 'TagWriter'):
        # BLOCK section: do not write content of model space and active layout
        if self.name.lower() in LAYOUT_NAMES:
            save = self.entity_space
            self.entity_space = EntitySpace()
            self.export_dxf_block(tagwriter)
            self.entity_space = save
        else:
            self.export_dxf_block(tagwriter)

    def delete_all_entities(self) -> None:
        # 1. delete from database
        for entity in self.entity_space:
            self.entitydb.delete_entity(entity)
        # 2. delete from entity space
        self.entity_space.clear()

    def destroy(self) -> None:
        self.doc.block_records.remove(self.name)
        self.delete_all_entities()
        self.entitydb.delete_entity(self.block)
        self.entitydb.delete_entity(self.endblk)

    def get_const_attdefs(self) -> Iterable['DXFEntity']:
        """
        Returns a generator for constant ATTDEF entities.

        """
        return (attdef for attdef in self.attdefs() if attdef.is_const)
