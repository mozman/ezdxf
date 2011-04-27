#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1015 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import DXFAttr
from ..ac1009.graphics import GraphicEntity, ColorMixin, QuadrilateralMixin

def make_AC1015_attribs(additional={}):
    dxfattribs = {
        'handle': DXFAttr(5, None, None),
        'block_record': DXFAttr(330, None, None), # Soft-pointer ID/handle to owner BLOCK_RECORD object
        'paperspace': DXFAttr(67, 'AcDbEntity', None), # 0 .. modelspace, 1 .. paperspace, default is 0
        'layer': DXFAttr(8, 'AcDbEntity', None), # layername as string, default is '0'
        'linetype': DXFAttr(6, 'AcDbEntity', None), # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
        'ltscale': DXFAttr(48,'AcDbEntity', None), # linetype scale, default is 1.0
        'invisible': DXFAttr(60, 'AcDbEntity', None), # invisible .. 1, visible .. 0, default is 0
        'color': DXFAttr(62, 'AcDbEntity', None),# dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
    }
    dxfattribs.update(additional)
    return dxfattribs

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
        'thickness': DXFAttr(39, 'AcDbLine', None),
        'extrusion': DXFAttr(210, 'AcDbLine', 'Point3D'),
    })

_POINT_TPL = """  0
POINT
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbPoint
 10
0.0
 20
0.0
 30
0.0
"""

class AC1015Point(GraphicEntity, ColorMixin):
    TEMPLATE = _POINT_TPL
    DXFATTRIBS = make_AC1015_attribs({
        'point': DXFAttr(10, None, 'Point2D/3D'),
        'thickness': DXFAttr(39, 'AcDbPoint', None),
        'extrusion': DXFAttr(210, 'AcDbPoint', 'Point3D'),
    })

_CIRCLE_TPL = """  0
CIRCLE
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbCircle
 10
0.0
 20
0.0
 30
0.0
 40
1.0
"""

class AC1015Circle(GraphicEntity, ColorMixin):
    TEMPLATE = _CIRCLE_TPL
    DXFATTRIBS = make_AC1015_attribs({
        'center': DXFAttr(10, 'AcDbCircle', 'Point2D/3D'),
        'radius': DXFAttr(40, 'AcDbCircle', None),
        'thickness': DXFAttr(39, 'AcDbCircle', None),
        'extrusion': DXFAttr(210, 'AcDbCircle', 'Point3D'),
    })

_ARC_TPL = """  0
ARC
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbCircle
 10
0.0
 20
0.0
 30
0.0
 40
1.0
100
AcDbArc
 50
0
 51
360
"""

class AC1015Arc(GraphicEntity, ColorMixin):
    TEMPLATE = _ARC_TPL
    DXFATTRIBS = make_AC1015_attribs({
        'thickness': DXFAttr(39, 'AcDbCircle', None),
        'center': DXFAttr(10, 'AcDbCircle', 'Point2D/3D'),
        'radius': DXFAttr(40, 'AcDbCircle', None),
        'startangle': DXFAttr(50, 'AcDbArc', None),
        'endangle': DXFAttr(51, 'AcDbArc', None),
        'extrusion': DXFAttr(210, 'AcDbArc', 'Point3D'),
    })

_TRACE_TPL = """  0
TRACE
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbTrace
 10
0.0
 20
0.0
 30
0.0
 11
0.0
 21
0.0
 31
0.0
 12
0.0
 22
0.0
 32
0.0
 13
0.0
 23
0.0
 33
0.0
"""

class AC1015Trace(GraphicEntity, ColorMixin, QuadrilateralMixin):
    TEMPLATE = _TRACE_TPL
    DXFATTRIBS = make_AC1015_attribs({
        'vtx0' : DXFAttr(10, 'AcDbTrace', 'Point2D/3D'),
        'vtx1' : DXFAttr(11, 'AcDbTrace', 'Point2D/3D'),
        'vtx2' : DXFAttr(12, 'AcDbTrace', 'Point2D/3D'),
        'vtx3' : DXFAttr(13, 'AcDbTrace', 'Point2D/3D'),
        'thickness': DXFAttr(39, 'AcDbTrace', None),
        'extrusion': DXFAttr(210, 'AcDbTrace', 'Point3D'),
    })

class AC1015Solid(AC1015Trace):
    TEMPLATE = _TRACE_TPL.replace('TRACE', 'SOLID')

_3DFACE_TPL = """  0
3DFACE
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbFace
 10
0.0
 20
0.0
 30
0.0
 11
0.0
 21
0.0
 31
0.0
 12
0.0
 22
0.0
 32
0.0
 13
0.0
 23
0.0
 33
0.0
"""
class AC10153DFace(GraphicEntity, ColorMixin, QuadrilateralMixin):
    TEMPLATE = _3DFACE_TPL
    DXFATTRIBS = make_AC1015_attribs({
        'vtx0' : DXFAttr(10, 'AcDbFace', 'Point2D/3D'),
        'vtx1' : DXFAttr(11, 'AcDbFace', 'Point2D/3D'),
        'vtx2' : DXFAttr(12, 'AcDbFace', 'Point2D/3D'),
        'vtx3' : DXFAttr(13, 'AcDbFace', 'Point2D/3D'),
        'invisible_edge': DXFAttr(70, 'AcDbFace', None),
    })

_TEXT_TPL = """  0
TEXT
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbText
 10
0.0
 20
0.0
 30
0.0
 40
1.0
  1
TEXTCONTENT
 50
0.0
 51
0.0
  7
STANDARD
 41
1.0
 71
0
 72
0
 11
0.0
 21
0.0
 31
0.0
100
AcDbText
 73
0
"""

class AC1015Text(GraphicEntity, ColorMixin):
    TEMPLATE = _TEXT_TPL
    DXFATTRIBS = make_AC1015_attribs({
        'insert': DXFAttr(10, 'AcDbText', 'Point2D/3D'),
        'height': DXFAttr(40, 'AcDbText', None),
        'text': DXFAttr(1, 'AcDbText', None),
        'rotation': DXFAttr(50, 'AcDbText', None), # in degrees (circle = 360deg)
        'oblique': DXFAttr(51, 'AcDbText', None), # in degrees, vertical = 0deg
        'style': DXFAttr(7, 'AcDbText', None), # text style
        'width': DXFAttr(41, 'AcDbText', None), # width FACTOR!
        'textgenerationflag': DXFAttr(71, 'AcDbText', None), # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, 'AcDbText', None), # horizontal justification
        'valign': DXFAttr(73, 'AcDbText', None), # vertical justification
        'alignpoint': DXFAttr(11, 'AcDbText', 'Point2D/3D'),
        'thickness': DXFAttr(39, 'AcDbText', None),
        'extrusion': DXFAttr(210, 'AcDbText', 'Point3D'),
    })

    def _set_subclass_value(self, dxfattr, value):
        len_before = len(self.tags.subclass['AcDbText'])
        super(AC1015Text, self)._set_subclass_value(dxfattr, value)
        if len(self.tags.subclass['AcDbText']) != len_before:
            self._reorg_AcDbText_sublass(self.tags.subclass[subclassname])

    def _reorg_AcDbText_sublass(self, tags):
        def pop_special_tags():
            collection = list()
            if tag in tags[1:]:
                if tag.code in (100, 73):
                    collection += tag.pop(tag)
            return collection
        special_tags = pop_special_tags()
        tags.extend(special_tags)
