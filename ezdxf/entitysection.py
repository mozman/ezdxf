#!/usr/bin/env python
#coding:utf-8
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
from .dxfobjects import DXFDictionary


class EntitySection(object):
    name = 'entities'

    def __init__(self, tags, drawing):
        self._entityspace = EntitySpace(drawing.entitydb)
        self._dxffactory = drawing.dxffactory
        self._build(tags)

    def get_entityspace(self):
        return self._entityspace

    # start of public interface

    def __len__(self):
        return len(self._entityspace)

    def __iter__(self):
        for handle in self._entityspace:
            yield self._dxffactory.wrap_handle(handle)

    def __getitem__(self, index):
        if isinstance(index, int):
            raise ValueError('Integer index required')
        return self._entityspace[index]

    # end of public interface

    def _build(self, tags):
        assert tags[0] == (0, 'SECTION')
        assert tags[1] == (2, self.name.upper())
        assert tags[-1] == (0, 'ENDSEC')

        if len(tags) == 3:  # empty entities section
            return

        for group in TagGroups(islice(tags, 2, len(tags)-1)):
            self._entityspace.add(ClassifiedTags(group))

    def write(self, stream):
        stream.write("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        self._entityspace.write(stream)
        stream.write("  0\nENDSEC\n")


class ObjectsSection(EntitySection):
    name = 'objects'

    def roothandle(self):
        return self._entityspace[0]


class ClassesSection(EntitySection):
    name = 'classes'
