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
    def __init__(self, drawing):
        super(EntitySpace, self).__init__()
        self._drawing = drawing

    def add(self, entity):
        if isinstance(entity, Tags):
            handle = entity.gethandle(self._drawing.handles)
            self._drawing.entitydb[handle] = entity
        else:
            handle = entity.handle
        self.append(handle)

    def write(self, stream):
        db = self._drawing.entitydb
        for handle in self:
            db[handle].write(stream)



