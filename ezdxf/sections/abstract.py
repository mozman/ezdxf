# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from itertools import islice

from ..lldxf.tags import group_tags, DXFStructureError
from ..lldxf.extendedtags import ExtendedTags, get_tags_linker
from ..query import EntityQuery
from ..lldxf.validator import entity_structure_validator
from ..options import options


class AbstractSection(object):
    name = 'abstract'

    def __init__(self, entity_space, tags, drawing):
        self._entity_space = entity_space
        self.drawing = drawing
        if tags is not None:
            self._build(tags)

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    @property
    def entitydb(self):
        return self.drawing.entitydb

    def get_entity_space(self):
        return self._entity_space

    def _build(self, tags):
        if tags[0] != (0, 'SECTION') or tags[1] != (2, self.name.upper()) or tags[-1] != (0, 'ENDSEC'):
            raise DXFStructureError("Critical structure error in {} section.".format(self.name.upper()))

        if len(tags) == 3:  # empty entities section
            return

        linked_tags = get_tags_linker()
        store_tags = self._entity_space.store_tags
        entitydb = self.entitydb
        post_read_tags_fixer = self.dxffactory.post_read_tags_fixer
        check_tag_structure = options.check_entity_tag_structures
        for group in group_tags(islice(tags, 2, len(tags)-1)):
            if check_tag_structure:
                group = entity_structure_validator(group)
            tags = ExtendedTags(group)
            post_read_tags_fixer(tags)  # for VERTEX!
            handle = entitydb.add_tags(tags)
            if not linked_tags(tags, handle):  # also creates the link structure as side effect
                store_tags(tags)  # add to entity space

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        self._entity_space.write(stream)
        stream.write("  0\nENDSEC\n")

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
