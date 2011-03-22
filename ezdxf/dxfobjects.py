#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf objects wrapper, dxf-objects arn non-graphical entities
# all dxf objects resides in the OBJECTS SECTION
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .tags import TagGroups
from .entity import GenericWrapper

class DXFDictionary(GenericWrapper):
    CODE = {
        'handle': 5,
        'parent': 330,
    }

    def __init__(self, tags):
        super(DXFDictionary, self).__init__(tags)
        self._values = {}
        self._setup()

    def _setup(self):
        for group in TagGroups(self.tags, splitcode=3):
            name = group[0].value
            handle = group[1].value
            self._values[name] = handle

    def __getitem__(self, key):
        return self._values[key]

    def get(self, key, default=None):
        return self._values.get(key, default)
