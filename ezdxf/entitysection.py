#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .tags import TagGroups
from .entityspace import EntitySpace

class EntitySection:
    name = 'entities'
    def __init__(self, tags, drawing):
        self._space = EntitySpace(self)
        self._drawing = drawing
        self._build(tags)

    @property
    def entitydb(self):
        return self._drawing.entitydb

    @property
    def handles(self):
        return self._drawing.handles


    def _build(self, tags):
        assert tags[0] == (0, 'SECTION')
        assert tags[1] == (2, 'ENTITIES')
        assert tags[-1] == (0, 'ENDSEC')

        groups = TagGroups(tags)
        for group in groups[1:-1]:
            self._space.add(group)

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\nENTITIES\n")
        db = self.entitydb
        for handle in self._space:
            entity = db[handle]
            entity.write(stream)
        stream.write("  0\nENDSEC\n")
