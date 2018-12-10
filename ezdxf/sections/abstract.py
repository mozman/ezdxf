# Purpose: entity section
# Created: 13.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Iterator
import abc

from ezdxf.lldxf.tags import DXFStructureError, DXFValueError
from ezdxf.lldxf.extendedtags import get_xtags_linker
from ezdxf.query import EntityQuery

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.lldxf.extendedtags import ExtendedTags
    from ezdxf.lldxf.tagwriter import TagWriter
    from ezdxf.dxfentity import DXFEntity
    from ezdxf.entityspace import EntitySpace
    from ezdxf.drawing import Drawing
    from ezdxf.dxffactory import DXFFactory
    from ezdxf.database import EntityDB


class AbstractSection:
    name = 'abstract'  # type: str

    def __init__(self, entity_space: 'EntitySpace', entities: Iterable['ExtendedTags'], drawing: 'Drawing'):
        self._entity_space = entity_space
        self.drawing = drawing
        if entities is not None:
            self._build(iter(entities))

    @property
    def dxffactory(self) -> 'DXFFactory':
        return self.drawing.dxffactory

    @property
    def entitydb(self) -> 'EntityDB':
        return self.drawing.entitydb

    def get_entity_space(self) -> 'EntitySpace':
        return self._entity_space

    def _build(self, entities: Iterator['ExtendedTags']) -> None:
        section_head = next(entities)

        if section_head[0] != (0, 'SECTION') or section_head[1] != (2, self.name.upper()):
            raise DXFStructureError("Critical structure error in {} section.".format(self.name.upper()))

        linked_tags = get_xtags_linker()
        for entity in entities:
            if not linked_tags(entity):  # don't store linked entities (VERTEX, ATTRIB, SEQEND) in entity space
                self._entity_space.store_tags(entity)

    def write(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        self._entity_space.write(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

    def create_new_dxf_entity(self, _type: str, dxfattribs: dict) -> 'DXFEntity':
        """
        Create new DXF entity add it to th entity database and add it to the entity space.

        """
        dxf_entity = self.dxffactory.create_db_entry(_type, dxfattribs)
        self._entity_space.add_handle(dxf_entity.dxf.handle)
        return dxf_entity

    def add_handle(self, handle: str) -> None:
        self._entity_space.add_handle(handle)

    def remove_handle(self, handle: str) -> None:
        try:
            self._entity_space.remove(handle)
        except ValueError:
            raise DXFValueError('Handle #{} not in entity space.'.format(handle))

    def delete_entity(self, entity: 'DXFEntity') -> None:
        self.remove_handle(entity.dxf.handle)
        self.entitydb.delete_entity(entity)

    # start of public interface

    @abc.abstractmethod
    def __iter__(self) -> Iterable['DXFEntity']:
        pass

    def __len__(self) -> int:
        return len(self._entity_space)

    def __contains__(self, handle: str) -> bool:
        return handle in self._entity_space

    def query(self, query: str = '*') -> EntityQuery:
        return EntityQuery(iter(self), query)

    def delete_all_entities(self) -> None:
        """ Delete all entities. """
        self._entity_space.delete_all_entities()

    # end of public interface
