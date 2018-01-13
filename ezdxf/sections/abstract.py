# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..lldxf.tags import group_tags, DXFStructureError
from ..lldxf.extendedtags import ExtendedTags, get_tags_linker
from ..query import EntityQuery
from ..lldxf.validator import entity_structure_validator
from ..options import options


def xtags_into_entitydb(section_tags, entitydb, dxffactory):
    linked_tags = get_tags_linker()
    post_read_tags_fixer = dxffactory.post_read_tags_fixer
    check_tag_structure = options.check_entity_tag_structures
    for tag_group in group_tags(section_tags):
        if check_tag_structure:
            tag_group = entity_structure_validator(tag_group)
        xtags = ExtendedTags(tag_group)
        post_read_tags_fixer(xtags)  # for VERTEX!
        handle = entitydb.add_tags(xtags)
        if not linked_tags(xtags, handle):  # also creates the link structure as side effect
            yield handle, xtags


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

        for handle, xtags in xtags_into_entitydb(tags[2:-1], self.entitydb, self.dxffactory):
            self._entity_space.store_tags(xtags)

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


