#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: DXF 12 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..entity import GenericWrapper

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
        'handle': 5,
        'layer': 8, # layername as string, default is '0'
        'linetype': 6, # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
        'color': 62, # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
        'paperspace': 67, # 0 .. modelspace, 1 .. paperspace, default is 0
        'start': (10, 'Point2D/3D'),
        'end': (11, 'Point2D/3D'),
        'extrusion': (210, 'Point3D'), # never used !?
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


