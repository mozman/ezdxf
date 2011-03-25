#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1015 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..ac1009.graphics import AC1009Line

_LINETEMPLATE = """  0
LINE
  5
0
330
0
100
AcDbEntity
100
AcDbLine
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

class AC1015Line(AC1009Line):
    TEMPLATE = _LINETEMPLATE
    CODE = {
        'handle': 5,
        'owner': 330, # Soft-pointer ID/handle to owner BLOCK_RECORD object
        'layer': 8, # layername as string, default is '0'
        'linetype': 6, # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
        'ltscale': 48, # linetype scale, default is 1.0
        'invisible': 60, # invisible .. 1, visible .. 0, default is 0
        'color': 62, # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
        'paperspace': 67, # 0 .. modelspace, 1 .. paperspace, default is 0
        'start': (10, 'Point2D/3D'),
        'end': (11, 'Point2D/3D'),
        'extrusion': (210, 'Point3D'), # never used !?
    }
