#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1015 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import DXFAttr
from ..ac1009.graphics import ColorMixin, QuadrilateralMixin
from ..entity import GenericSubclassWrapper

from ..dxfattr import DXFAttributes, SubclassDef

class GraphicEntity(GenericSubclassWrapper):
    def set_builder(self, builder):
        self._builder = builder # IGraphicBuilder

none_subclass = SubclassDef(None, {
        'handle': DXFAttr(5, None),
        'block_record': DXFAttr(330, None), # Soft-pointer ID/handle to owner BLOCK_RECORD object
})
        
entity_subclass = SubclassDef('AcDbEntity', {
    'paperspace': DXFAttr(67, None), # 0 .. modelspace, 1 .. paperspace, default is 0
    'layer': DXFAttr(8, None), # layername as string, default is '0'
    'linetype': DXFAttr(6, None), # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
    'ltscale': DXFAttr(48, None), # linetype scale, default is 1.0
    'invisible': DXFAttr(60, None), # invisible .. 1, visible .. 0, default is 0
    'color': DXFAttr(62, None),# dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
})

def make_AC1015_attribs(additional={}):
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

line_subclass = SubclassDef('AcDbLine', {
        'start': DXFAttr(10, 'Point2D/3D'),
        'end': DXFAttr(11, 'Point2D/3D'),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
})

class AC1015Line(GraphicEntity, ColorMixin):
    TEMPLATE = _LINETEMPLATE
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, line_subclass)

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
point_subclass = SubclassDef('AcDbPoint', {
        'point': DXFAttr(10, 'Point2D/3D'),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
})

class AC1015Point(GraphicEntity, ColorMixin):
    TEMPLATE = _POINT_TPL
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, point_subclass)

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
circle_subclass = SubclassDef('AcDbCircle', {
        'center': DXFAttr(10, 'Point2D/3D'),
        'radius': DXFAttr(40, None),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
})
class AC1015Circle(GraphicEntity, ColorMixin):
    TEMPLATE = _CIRCLE_TPL
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, circle_subclass)

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

arc_subclass = (
    SubclassDef('AcDbCircle', {
        'center': DXFAttr(10, 'Point2D/3D'),
        'radius': DXFAttr(40, None),
        'thickness': DXFAttr(39, None),
        }),
    SubclassDef('AcDbArc', {
        'startangle': DXFAttr(50, None),
        'endangle': DXFAttr(51, None),
        'extrusion': DXFAttr(210, 'Point3D'),
        }),
    )

class AC1015Arc(GraphicEntity, ColorMixin):
    TEMPLATE = _ARC_TPL
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *arc_subclass)

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
trace_subclass = SubclassDef('AcDbTrace', {
        'vtx0' : DXFAttr(10,'Point2D/3D'),
        'vtx1' : DXFAttr(11, 'Point2D/3D'),
        'vtx2' : DXFAttr(12, 'Point2D/3D'),
        'vtx3' : DXFAttr(13, 'Point2D/3D'),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
    })
class AC1015Trace(GraphicEntity, ColorMixin, QuadrilateralMixin):
    TEMPLATE = _TRACE_TPL
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, trace_subclass)

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
face_subclass = SubclassDef('AcDbFace', {
        'vtx0' : DXFAttr(10,'Point2D/3D'),
        'vtx1' : DXFAttr(11, 'Point2D/3D'),
        'vtx2' : DXFAttr(12, 'Point2D/3D'),
        'vtx3' : DXFAttr(13, 'Point2D/3D'),
        'invisible_edge': DXFAttr(70, None),
    })

class AC10153DFace(GraphicEntity, ColorMixin, QuadrilateralMixin):
    TEMPLATE = _3DFACE_TPL
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, face_subclass)

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
text_subclass = (
    SubclassDef('AcDbText', {
        'insert': DXFAttr(10, 'Point2D/3D'),
        'height': DXFAttr(40, None),
        'text': DXFAttr(1, None),
        'rotation': DXFAttr(50, None), # in degrees (circle = 360deg)
        'oblique': DXFAttr(51, None), # in degrees, vertical = 0deg
        'style': DXFAttr(7, None), # text style
        'width': DXFAttr(41, None), # width FACTOR!
        'textgenerationflag': DXFAttr(71, None), # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, None), # horizontal justification
        'alignpoint': DXFAttr(11, 'Point2D/3D'),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
        }), # Hey Autodesk, what are you doing???
    SubclassDef('AcDbText', {
        'valign': DXFAttr(73, None), # vertical justification
        }),
)

class AC1015Text(GraphicEntity, ColorMixin):
    TEMPLATE = _TEXT_TPL
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *test_subclass)
