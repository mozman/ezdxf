#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1015 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import DXFAttr
from ..ac1009.graphics import GraphicEntity, ColorMixin

def make_AC1015_attribs(additional={}):
    attribs = {
        'handle': DXFAttr(5, None, None),
        'block_record': DXFAttr(330, None, None), # Soft-pointer ID/handle to owner BLOCK_RECORD object
        'paperspace': DXFAttr(67, 'AcDbEntity', None), # 0 .. modelspace, 1 .. paperspace, default is 0
        'layer': DXFAttr(8, 'AcDbEntity', None), # layername as string, default is '0'
        'linetype': DXFAttr(6, 'AcDbEntity', None), # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
        'ltscale': DXFAttr(48,'AcDbEntity', None), # linetype scale, default is 1.0
        'invisible': DXFAttr(60, 'AcDbEntity', None), # invisible .. 1, visible .. 0, default is 0
        'color': DXFAttr(62, 'AcDbEntity', None),# dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
    }
    attribs.update(additional)
    return attribs

_LINETEMPLATE = """  0
LINE
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbLine
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

class AC1015Line(GraphicEntity, ColorMixin):
    TEMPLATE = _LINETEMPLATE
    DXFATTRIBS = make_AC1015_attribs({
        'start': DXFAttr(10, 'AcDbLine', 'Point2D/3D'),
        'end': DXFAttr(11, 'AcDbLine', 'Point2D/3D'),
        'extrusion': DXFAttr(210, 'AcDbLine', 'Point3D'), # never used !?
    })
