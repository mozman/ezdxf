# Created: 2019-02-18
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Optional, Union
from .base import BaseLayout

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFGraphic, AttDef


class BlockLayout(BaseLayout):
    """
    BlockLayout has the same factory-functions as Layout, but is managed
    in the :class:`BlocksSection` class. It represents a DXF Block.

    """
    def __contains__(self, entity: Union['DXFGraphic', str]) -> bool:
        """ Returns ``True`` if `entity` if stored in this block.

        Args:
             entity: :class:`DXFGraphic` object or handle as hex string

        """
        if isinstance(entity, str):
            entity = self.entitydb[entity]
        return entity in self.entity_space

    @property
    def block(self):
        """ Get the associated BLOCK entity. """
        return self.block_record.block

    @property
    def endblk(self):
        """ Get the associated ENDBLK entity. """
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
        """ DXF name space of associated BLOCK_RECORD. """
        return self.block_record.dxf

    def attdefs(self) -> Iterable['AttDef']:
        """ Iterate for all :class:`~ezdxf.entities.attrib.Attdef` entities. """
        return (entity for entity in self if entity.dxftype() == 'ATTDEF')

    def has_attdef(self, tag: str) -> bool:
        """ Returns ``True`` if an :class:`~ezdxf.entities.attrib.Attdef` for `tag`. """
        return self.get_attdef(tag) is not None

    def get_attdef(self, tag: str) -> Optional['DXFGraphic']:
        """ Get attached :class:`~ezdxf.entities.attrib.Attdef` entity by `tag`. """
        for attdef in self.attdefs():
            if tag == attdef.dxf.tag:
                return attdef

    def get_attdef_text(self, tag: str, default: str = None) -> str:
        """
        Get content text for :class:`~ezdxf.entities.attrib.Attdef` `tag` as string or returns `default` if no
        :class:`Attdef` for `tag` exist.

        Args:
            tag: tag name
            default: default value if tag is absent

        """
        attdef = self.get_attdef(tag)
        if attdef is None:
            return default
        return attdef.dxf.text

    def get_const_attdefs(self) -> Iterable['AttDef']:
        """ Returns a generator for constant ATTDEF entities. (internal API) """
        return (attdef for attdef in self.attdefs() if attdef.is_const)
