# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from itertools import islice

from .tags import TagGroups, DXFStructureError
from .classifiedtags import ClassifiedTags
from .entityspace import EntitySpace
from .query import EntityQuery


class EntitySection(object):
    name = 'entities'

    def __init__(self, tags, drawing):
        self._entityspace = EntitySpace(drawing.entitydb)
        self.drawing = drawing
        if tags is not None:
            self._build(tags)

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    def get_entityspace(self):
        return self._entityspace

    # start of public interface

    def __len__(self):
        return len(self._entityspace)

    def __iter__(self):
        dxffactory = self.dxffactory
        for handle in self._entityspace:
            entity = dxffactory.wrap_handle(handle)
            yield entity

    def __getitem__(self, index):
        if isinstance(index, int):
            raise ValueError('Integer index required')
        return self._entityspace[index]

    def query(self, query='*'):
        return EntityQuery(iter(self), query)

    # end of public interface

    def _build(self, tags):
        if tags[0] != (0, 'SECTION') or tags[1] != (2, self.name.upper()) or tags[-1] != (0, 'ENDSEC'):
            raise DXFStructureError("Critical structure error in {} section.".format(self.name.upper()))

        if len(tags) == 3:  # empty entities section
            return

        for group in TagGroups(islice(tags, 2, len(tags) - 1)):
            self._entityspace.store_tags(ClassifiedTags(group))
        self._entityspace.build_link_structure(self.dxffactory.wrap_handle)

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        self._entityspace.write(stream)
        stream.write("  0\nENDSEC\n")

    def delete_all_entities(self):
        """ Delete all entities. """
        db = self.drawing.entitydb
        for entity in list(self):  # delete modifies the base data structure of the iterator
            db.delete_entity(entity)
        del self._entityspace[:]  # clear entity space


class ClassesSection(EntitySection):
    name = 'classes'

    def __iter__(self):  # no layout setting required/possible
        for handle in self._entityspace:
            yield self.dxffactory.wrap_handle(handle)


class ObjectsSection(ClassesSection):
    name = 'objects'

    def roothandle(self):
        return self._entityspace[0]
