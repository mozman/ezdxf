# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

from ezdxf.legacy import trace

from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntityExtension


_TRACE_TPL = """0
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
    'vtx0': DXFAttr(10, xtype='Point2D/3D'),
    'vtx1': DXFAttr(11, xtype='Point2D/3D'),
    'vtx2': DXFAttr(12, xtype='Point2D/3D'),
    'vtx3': DXFAttr(13, xtype='Point2D/3D'),
    'thickness': DXFAttr(39, default=0.0),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Trace(trace.Trace, ModernGraphicEntityExtension):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_TRACE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, trace_subclass)


class Solid(Trace):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_TRACE_TPL.replace('TRACE', 'SOLID'))


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
    'vtx0': DXFAttr(10, xtype='Point3D'),
    'vtx1': DXFAttr(11, xtype='Point3D'),
    'vtx2': DXFAttr(12, xtype='Point3D'),
    'vtx3': DXFAttr(13, xtype='Point3D'),
    'invisible_edge': DXFAttr(70, default=0),
})


class Face(trace.Face, ModernGraphicEntityExtension):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_3DFACE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, face_subclass)
