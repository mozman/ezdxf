#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1015 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..ac1009 import graphics as ac1009
from ..tags import DXFTag
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass
from .. import const
from ..facemixins import PolyfaceMixin, PolymeshMixin

none_subclass = DefSubclass(None, {
        'handle': DXFAttr(5, None),
        'block_record': DXFAttr(330, None), # Soft-pointer ID/handle to owner BLOCK_RECORD object
})

entity_subclass = DefSubclass('AcDbEntity', {
    'paperspace': DXFAttr(67, None), # 0 .. modelspace, 1 .. paperspace, default is 0
    'layer': DXFAttr(8, None), # layername as string, default is '0'
    'linetype': DXFAttr(6, None), # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
    'ltscale': DXFAttr(48, None), # linetype scale, default is 1.0
    'invisible': DXFAttr(60, None), # invisible .. 1, visible .. 0, default is 0
    'color': DXFAttr(62, None),# dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
})

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

line_subclass = DefSubclass('AcDbLine', {
        'start': DXFAttr(10, 'Point2D/3D'),
        'end': DXFAttr(11, 'Point2D/3D'),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
})

class Line(ac1009.Line):
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
point_subclass = DefSubclass('AcDbPoint', {
        'point': DXFAttr(10, 'Point2D/3D'),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
})

class Point(ac1009.Point):
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
circle_subclass = DefSubclass('AcDbCircle', {
        'center': DXFAttr(10, 'Point2D/3D'),
        'radius': DXFAttr(40, None),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
})
class Circle(ac1009.Circle):
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
    DefSubclass('AcDbCircle', {
        'center': DXFAttr(10, 'Point2D/3D'),
        'radius': DXFAttr(40, None),
        'thickness': DXFAttr(39, None),
        }),
    DefSubclass('AcDbArc', {
        'startangle': DXFAttr(50, None),
        'endangle': DXFAttr(51, None),
        'extrusion': DXFAttr(210, 'Point3D'),
        }),
    )

class Arc(ac1009.Arc):
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
trace_subclass = DefSubclass('AcDbTrace', {
        'vtx0' : DXFAttr(10,'Point2D/3D'),
        'vtx1' : DXFAttr(11, 'Point2D/3D'),
        'vtx2' : DXFAttr(12, 'Point2D/3D'),
        'vtx3' : DXFAttr(13, 'Point2D/3D'),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
    })
class Trace(ac1009.Trace):
    TEMPLATE = _TRACE_TPL
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, trace_subclass)

class Solid(Trace):
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
face_subclass = DefSubclass('AcDbFace', {
        'vtx0' : DXFAttr(10,'Point2D/3D'),
        'vtx1' : DXFAttr(11, 'Point2D/3D'),
        'vtx2' : DXFAttr(12, 'Point2D/3D'),
        'vtx3' : DXFAttr(13, 'Point2D/3D'),
        'invisible_edge': DXFAttr(70, None),
    })

class Face(ac1009.Face):
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
    DefSubclass('AcDbText', {
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
    DefSubclass('AcDbText', {
        'valign': DXFAttr(73, None), # vertical justification
        }),
)

class Text(ac1009.Text):
    TEMPLATE = _TEXT_TPL
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *text_subclass)

_POLYLINE_TPL = """  0
POLYLINE
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDb2dPolyline
 66
1
 70
0
 10
0.0
 20
0.0
 30
0.0
"""

polyline_subclass = DefSubclass('AcDb2dPolyline', {
        'elevation': DXFAttr(10, 'Point2D/3D'),
        'flags': DXFAttr(70, None),
        'defaultstartwidth': DXFAttr(40, None),
        'defaultendwidth': DXFAttr(41, None),
        'mcount': DXFAttr(71, None),
        'ncount': DXFAttr(72, None),
        'msmoothdensity': DXFAttr(73, None),
        'nsmoothdensity': DXFAttr(74, None),
        'smoothtype': DXFAttr(75, None),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
})

class Polyline(ac1009.Polyline):
    TEMPLATE = _POLYLINE_TPL
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, polyline_subclass)

    def post_new_hook(self):
        self.update_subclass_specifier()

    def update_subclass_specifier(self):
        def set_subclass(subclassname):
            # For dxf attribute access not the name of the subclass is important, but
            # the order of the subcasses 1st, 2nd, 3rd and so on.
            # The 3rd subclass is the AcDb3dPolyline or AcDb2dPolyline subclass
            subclass = self.tags.subclasses[2]
            subclass[0] = DXFTag(100, subclassname)

        if self.getmode() == 'polyline2d':
            set_subclass('AcDb2dPolyline')
        else:
            set_subclass('AcDb3dPolyline')

    def cast(self):
        mode = self.getmode()
        if mode == 'polyface':
            return Polyface.convert(self)
        elif mode == 'polymesh':
            return Polymesh.convert(self)
        else:
            return self

class Polyface(Polyline, PolyfaceMixin):
    @staticmethod
    def convert(polyline):
        face = Polyface(polyline.tags)
        face.set_builder(polyline._builder)
        return face

class Polymesh(Polyline, PolymeshMixin):
    @staticmethod
    def convert(polyline):
        mesh = Polymesh(polyline.tags)
        mesh.set_builder(polyline._builder)
        return mesh

_VERTEX_TPL = """ 0
VERTEX
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbVertex
100
AcDb2dVertex
 10
0.0
 20
0.0
 30
0.0
 40
0.0
 41
0.0
 42
0.0
 70
0
"""
vertex_subclass = (
    DefSubclass('AcDbVertex', {}), # subclasses[2]
    DefSubclass('AcDb2dVertex', { # subclasses[3]
        'location': DXFAttr(10, 'Point2D/3D'),
        'startwidth': DXFAttr(40, None),
        'endwidth': DXFAttr(41, None),
        'bulge': DXFAttr(42, None),
        'flags': DXFAttr(70, None),
        'tangent': DXFAttr(50, None),
        'vtx0': DXFAttr(71, None),
        'vtx1': DXFAttr(72, None),
        'vtx2': DXFAttr(73, None),
        'vtx3': DXFAttr(74, None),
    })
)



class Vertex(ac1009.Vertex):
    VTX3D = const.VTX_3D_POLYFACE_MESH_VERTEX | const.VTX_3D_POLYGON_MESH_VERTEX | const.VTX_3D_POLYLINE_VERTEX
    TEMPLATE = _VERTEX_TPL
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *vertex_subclass)

    def post_new_hook(self):
        self.update_subclass_specifier()

    def update_subclass_specifier(self):
        def set_subclass(subclassname):
            subclass = self.tags.subclasses[3]
            subclass[0] = DXFTag(100, subclassname)

        if self.dxf.flags & Vertex.VTX3D != 0:
            set_subclass('AcDb3dPolylineVertex')
        else:
            set_subclass('AcDb2dVertex')

class SeqEnd(ac1009.SeqEnd):
    TEMPLATE = "  0\nSEQEND\n  5\n0\n330\n 0\n100\nAcDbEntity\n"
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass)
