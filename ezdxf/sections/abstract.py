# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

from ..lldxf.tags import DXFStructureError
from ..lldxf.extendedtags import get_xtags_linker
from ..query import EntityQuery


class AbstractSection(object):
    name = 'abstract'

    def __init__(self, entity_space, entities, drawing):
        self._entity_space = entity_space
        self.drawing = drawing
        if entities is not None:
            self._build(iter(entities))

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    @property
    def entitydb(self):
        return self.drawing.entitydb

    def get_entity_space(self):
        return self._entity_space

    def _build(self, entities):
        section_head = next(entities)

        if section_head[0] != (0, 'SECTION') or section_head[1] != (2, self.name.upper()):
            raise DXFStructureError("Critical structure error in {} section.".format(self.name.upper()))

        linked_tags = get_xtags_linker()
        for entity in entities:
            if not linked_tags(entity):  # don't store linked entities (VERTEX, ATTRIB, SEQEND) in entity space
                self._entity_space.store_tags(entity)

    def write(self, tagwriter):
        tagwriter.write_str("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        self._entity_space.write(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

    def create_new_dxf_entity(self, _type, dxfattribs):
        """ Create new DXF entity add it to th entity database and add it to the entity space.
        """
        dxf_entity = self.dxffactory.create_db_entry(_type, dxfattribs)
        self._entity_space.add_handle(dxf_entity.dxf.handle)
        return dxf_entity

    def add_handle(self, handle):
        self._entity_space.add_handle(handle)

    def remove_handle(self, handle):
        self._entity_space.remove(handle)

    def delete_entity(self, entity):
        self.remove_handle(entity.dxf.handle)
        self.entitydb.delete_entity(entity)

    # start of public interface

    def __len__(self):
        return len(self._entity_space)

    def __contains__(self, handle):
        return handle in self._entity_space

    def query(self, query='*'):
        return EntityQuery(iter(self), query)

    def delete_all_entities(self):
        """ Delete all entities. """
        self._entity_space.delete_all_entities()

    # end of public interface


