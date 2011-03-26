#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: DXF 12 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import DXFAttr
from ..entity import GenericWrapper

class AC1009GraphicBuilder:
    def add_line(self, start, end, attribs={}):
        def update_attribs():
            self._set_paper_space(attribs)
            attribs['start'] = start
            attribs['end'] = end

        update_attribs()
        entity = self._build_entity('LINE', attribs)
        self._add_entity(entity)
        return entity

    def _build_entity(self, type_, attribs):
        pass # abstract method

    def _add_entity(self, entity):
        pass # abstract method

    def _set_paper_space(self, attribs):
        pass # abstract method


_LINETEMPLATE = """  0
LINE
  5
0
  8
0
 10
0.0
 20
0.0
 30
0.0
 11
1.0
 21
1.0
 31
1.0
"""

class AC1009Line(GenericWrapper):
    TEMPLATE = _LINETEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'layer': DXFAttr(8, None, None), # layername as string, default is '0'
        'linetype': DXFAttr(6, None, None), # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
        'color': DXFAttr(62, None, None), # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
        'paperspace': DXFAttr(67, None, None), # 0 .. modelspace, 1 .. paperspace, default is 0
        'start': DXFAttr(10, None, 'Point2D/3D'),
        'end': DXFAttr(11, None, 'Point2D/3D'),
        'extrusion': DXFAttr(210, None, 'Point3D'), # never used !?
    }

    def set_extcolor(self, color):
        """ Set color by color-name or rgb-tuple, for DXF R12 the nearest
        default DXF color index will be determined.
        """
        pass

    def get_rgbcolor(self):
        return (0, 0, 0)

    def get_colorname(self):
        return 'Black'


