# Purpose: entity space
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


class EntitySpace(list):
    """
    An EntitySpace is a collection of drawing entities.
    The ENTITY section is such an entity space, but also blocks.
    The EntitySpace stores only handles to the drawing entity database.
    """
    def __init__(self, entitydb):
        self._entitydb = entitydb

    def add(self, entity):
        if hasattr(entity, 'get_handle'):
            try:
                handle = entity.get_handle()
            except ValueError:
                handle = self._entitydb.handles.next()
            self._entitydb[handle] = entity
        else:
            handle = entity.dxf.handle
        self.append(handle)

    def write(self, stream):
        for handle in self:
            self._entitydb[handle].write(stream)
