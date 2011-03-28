#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: entity space
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .tags import Tags

class EntitySpace(list):
    """
    An EntitySpace is a collection of drawing entities.
    The ENTITY section is such an entity-space, but also blocks, the
    modelspace and paperspaces (which are also blocks).
    The EntitySpace stores only handles to the entity-database.

    """
    def __init__(self, entitydb):
        self._entitydb = entitydb

    def add(self, entity):
        if isinstance(entity, Tags):
            try:
                handle = entity.gethandle()
            except ValueError:
                handle = self._entitydb.handles.next()
            self._entitydb[handle] = entity
        else:
            handle = entity.handle
        self.append(handle)

    def write(self, stream):
        for handle in self:
            self._entitydb[handle].write(stream)



