# Created: 2019-02-15
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Union
from ezdxf.tools.handle import ImageKeyGenerator, UnderlayKeyGenerator
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.entities.dxfentity import DXFEntity, DXFTagStorage
from ezdxf.lldxf.const import DXFInternalEzdxfError

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing

__all__ = ['EntityFactory', 'register_entity', 'ENTITY_CLASSES']

ENTITY_CLASSES = {}  # registered classes


def register_entity(cls):
    name = cls.DXFTYPE
    if name in ENTITY_CLASSES:
        raise DXFInternalEzdxfError('Double registration for DXF type {}.'.format(name))
    ENTITY_CLASSES[name] = cls
    return cls


DEFAULT_CLASS = DXFTagStorage


class EntityFactory:
    def __init__(self, doc: 'Drawing' = None):
        self.doc = doc
        self.image_key_generator = ImageKeyGenerator()
        self.underlay_key_generator = UnderlayKeyGenerator()

    def new_entity(self, dxftype: str, dxfattribs: dict = None) -> 'DXFEntity':
        """ Create a new entity. """
        class_ = ENTITY_CLASSES.get(dxftype, DEFAULT_CLASS)
        entity = class_.new(handle=None, owner=None, dxfattribs=dxfattribs, doc=self.doc)
        self.doc.tracker.dxftypes.add(dxftype)
        return entity.cast() if hasattr(entity, 'cast') else entity

    def create_db_entry(self, type_: str, dxfattribs: dict) -> 'DXFEntity':
        """ Create new entity and add to drawing-database. """
        entity = self.new_entity(dxftype=type_, dxfattribs=dxfattribs)
        self.doc.entitydb.add(entity)
        if hasattr(entity, 'seqend'):
            seqend = self.create_db_entry('SEQEND', dxfattribs={'layer': entity.dxf.layer})
            self.doc.entitydb.add(seqend)
            entity.seqend = seqend
        return entity

    def load(self, tags: Union['ExtendedTags', 'Tags']) -> 'DXFEntity':
        entity = self.entity(tags)
        self.doc.entitydb.add(entity)
        return entity

    def entity(self, tags: Union['ExtendedTags', 'Tags']) -> 'DXFEntity':
        if not isinstance(tags, ExtendedTags):
            tags = ExtendedTags(tags)
        dxftype = tags.dxftype()
        class_ = ENTITY_CLASSES.get(dxftype, DEFAULT_CLASS)
        entity = class_.load(tags, self.doc)
        return entity.cast() if hasattr(entity, 'cast') else entity

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
