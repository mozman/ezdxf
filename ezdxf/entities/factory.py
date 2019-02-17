# Created: 2019-02-15
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from ezdxf.tools.handle import ImageKeyGenerator, UnderlayKeyGenerator
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.entities.dxfentity import DXFEntity, DXFTagStorage

if TYPE_CHECKING:
    from ezdxf.eztypes import Table, DXFDictionary, BlocksSection
    from ezdxf.entitydb import EntityDB
    from ezdxf.drawing2 import Drawing

__all__ = ['EntityFactory', 'register_entity']

ENTITY_CLASSES = {}  # registered classes


def register_entity(cls):
    name = cls.DXFTYPE
    ENTITY_CLASSES[name] = cls
    return cls


DEFAULT_CLASS = DXFTagStorage


class EntityFactory:
    def __init__(self, doc: 'Drawing'):
        self.doc = doc
        self.image_key_generator = ImageKeyGenerator()
        self.underlay_key_generator = UnderlayKeyGenerator()

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    @property
    def dxfversion(self):
        return self.doc.dxfversion

    @property
    def rootdict(self) -> 'DXFDictionary':
        return self.doc.rootdict

    @property
    def blocks(self) -> 'BlocksSection':
        return self.doc.blocks

    @property
    def block_records(self) -> 'Table':
        return self.doc.sections.tables.block_records

    def new_entity(self, dxftype: str, dxfattribs: dict = None) -> 'DXFEntity':
        """ Create a new entity. """
        class_ = ENTITY_CLASSES.get(dxftype, DEFAULT_CLASS)
        entity = class_.new(handle=None, owner=None, dxfattribs=dxfattribs, doc=self.doc)
        # track used DXF types, but only for new created DXF entities
        self.doc.tracker.dxftypes.add(dxftype)
        return entity

    def create_db_entry(self, type_: str, dxfattribs: dict) -> 'DXFEntity':
        """ Create new entity and add to drawing-database. """
        entity = self.new_entity(dxftype=type_, dxfattribs=dxfattribs)
        self.entitydb.add(entity)
        return entity

    def load(self, tags: 'ExtendedTags') -> 'DXFEntity':
        entity = self.entity(tags)
        self.doc.entitydb.add(entity)
        return entity

    def entity(self, tags: 'ExtendedTags') -> 'DXFEntity':
        if not isinstance(tags, ExtendedTags):
            tags = ExtendedTags(tags)
        dxftype = tags.dxftype()
        class_ = ENTITY_CLASSES.get(dxftype, DEFAULT_CLASS)
        entity = class_.load(tags, self.doc)
        return entity

    def next_image_key(self, checkfunc=lambda k: True) -> str:
        while True:
            key = self.image_key_generator.next()
            if checkfunc(key):
                return key

    def next_underlay_key(self, checkfunc=lambda k: True) -> str:
        while True:
            key = self.underlay_key_generator.next()
            if checkfunc(key):
                return key
