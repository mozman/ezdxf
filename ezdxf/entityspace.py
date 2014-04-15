# Purpose: entity space
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


class EntitySpace(list):
    """An EntitySpace is a collection of drawing entities.
    The ENTITY section is such an entity space, but also blocks.
    The EntitySpace stores only handles to the drawing entity database.
    """
    def __init__(self, entitydb):
        self._entitydb = entitydb

    def get_tags_by_handle(self, handle):
        return self._entitydb[handle]

    def store_tags(self, tags):
        try:
            handle = tags.get_handle()
        except ValueError:  # no handle tag available
            # handle is not stored in tags!!!
            handle = self._entitydb.handles.next()
        self.append(handle)
        self._entitydb[handle] = tags

    def write(self, stream):
        for handle in self:
            self._entitydb[handle].write(stream)

    def delete_entity(self, entity):
        self.remove(entity.dxf.handle)