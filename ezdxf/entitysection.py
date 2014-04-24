# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from itertools import islice

from .tags import TagGroups, DXFStructureError
from .classifiedtags import ClassifiedTags, get_tags_linker
from .entityspace import EntitySpace, LayoutSpaces
from .query import EntityQuery


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

        linked_tags = get_tags_linker(self.dxffactory.wrap_entity)
        store_tags = self._entity_space.store_tags
        entitydb = self.entitydb
        fix_tags = self.dxffactory.fix_tags

        for group in TagGroups(islice(tags, 2, len(tags) - 1)):
            tags = ClassifiedTags(group)
            fix_tags(tags)  # post read tags fixer for VERTEX!
            if linked_tags(tags):  # also creates the link structure as side effect
                entitydb.add_tags(tags)  # add just to database
            else:
                store_tags(tags)  # add to entity space and database

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        self._entity_space.write(stream)
        stream.write("  0\nENDSEC\n")

    # start of public interface

    def __len__(self):
        return len(self._entity_space)

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
