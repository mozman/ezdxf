# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from .graphics import GraphicEntity, ExtendedTags, make_attribs, DXFAttr
from ..lldxf.const import VERTEXNAMES


class QuadrilateralMixin(object):
    def __getitem__(self, num):
        return self.get_dxf_attrib(VERTEXNAMES[num])

    def __setitem__(self, num, value):
        return self.set_dxf_attrib(VERTEXNAMES[num], value)


_TRACE_TPL = """  0
TRACE
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


class Trace(GraphicEntity, QuadrilateralMixin):
    TEMPLATE = ExtendedTags.from_text(_TRACE_TPL)
    DXFATTRIBS = make_attribs({
        'vtx0': DXFAttr(10, xtype='Point2D/3D'),
        'vtx1': DXFAttr(11, xtype='Point2D/3D'),
        'vtx2': DXFAttr(12, xtype='Point2D/3D'),
        'vtx3': DXFAttr(13, xtype='Point2D/3D'),
    })


class Solid(Trace):
    TEMPLATE = ExtendedTags.from_text(_TRACE_TPL.replace('TRACE', 'SOLID'))


class Face(Trace):
    TEMPLATE = ExtendedTags.from_text(_TRACE_TPL.replace('TRACE', '3DFACE'))
    DXFATTRIBS = make_attribs({
        'vtx0': DXFAttr(10, xtype='Point3D'),
        'vtx1': DXFAttr(11, xtype='Point3D'),
        'vtx2': DXFAttr(12, xtype='Point3D'),
        'vtx3': DXFAttr(13, xtype='Point3D'),
        'invisible_edge': DXFAttr(70, default=0),
    })
