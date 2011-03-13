#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: entity space
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .tags import Tags
from .entity import Entity

class EntitySpace(list):
    """
    An EntitySpace is a collection of drawing entities.
    The ENTITY section is such an entity-space, but also blocks, the
    modelspace and paperspaces (which are also blocks).
    The EntitySpace stores only handles to the entity-database.

    """
    def __init__(self, parent):
        super(EntitySpace, self).__init__()
        self._parent = parent

    def add(self, entity):
        if isinstance(entity, Tags):
            handle = entity.gethandle(self._parent.handles)
            self._parent.entitydb[handle] = entity
        elif isinstance(entity, Entity):
            handle = entity.handle
        self.append(handle)


