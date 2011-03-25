#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from itertools import islice

from .tags import TagGroups, DXFStructureError, ExtendedTags
from .entityspace import EntitySpace
from .dxfobjects import DXFDictionary

class EntitySection:
    name = 'entities'
    def __init__(self, tags, drawing):
        self._workspace = EntitySpace(drawing)
        self._build(tags)

    def iterhandles(self):
        return iter(self._workspace)

    def _build(self, tags):
        assert tags[0] == (0, 'SECTION')
        assert tags[1] == (2, self.name.upper())
        assert tags[-1] == (0, 'ENDSEC')

        if len(tags) == 3: # empty entities section
            return

        for group in TagGroups(islice(tags, 2, len(tags)-1)):
            self._workspace.add(ExtendedTags(group))

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        self._workspace.write(stream)
        stream.write("  0\nENDSEC\n")

class ObjectsSection(EntitySection):
    name = 'objects'
    def roothandle(self):
        return self._workspace[0]

class ClassesSection(EntitySection):
    name = 'classes'
