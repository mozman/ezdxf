# Created: 2019-02-18
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Sequence, Optional
from .base import BaseLayout

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFGraphic, AttDef


class BlockLayout(BaseLayout):
    """
    BlockLayout has the same factory-function as Layout, but is managed
    in the BlocksSection() class. It represents a DXF Block definition.

    """
    def __contains__(self, entity: 'DXFGraphic') -> bool:
        """
        Returns True if block contains entity else False. *entity* can be a handle-string, Tags(),
        ExtendedTags() or a wrapped entity.

        """
        if isinstance(entity, str):
            entity = self.entitydb[entity]
        return entity in self.entity_space

    @property
    def block(self):
        return self.block_record.block

    @property
    def endblk(self):
        return self.block_record.endblk

    @property
    def name(self) -> str:
        """ Get block name """
        return self.block_record.dxf.name

    @name.setter
    def name(self, new_name) -> None:
        """ Set block and block_record name """
        self.block_record.rename(new_name)

    @property
    def dxf(self):
        """ Pass DXF name space of associated BLOCK_RECORD. """
        return self.block_record.dxf

    def attdefs(self) -> Iterable['AttDef']:
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

    def get_attdef(self, tag: str) -> Optional['DXFGraphic']:
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

    def get_const_attdefs(self) -> Iterable['AttDef']:
        """
        Returns a generator for constant ATTDEF entities.

        """
        return (attdef for attdef in self.attdefs() if attdef.is_const)
