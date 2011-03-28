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
        self.entityspace = EntitySpace(drawing)
        self._drawing = drawing
        self._build(tags)

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    # start of public interface

    def __len__(self):
        return len(self.entityspace)

    def __iter__(self):
        for handle in self.entityspace:
            yield self.dxffactory.wrap_handle(handle)

    def __getitem__(self, index):
        if isinstance(index, int):
            raise ValueError('Integer index required')
        return self.entityspace[index]

    # end of public interface

    def _build(self, tags):
        assert tags[0] == (0, 'SECTION')
        assert tags[1] == (2, self.name.upper())
        assert tags[-1] == (0, 'ENDSEC')

        if len(tags) == 3: # empty entities section
            return

        for group in TagGroups(islice(tags, 2, len(tags)-1)):
            self.entityspace.add(ExtendedTags(group))

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        self.entityspace.write(stream)
        stream.write("  0\nENDSEC\n")

class ObjectsSection(EntitySection):
    name = 'objects'
    def roothandle(self):
        return self.entityspace[0]

class ClassesSection(EntitySection):
    name = 'classes'
