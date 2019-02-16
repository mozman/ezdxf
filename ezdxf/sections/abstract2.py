# Purpose: entity section
# Created: 13.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Iterator

from ezdxf.lldxf.tags import DXFStructureError
from ezdxf.query import EntityQuery

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.entitydb import EntitySpace, EntityDB
    from ezdxf.entities.dxfentity import DXFEntity, UnknownEntity, entity_linker
    from ezdxf.entities.factory import EntityFactory
    from ezdxf.drawing2 import Drawing
    from ezdxf.eztypes import TagWriter


class AbstractSection:
    name = 'abstract'  # type: str

    def __init__(self, entity_space: 'EntitySpace', entities: Iterable['DXFEntity'], doc: 'Drawing'):
        self._entity_space = entity_space
        self.doc = doc
        if entities is not None:
            self._build(iter(entities))

    @property
    def dxffactory(self) -> 'EntityFactory':
        return self.doc.dxffactory

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    def get_entity_space(self) -> 'EntitySpace':
        return self._entity_space

    def _build(self, entities: Iterator['DXFEntity']) -> None:
        section_head = next(entities)  # type: UnknownEntity

        if section_head.dxftype() == 'SECTION' or section_head.base_class[1] != (2, self.name.upper()):
            raise DXFStructureError("Critical structure error in {} section.".format(self.name.upper()))

        linked_entities = entity_linker()
        for entity in entities:
            if not linked_entities(entity):  # don't store linked entities (VERTEX, ATTRIB, SEQEND) in entity space
                self._entity_space.add(entity)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        self._entity_space.export_dxf(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

    def create_new_dxf_entity(self, _type: str, dxfattribs: dict) -> 'DXFEntity':
        """
        Create new DXF entity add it to the entity database and add it to the entity space.

        """
        dxf_entity = self.dxffactory.create_db_entry(_type, dxfattribs)
        self._entity_space.add(dxf_entity)
        return dxf_entity

    def delete_entity(self, entity: 'DXFEntity') -> None:
        self._entity_space.remove(entity)
        self.entitydb.delete_entity(entity)

    # start of public interface

    def __iter__(self) -> Iterable['DXFEntity']:
        return iter(self._entity_space)

    def __len__(self) -> int:
        return len(self._entity_space)

    def __contains__(self, entity: 'DXFEntity') -> bool:
        return entity in self._entity_space

    def query(self, query: str = '*') -> EntityQuery:
        return EntityQuery(iter(self), query)

    def delete_all_entities(self) -> None:
        """ Delete all entities. """
        db = self.entitydb
        for entity in self._entity_space:
            db.delete_entity(entity)
        self._entity_space.clear()

    # end of public interface
