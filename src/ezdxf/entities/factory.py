# Created: 2019-02-15
# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Union
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.entities.dxfentity import DXFEntity, DXFTagStorage
from ezdxf.lldxf.const import DXFInternalEzdxfError

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing

__all__ = [
    'EntityFactory', 'register_entity', 'ENTITY_CLASSES', 'replace_entity',
    'new', 'cls', 'is_bound'
]
# Stores all registered classes:
ENTITY_CLASSES = {}
DEFAULT_CLASS = DXFTagStorage


def replace_entity(cls):
    name = cls.DXFTYPE
    ENTITY_CLASSES[name] = cls
    return cls


def register_entity(cls):
    name = cls.DXFTYPE
    if name in ENTITY_CLASSES:
        raise DXFInternalEzdxfError(f'Double registration for DXF type {name}.')
    ENTITY_CLASSES[name] = cls
    return cls


def new(dxftype: str, dxfattribs: dict = None,
        doc: 'Drawing' = None) -> 'DXFEntity':
    """ Create a new entity, does not require an instantiated DXF document. """
    entity = cls(dxftype).new(
        handle=None,
        owner=None,
        dxfattribs=dxfattribs,
        doc=doc,
    )
    return entity.cast() if hasattr(entity, 'cast') else entity


def create_db_entry(dxftype, dxfattribs: dict, doc: 'Drawing') -> 'DXFEntity':
    entity = new(dxftype=dxftype, dxfattribs=dxfattribs)
    bind(entity, doc)
    if hasattr(entity, 'seqend') and entity.seqend is None:
        seqend = new('SEQEND',
                     dxfattribs={'layer': entity.dxf.layer},
                     )
        bind(seqend, doc)
        entity.seqend = seqend
    return entity


def load(tags: ExtendedTags) -> 'DXFEntity':
    assert isinstance(tags, ExtendedTags)
    entity = cls(tags.dxftype()).load(tags)
    return entity.cast() if hasattr(entity, 'cast') else entity


def cls(dxftype: str) -> 'DXFEntity':
    """ Returns registered class for `dxftype`. """
    return ENTITY_CLASSES.get(dxftype, DEFAULT_CLASS)


def bind(entity: 'DXFEntity', doc: 'Drawing') -> None:
    """ Bind `entity` to the DXF document `doc`.

    The bind process stores the DXF `entity` in the entity database of the DXF
    document.

    """
    assert entity.is_alive, 'Can not bind destroyed entity.'
    assert doc.entitydb is not None, 'Missing entity database.'
    entity.doc = doc
    doc.entitydb.add(entity)


def is_bound(entity: 'DXFEntity', doc: 'Drawing') -> bool:
    """ Returns ``True`` if `entity`is bound to DXF document `doc`.
    """
    if not entity.is_alive or \
            entity.is_virtual or \
            entity.doc is not doc:
        return False
    assert doc.entitydb, 'Missing entity database.'
    return entity.dxf.handle in doc.entitydb


class EntityFactory:
    def __init__(self, doc: 'Drawing' = None):
        self.doc = doc

    def new_entity(self, dxftype: str, dxfattribs: dict = None) -> 'DXFEntity':
        """ Create a new entity, requires an instantiated DXF document. """
        return new(dxftype, dxfattribs, self.doc)

    def create_db_entry(self, dxftype: str, dxfattribs: dict) -> 'DXFEntity':
        """ Create new entity and add to drawing-database. """
        return create_db_entry(dxftype, dxfattribs, self.doc)

    def load(self, tags: Union['ExtendedTags', 'Tags']) -> 'DXFEntity':
        if not isinstance(tags, ExtendedTags):
            tags = ExtendedTags(tags)
        entity = load(tags)
        bind(entity, self.doc)
        return entity
