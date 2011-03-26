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

class DXFLayout(GenericWrapper):
    CODE = {
        'handle': 5,
        'parent': 330,
        'name': 1, # layout name
        'flags': 70,
        'taborder': 71,
        'limmin': (10, 'Point2D'), # minimum limits
        'limmax': (11, 'Point2D'), # maximum limits
        'insertbase': (12, 'Point3D'), #Insertion base point for this layout
        'extmin': (14, 'Point3D'), # Minimum extents for this layout
        'extmax': (15, 'Point3D'), # Maximum extents for this layout
        'elevation': 146,
        'ucsorigin': (13, 'Point3D'),
        'ucsxaxis': (16, 'Point3D'),
        'ucsyaxis': (17, 'Point3D'),
        'ucstype': 76, # Orthographic type of UCS 0 = UCS is not orthographic;
                       # 1 = Top; 2 = Bottom; 3 = Front; 4 = Back; 5 = Left; 6 = Right
        'viewport': 331, # ID/handle to the viewport that was last active in this
                         # layout when the layout was current
        'ucs': 345, #ID/handle of AcDbUCSTableRecord if UCS is a named
                    # UCS. If not present, then UCS is unnamed
        'baseucs': 345, #ID/handle of AcDbUCSTableRecord of base UCS if UCS is
                        # orthographic (76 code is non-zero). If not present and
                        # 76 code is non-zero, then base UCS is taken to be WORLD
    }

    @property
    def block_record(self):
        # block_record has same group-code as parent(330)
        # ID/handle to this layout’s associated paper space block table record
        return self.tags.lastvalue(330)
    @block_record.setter
    def block_record(self, value):
        self.tags.setlast(330, value)

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
