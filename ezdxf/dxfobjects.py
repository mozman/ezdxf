#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf objects wrapper, dxf-objects arn non-graphical entities
# all dxf objects resides in the OBJECTS SECTION
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .tags import TagGroups
from .dxfattr import DXFAttr, DXFAttributes, DefSubclass
from .entity import GenericWrapper

class DXFDictionary(GenericWrapper):
    DXFATTRIBS = DXFAttributes(
        DefSubclass(None, {
            'handle': DXFAttr(5, None),
            'parent': DXFAttr(330, None),
            }),
        DefSubclass('AcDbDictionary', {}),
    )

    def __init__(self, tags):
        super(DXFDictionary, self).__init__(tags)
        self._values = {}
        self._setup()

    def _setup(self):
        acdict = self.tags.get_subclass('AcDbDictionary')
        for group in TagGroups(acdict, splitcode=3):
            name = group[0].value
            handle = group[1].value
            self._values[name] = handle

    def keys(self):
        return self._values.keys()

    def items(self):
        return self._values.items()

    def __getitem__(self, key):
        return self._values[key]

    def get(self, key, default=None):
        return self._values.get(key, default)

class DXFLayout(GenericWrapper):
    DXFATTRIBS = DXFAttributes(
        DefSubclass(None, {
            'handle': DXFAttr(5, None),
            'parent': DXFAttr(330, None),
            }),
        DefSubclass('AcDbPlotSettings', {}),
        DefSubclass('AcDbLayout', {
            'name': DXFAttr(1, None), # layout name
            'flags': DXFAttr(70, None),
            'taborder': DXFAttr(71, None),
            'limmin': DXFAttr(10, 'Point2D'), # minimum limits
            'limmax': DXFAttr(11, 'Point2D'), # maximum limits
            'insertbase': DXFAttr(12, 'Point3D'), #Insertion base point for this layout
            'extmin': DXFAttr(14, 'Point3D'), # Minimum extents for this layout
            'extmax': DXFAttr(15, 'Point3D'), # Maximum extents for this layout
            'elevation': DXFAttr(146, None),
            'ucsorigin': DXFAttr(13, 'Point3D'),
            'ucsxaxis': DXFAttr(16, 'Point3D'),
            'ucsyaxis': DXFAttr(17, 'Point3D'),
            'ucstype': DXFAttr(76, None),
            # Orthographic type of UCS 0 = UCS is not orthographic;
            # 1 = Top; 2 = Bottom; 3 = Front; 4 = Back; 5 = Left; 6 = Right
            'block_record': DXFAttr(330, None),
            'viewport': DXFAttr(331, None),
            # ID/handle to the viewport that was last active in this
            # layout when the layout was current
            'ucs': DXFAttr(345, None),
            #ID/handle of AcDbUCSTableRecord if UCS is a named
            # UCS. If not present, then UCS is unnamed
            'baseucs': DXFAttr(345, None),
            #ID/handle of AcDbUCSTableRecord of base UCS if UCS is
            # orthographic (76 code is non-zero). If not present and
            # 76 code is non-zero, then base UCS is taken to be WORLD
        }))
