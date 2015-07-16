# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from itertools import islice

from ..lldxf.tags import TagGroups, DXFStructureError
from ..lldxf.classifiedtags import ClassifiedTags, get_tags_linker
from ..entityspace import EntitySpace, LayoutSpaces
from ..query import EntityQuery


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
        fix_tags = self.dxffactory.modify_tags

        for group in TagGroups(islice(tags, 2, len(tags)-1)):
            tags = ClassifiedTags(group)
            fix_tags(tags)  # post read tags fixer for VERTEX!
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

    def remove_handle(self, handle):
        self._entity_space.remove(handle)

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


class ClassesSection(AbstractSection):
    name = 'classes'

    def __init__(self, tags, drawing):
        entity_space = EntitySpace(drawing.entitydb)
        super(ClassesSection, self).__init__(entity_space, tags, drawing)

    def __iter__(self):  # no layout setting required/possible
        for handle in self._entity_space:
            yield self.dxffactory.wrap_handle(handle)


class ObjectsSection(ClassesSection):
    name = 'objects'

    def roothandle(self):
        return self._entity_space[0]


class EntitySection(AbstractSection):
    name = 'entities'

    def __init__(self, tags, drawing):
        layout_spaces = LayoutSpaces(drawing.entitydb, drawing.dxfversion)
        super(EntitySection, self).__init__(layout_spaces, tags, drawing)

    def get_layout_space(self, key):
        return self._entity_space.get_entity_space(key)

    # start of public interface

    def __iter__(self):
        dxffactory = self.dxffactory
        for handle in self._entity_space.handles():
            entity = dxffactory.wrap_handle(handle)
            yield entity

    # end of public interface

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        modelspace = self.drawing.modelspace()
        self._entity_space.write(stream, first_key=modelspace.layout_key)
        stream.write("  0\nENDSEC\n")

    def repair_model_space(self, model_space_layout_key):
        self._entity_space.repair_model_space(model_space_layout_key)