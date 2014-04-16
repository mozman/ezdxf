# Purpose: AC1015 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

# Support for new AC1015 entities planned for the future:
# - MText
# - RText
# - Spline
# - ArcAlignedText
# - Hatch
# - Image
# - Viewport
# - Dimension
# - Tolerance
# - Leader
# - Wipeout ???
# - MLine ???
# - Shape ??? (not new but unnecessary ;-)
# 
# Unsupported DXF BLOBS: (existing entities will be preserved)
# - Body
# - Region
# - 3DSolid
#
# Unsupported AutoCAD/Windows entities: (existing entities will be preserved)
# - ACAD_PROXY_ENTITY
# - OLEFRAME
# - OLE2FRAME
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager
import math

from ..ac1009 import graphics as ac1009
from ..tags import DXFTag
from ..classifiedtags import ClassifiedTags
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass
from .. import const
from ..facemixins import PolyfaceMixin, PolymeshMixin
from ..tools import safe_3D_point

none_subclass = DefSubclass(None, {
    'handle': DXFAttr(5),
    'owner': DXFAttr(330),  # Soft-pointer ID/handle to owner BLOCK_RECORD object
})

entity_subclass = DefSubclass('AcDbEntity', {
    'paperspace': DXFAttr(67, default=0),  # 0 .. modelspace, 1 .. paperspace
    'layer': DXFAttr(8, default='0'),  # layername as string
    'linetype': DXFAttr(6, default='BYLAYER'),  # linetype as string, special names BYLAYER/BYBLOCK
    'ltscale': DXFAttr(48, default=1.0),  # linetype scale
    'invisible': DXFAttr(60, default=0),  # invisible .. 1, visible .. 0
    'color': DXFAttr(62, default=256),  # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER
})


class GraphicEntity(ac1009.GraphicEntity):
    """ Default graphic entity wrapper, allows access to following dxf attributes:
     - handle
     - owner handle
     - layer
     - linetype
     - color
     - paperspace
     - ltscale
     - invisible

     Wrapper for all unsupported graphic entities.
    """
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass)

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
    'start': DXFAttr(10, xtype='Point2D/3D'),
    'end': DXFAttr(11, xtype='Point2D/3D'),
    'thickness': DXFAttr(39, default=0),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Line(ac1009.Line):
    TEMPLATE = ClassifiedTags.from_text(_LINETEMPLATE)
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
    'location': DXFAttr(10, 'Point2D/3D'),
    'thickness': DXFAttr(39, None),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Point(ac1009.Point):
    TEMPLATE = ClassifiedTags.from_text(_POINT_TPL)
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
    'center': DXFAttr(10, xtype='Point2D/3D'),
    'radius': DXFAttr(40),
    'thickness': DXFAttr(39, default=0.0),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Circle(ac1009.Circle):
    TEMPLATE = ClassifiedTags.from_text(_CIRCLE_TPL)
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
        'center': DXFAttr(10, xtype='Point2D/3D'),
        'radius': DXFAttr(40),
        'thickness': DXFAttr(39, default=0.0),
    }),
    DefSubclass('AcDbArc', {
        'start_angle': DXFAttr(50),
        'end_angle': DXFAttr(51),
        'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    }),
)


class Arc(ac1009.Arc):
    TEMPLATE = ClassifiedTags.from_text(_ARC_TPL)
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
    'vtx0': DXFAttr(10, xtype='Point2D/3D'),
    'vtx1': DXFAttr(11, xtype='Point2D/3D'),
    'vtx2': DXFAttr(12, xtype='Point2D/3D'),
    'vtx3': DXFAttr(13, xtype='Point2D/3D'),
    'thickness': DXFAttr(39, default=0.0),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Trace(ac1009.Trace):
    TEMPLATE = ClassifiedTags.from_text(_TRACE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, trace_subclass)


class Solid(Trace):
    TEMPLATE = ClassifiedTags.from_text(_TRACE_TPL.replace('TRACE', 'SOLID'))

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


class Face(ac1009.Face):
    TEMPLATE = ClassifiedTags.from_text(_3DFACE_TPL)
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
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'rotation': DXFAttr(50, default=0.0),  # in degrees (circle = 360deg)
        'oblique': DXFAttr(51, default=0.0),  # in degrees, vertical = 0deg
        'style': DXFAttr(7, default='STANDARD'),  # text style
        'width': DXFAttr(41, default=1.0),  # width FACTOR!
        'text_generation_flag': DXFAttr(71, default=0),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, default=0),  # horizontal justification
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
        'thickness': DXFAttr(39, default=0.0),
        'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    }),
    DefSubclass('AcDbText', {'valign': DXFAttr(73, default=0)}))


class Text(ac1009.Text):
    TEMPLATE = ClassifiedTags.from_text(_TEXT_TPL)
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
    'elevation': DXFAttr(10, xtype='Point3D'),
    'flags': DXFAttr(70, default=0),
    'default_start_width': DXFAttr(40, default=0.0),
    'default_end_width': DXFAttr(41, default=0.0),
    'm_count': DXFAttr(71, default=0),
    'n_count': DXFAttr(72, default=0),
    'm_smooth_density': DXFAttr(73, default=0),
    'n_smooth_density': DXFAttr(74, default=0),
    'smooth_type': DXFAttr(75, default=0),
    'thickness': DXFAttr(39, default=0.0),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Polyline(ac1009.Polyline):
    TEMPLATE = ClassifiedTags.from_text(_POLYLINE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, polyline_subclass)

    def post_new_hook(self):
        super(Polyline, self).post_new_hook()
        self.update_subclass_specifier()

    def update_subclass_specifier(self):
        def set_subclass(subclassname):
            # For dxf attribute access not the name of the subclass is important, but
            # the order of the subcasses 1st, 2nd, 3rd and so on.
            # The 3rd subclass is the AcDb3dPolyline or AcDb2dPolyline subclass
            subclass = self.tags.subclasses[2]
            subclass[0] = DXFTag(100, subclassname)

        if self.get_mode() == 'polyline2d':
            set_subclass('AcDb2dPolyline')
        else:
            set_subclass('AcDb3dPolyline')

    def cast(self):
        mode = self.get_mode()
        if mode == 'polyface':
            return Polyface.convert(self)
        elif mode == 'polymesh':
            return Polymesh.convert(self)
        else:
            return self


class Polyface(Polyline, PolyfaceMixin):
    @staticmethod
    def convert(polyline):
        return Polyface(polyline.tags, polyline.drawing)


class Polymesh(Polyline, PolymeshMixin):
    @staticmethod
    def convert(polyline):
        return Polymesh(polyline.tags, polyline.drawing)

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
    DefSubclass('AcDbVertex', {}),  # subclasses[2]
    DefSubclass('AcDb2dVertex', {  # subclasses[3]
        'location': DXFAttr(10, xtype='Point2D/3D'),
        'start_width': DXFAttr(40, default=0.0),
        'end_width': DXFAttr(41, default=0.0),
        'bulge': DXFAttr(42, default=0),
        'flags': DXFAttr(70),
        'tangent': DXFAttr(50),
        'vtx0': DXFAttr(71),
        'vtx1': DXFAttr(72),
        'vtx2': DXFAttr(73),
        'vtx3': DXFAttr(74),
    })
)


class Vertex(ac1009.Vertex):
    VTX3D = const.VTX_3D_POLYFACE_MESH_VERTEX | const.VTX_3D_POLYGON_MESH_VERTEX | const.VTX_3D_POLYLINE_VERTEX
    TEMPLATE = ClassifiedTags.from_text(_VERTEX_TPL)
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
    TEMPLATE = ClassifiedTags.from_text("  0\nSEQEND\n  5\n0\n330\n 0\n100\nAcDbEntity\n")
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass)
    
_LWPOLYLINE_TPL = """  0
LWPOLYLINE
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbPolyline
 90
0
 70
0
"""

lwpolyline_subclass = DefSubclass('AcDbPolyline', {
    'elevation': DXFAttr(38, default=0.0),
    'thickness': DXFAttr(39, default=0.0),
    'flags': DXFAttr(70, default=0),
    'const_width': DXFAttr(43, default=0.0),
    'count': DXFAttr(90),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})

LWPOINTCODES = (10, 20, 40, 41, 42)


class LWPolyline(ac1009.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_LWPOLYLINE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, lwpolyline_subclass)

    @property
    def AcDbPolyline(self):
        return self.tags.subclasses[2]

    @property
    def closed(self):
        return bool(self.dxf.flags & const.LWPOLYLINE_CLOSED)

    @closed.setter
    def closed(self, status):
        flagsnow = self.dxf.flags
        if status:
            self.dxf.flags = flagsnow | const.LWPOLYLINE_CLOSED
        else:
            self.dxf.flags = flagsnow & (~const.LWPOLYLINE_CLOSED)

    def __len__(self):
        return self.dxf.count

    def __iter__(self):
        """ Yielding tuples of DXFTag.
        """
        point = []
        for tag in self.AcDbPolyline:
            if tag.code in LWPOINTCODES:
                if tag.code == 10:
                    if len(point):
                        yield tuple(point)
                        del point[:]
                point.append(tag)
        if len(point):
            yield tuple(point)

    def append_points(self, points):
        """ Append new *points* to polyline, *points* is a list of (x, y, [start_width, [end_width, [bulge]]])
        tuples.
        """
        tags = self.AcDbPolyline

        def append_point(point):
            def add_tag_if_not_zero(code, value):
                if value != 0.0:
                    tags.append(DXFTag(code, value))
            tags.append(DXFTag(10, point[0]))  # x value
            tags.append(DXFTag(20, point[1]))  # y value
            try:
                add_tag_if_not_zero(40, point[2])  # start width, default=0
                add_tag_if_not_zero(41, point[3])  # end width, default=0
                add_tag_if_not_zero(42, point[4])  # bulge, default=0
            except IndexError:
                pass
            
        for point in points:
            append_point(point)

        self._update_count()

    def _update_count(self):
        self.dxf.count = len(self.AcDbPolyline.find_all(10))

    def get_points(self):
        """  Returns all polyline points as list of tuples (x, y, [start_width, [end_width, [bulge]]]).
        """
        return (tuple(tag.value for tag in point) for point in self)

    def set_points(self, points):
        """ Remove all points and append new *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]])
        tuples.
        """
        self.discard_points()
        self.append_points(points)

    @contextmanager
    def points(self):
        points = list(self.get_points())
        yield points
        self.set_points(points)

    def discard_points(self):
        self.AcDbPolyline.remove_tags(codes=LWPOINTCODES)
        self.dxf.count = 0

    def __getitem__(self, index):
        """ Returns polyline point at *index* as (x, y, [start_width, [end_width, [bulge]]]) tuple.
        """
        if index < 0:
            index += self.dxf.count
        for x, point in enumerate(self.get_points()):
            if x == index:
                return point
        raise IndexError(index)

_BLOCK_TPL = """  0
BLOCK
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbBlockBegin
  2
BLOCKNAME
  3
BLOCKNAME
 70
0
 10
0.0
 20
0.0
 30
0.0
  1

"""
block_subclass = (
    DefSubclass('AcDbEntity', {'layer': DXFAttr(8, default='0')}),
    DefSubclass('AcDbBlockBegin', {
        'name': DXFAttr(2),
        'name2': DXFAttr(3),
        'description': DXFAttr(4),
        'flags': DXFAttr(70),
        'base_point': DXFAttr(10, xtype='Point2D/3D'),
        'xref_path': DXFAttr(1, default=""),
    })
)


class Block(ac1009.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_BLOCK_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, *block_subclass)

_ENDBLOCK_TPL = """  0
ENDBLK
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbBlockEnd
"""
endblock_subclass = (
    DefSubclass('AcDbEntity', {'layer': DXFAttr(8, default='0')}),
    DefSubclass('AcDbBlockEnd', {}),
)


class EndBlk(ac1009.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_ENDBLOCK_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, *endblock_subclass)

_INSERT_TPL = """  0
INSERT
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbBlockReference
  2
BLOCKNAME
 10
0.0
 20
0.0
 30
0.0
 41
1.0
 42
1.0
 43
1.0
 50
0.0
"""

insert_subclass = DefSubclass('AcDbBlockReference', {
    'attribs_follow': DXFAttr(66, default=0),
    'name': DXFAttr(2),
    'insert': DXFAttr(10, xtype='Point2D/3D'),
    'xscale': DXFAttr(41, default=1.0),
    'yscale': DXFAttr(42, default=1.0),
    'zscale': DXFAttr(43, default=1.0),
    'rotation': DXFAttr(50, default=0.0),
    'column_count': DXFAttr(70, default=1),
    'row_count': DXFAttr(71, default=1),
    'column_spacing': DXFAttr(44, default=0.0),
    'row_spacing': DXFAttr(45, default=0.0),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Insert(ac1009.Insert):
    TEMPLATE = ClassifiedTags.from_text(_INSERT_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, insert_subclass)
    
_ATTDEF_TPL = """  0
ATTDEF
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
DEFAULTTEXT
 50
0.0
 51
0.0
 41
1.0
  7
STANDARD
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
AcDbAttributeDefinition
  3
PROMPTTEXT
  2
TAG
 70
0
 73
0
 74
0
"""

attdef_subclass = (
    DefSubclass('AcDbText', {
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'thickness': DXFAttr(39, default=0.0),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'rotation': DXFAttr(50, default=0.0),
        'width': DXFAttr(41, default=1.0),
        'oblique': DXFAttr(51, default=0.0),
        'style': DXFAttr(7, default='STANDARD'),
        'text_generation_flag': DXFAttr(71, default=0),
        'halign': DXFAttr(72, default=0),
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
        'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    }),
    DefSubclass('AcDbAttributeDefinition', {
        'prompt': DXFAttr(3),
        'tag': DXFAttr(2),
        'flags': DXFAttr(70),
        'field_length': DXFAttr(73, default=0),
        'valign': DXFAttr(74, default=0),
    })
)


class Attdef(ac1009.Attdef):
    TEMPLATE = ClassifiedTags.from_text(_ATTDEF_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *attdef_subclass)
    
_ATTRIB_TPL = """  0
ATTRIB
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
DEFAULTTEXT
 50
0.0
 51
0.0
 41
1.0
  7
STANDARD
100
AcDbAttribute
  2
TAG
 70
0
 71
0
 72
0
 73
0
 74
0
 11
0.0
 21
0.0
 31
0.0
"""
attrib_subclass = (
    DefSubclass('AcDbText', {
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'thickness': DXFAttr(39, default=0.0),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'rotation': DXFAttr(50, default=0.0),  # error in DXF description, because placed in 'AcDbAttribute'
        'width': DXFAttr(41, default=1.0),  # error in DXF description, because placed in 'AcDbAttribute'
        'oblique': DXFAttr(51, default=0.0),  # error in DXF description, because placed in 'AcDbAttribute'
        'style': DXFAttr(7, default='STANDARD'),  # error in DXF description, because placed in 'AcDbAttribute'
        'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),  # error in DXF description, because placed in 'AcDbAttribute'
    }),
    DefSubclass('AcDbAttribute', {
        'tag': DXFAttr(2),
        'flags': DXFAttr(70),
        'field_length': DXFAttr(73, default=0),
        'text_generation_flag': DXFAttr(71, default=0),
        'halign': DXFAttr(72, default=0),
        'valign': DXFAttr(74, default=0),
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
    })
)


class Attrib(ac1009.Attrib):
    TEMPLATE = ClassifiedTags.from_text(_ATTRIB_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *attrib_subclass)
_ELLIPSE_TPL = """  0
ELLIPSE
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbEllipse
 10
0.0
 20
0.0
 30
0.0
 11
1.0
 21
0.0
 31
0.0
 40
1.0
 41
0.0
 42
6.283185307179586
"""

ellipse_subclass = DefSubclass('AcDbEllipse', {
    'center': DXFAttr(10, xtype='Point2D/3D'),
    'major_axis': DXFAttr(11, xtype='Point2D/3D'),  # relative to the center
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    'ratio': DXFAttr(40),
    'start_param': DXFAttr(41),  # this value is 0.0 for a full ellipse
    'end_param': DXFAttr(42),  # this value is 2*pi for a full ellipse
})


class Ellipse(ac1009.GraphicEntity, ac1009.ColorMixin):
    TEMPLATE = ClassifiedTags.from_text(_ELLIPSE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, ellipse_subclass)
_RAY_TPL = """ 0
RAY
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbRay
 10
0.0
 20
0.0
 30
0.0
 11
1.0
 21
0.0
 31
0.0
"""
ray_subclass = DefSubclass('AcDbRay', {
    'start': DXFAttr(10, xtype='Point3D'),
    'unit_vector': DXFAttr(11, xtype='Point3D'),
})


class Ray(ac1009.GraphicEntity, ac1009.ColorMixin):
    TEMPLATE = ClassifiedTags.from_text(_RAY_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, ray_subclass)


class XLine(Ray):
    TEMPLATE = ClassifiedTags.from_text(_RAY_TPL.replace('RAY', 'XLINE'))


_MTEXT_TPL = """ 0
MTEXT
 5
0
330
0
100
AcDbEntity
  8
0
100
AcDbMText
 50
0.0
 40
1.0
 41
1.0
 71
1
 72
5
 73
1
  1

"""

mtext_subclass = DefSubclass('AcDbMText', {
    'insert': DXFAttr(10, xtype='Point3D'),
    'char_height': DXFAttr(40),  # nominal (initial) text height
    'width': DXFAttr(41),  # reference column width
    'attachment_point': DXFAttr(71),
    # 1 = Top left; 2 = Top center; 3 = Top right
    # 4 = Middle left; 5 = Middle center; 6 = Middle right
    # 7 = Bottom left; 8 = Bottom center; 9 = Bottom right
    'flow_direction': DXFAttr(72),
    # 1 = Left to right
    # 3 = Top to bottom
    # 5 = By style (the flow direction is inherited from the associated text style)
    'style': DXFAttr(7, default='STANDARD'),  # text style name
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    'text_direction': DXFAttr(11, xtype='Point3D'),  # x-axis direction vector (in WCS)
    # If *rotation* and *text_direction* are present, *text_direction* wins
    'rect_width': DXFAttr(42),  # Horizontal width of the characters that make up the mtext entity.
    # This value will always be equal to or less than the value of *width*, (read-only, ignored if supplied)
    'rect_height': DXFAttr(43),  # vertical height of the mtext entity (read-only, ignored if supplied)
    'rotation': DXFAttr(50, default=0.0),  # in degrees (circle=360 deg) -  error in DXF reference, which says radians
    'line_spacing_style': DXFAttr(73),  # line spacing style (optional):
    # 1 = At least (taller characters will override)
    # 2 = Exact (taller characters will not override)
    'line_spacing_factor': DXFAttr(44),  # line spacing factor (optional):
    # Percentage of default (3-on-5) line spacing to be applied. Valid values
    # range from 0.25 to 4.00
})


class MText(ac1009.GraphicEntity):  # MTEXT will be extended in DXF version AC1021 (ACAD 2007)
    TEMPLATE = ClassifiedTags.from_text(_MTEXT_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, mtext_subclass)

    def get_text(self):
        tags = self.tags.get_subclass('AcDbMText')
        tail = ""
        parts = []
        for tag in tags:
            if tag.code == 1:
                tail = tag.value
            if tag.code == 3:
                parts.append(tag.value)
        parts.append(tail)
        return "".join(parts)

    def set_text(self, text):
        tags = self.tags.get_subclass('AcDbMText')
        tags.remove_tags(codes=(1, 3))
        str_chunks = split_string_in_chunks(text, size=250)
        if len(str_chunks) == 0:
            str_chunks.append("")
        while len(str_chunks) > 1:
            tags.append(DXFTag(3, str_chunks.pop(0)))
        tags.append(DXFTag(1, str_chunks[0]))
        return self

    def get_rotation(self):
        try:
            vector = self.dxf.text_direction
        except ValueError:
            rotation = self.get_dxf_attrib('rotation', 0.0)
        else:
            radians = math.atan2(vector[1], vector[0]) # ignores z-axis
            rotation = math.degrees(radians)
        return rotation

    def set_rotation(self, angle):
        del self.dxf.text_direction  # *text_direction* has higher priority than *rotation*, therefore delete it
        self.dxf.rotation = angle
        return self

    def set_location(self, insert, rotation=None, attachment_point=None):
        self.dxf.insert = safe_3D_point(insert)
        if rotation is not None:
            self.set_rotation(rotation)
        if attachment_point is not None:
            self.dxf.attachment_point = attachment_point
        return self

    @contextmanager
    def buffer(self):
        buffer = MTextBuffer(self.get_text())
        yield buffer
        self.set_text(buffer.text)

##################################################
# MTEXT inline codes
# \L	Start underline
# \l	Stop underline
# \O	Start overstrike
# \o	Stop overstrike
# \K	Start strike-through
# \k	Stop strike-through
# \P	New paragraph (new line)
# \pxi	Control codes for bullets, numbered paragraphs and columns
# \X	Paragraph wrap on the dimension line (only in dimensions)
# \Q	Slanting (obliquing) text by angle - e.g. \Q30;
# \H	Text height - e.g. \H3x;
# \W	Text width - e.g. \W0.8x;
# \F	Font selection
#
#     e.g. \Fgdt;o - GDT-tolerance
#     e.g. \Fkroeger|b0|i0|c238|p10 - font Kroeger, non-bold, non-italic, codepage 238, pitch 10
#
# \S	Stacking, fractions
#
#     e.g. \SA^B:
#     A
#     B
#     e.g. \SX/Y:
#     X
#     -
#     Y
#     e.g. \S1#4:
#     1/4
#
# \A	Alignment
#
#     \A0; = bottom
#     \A1; = center
#     \A2; = top
#
# \C	Color change
#
#     \C1; = red
#     \C2; = yellow
#     \C3; = green
#     \C4; = cyan
#     \C5; = blue
#     \C6; = magenta
#     \C7; = white
#
# \T	Tracking, char.spacing - e.g. \T2;
# \~	Non-wrapping space, hard space
# {}	Braces - define the text area influenced by the code
# \	Escape character - e.g. \\ = "\", \{ = "{"
#
# Codes and braces can be nested up to 8 levels deep


class MTextBuffer(object):
    UNDERLINE_START = '\\L;'
    UNDERLINE_STOP = '\\l;'
    UNDERLINE = UNDERLINE_START + '%s' + UNDERLINE_STOP
    OVERSTRIKE_START = '\\O;'
    OVERSTRIKE_STOP = '\\o;'
    OVERSTRIKE = OVERSTRIKE_START + '%s' + OVERSTRIKE_STOP
    STRIKE_START = '\\K;'
    STRIKE_STOP = '\\k;'
    STRIKE = STRIKE_START + '%s' + STRIKE_STOP
    NEW_LINE = '\\P;'
    GROUP_START = '{'
    GROUP_END = '}'
    GROUP = GROUP_START + '%s' + GROUP_END
    NBSP = '\\~' # none breaking space

    def __init__(self, text):
        self.text = text

    def __iadd__(self, text):
        self.text += text
        return self
    append = __iadd__

    def set_font(self, name, bold=False, italic=False, codepage=1252, pitch=0):
        bold_flag = 1 if bold else 0
        italic_flag = 1 if italic else 0
        s = "\\F{}|b{}|i{}|c{}|p{};".format(name, bold_flag, italic_flag, codepage, pitch)
        self.append(s)

    def set_color(self, color_name):
        self.append("\\C%d" % const.MTEXT_COLOR_INDEX[color_name.lower()])


def split_string_in_chunks(s, size=250):
    chunks = []
    pos = 0
    while True:
        chunk = s[pos:pos+size]
        chunk_len = len(chunk)
        if chunk_len:
            chunks.append(chunk)
            if chunk_len < size:
                return chunks
            pos += size
        else:
            return chunks

_SHAPE_TPL = """  0
SHAPE
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbShape
 10
0.0
 20
0.0
 30
0.0
 40
1.0
  2
NAME
 50
0.0
 41
1.0
 51
0.0
"""

shape_subclass = DefSubclass('AcDbShape', {
    'thickness': DXFAttr(39, default=0.0),
    'insert': DXFAttr(10, xtype='Point2D/3D'),
    'size': DXFAttr(40),
    'name': DXFAttr(2),
    'rotation': DXFAttr(50, default=0.0),
    'xscale': DXFAttr(41, default=1.0),
    'oblique': DXFAttr(51, default=0.0),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


# SHAPE is not tested with real world DXF drawings!
class Shape(ac1009.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_SHAPE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, shape_subclass)


_SPLINE_TPL = """  0
SPLINE
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbSpline
 70
0
 71
3
 72
0
 73
0
 74
0
"""
spline_subclass = DefSubclass('AcDbSpline', {
    'flags': DXFAttr(70, default=0),
    'degree': DXFAttr(71),
    'n_knots': DXFAttr(72),
    'n_control_points': DXFAttr(73),
    'n_fit_points': DXFAttr(74),
    'knot_tolerance': DXFAttr(42, default=1e-10),
    'control_point_tolerance': DXFAttr(43, default=1e-10),
    'fit_tolerance': DXFAttr(44, default=1e-10),
    'start_tangent': DXFAttr(12, xtype='Point3D'),
    'end_tangent': DXFAttr(13, xtype='Point3D'),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Spline(ac1009.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_SPLINE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, spline_subclass)

    @property
    def AcDbSpline(self):
        return self.tags.subclasses[2]

    @property
    def closed(self):
        return bool(self.dxf.flags & const.CLOSED_SPLINE)

    @closed.setter
    def closed(self, status):
        flagsnow = self.dxf.flags
        if status:
            self.dxf.flags = flagsnow | const.CLOSED_SPLINE
        else:
            self.dxf.flags = flagsnow & (~const.CLOSED_SPLINE)

    def get_knot_values(self):
        return [tag.value for tag in self.AcDbSpline.find_all(code=40)]

    def set_knot_values(self, knot_values):
        self._set_values(knot_values, code=40)
        self.dxf.n_knots = len(knot_values)

    def _set_values(self, values, code):
        tags = self.AcDbSpline
        tags.remove_tags(codes=(code, ))
        tags.extend([DXFTag(code, value) for value in values])

    @contextmanager
    def knot_values(self):
        values = self.get_knot_values()
        yield values
        self.set_knot_values(values)

    def get_weights(self):
        return [tag.value for tag in self.AcDbSpline.find_all(code=41)]

    def set_weights(self, values):
        self._set_values(values, code=41)

    @contextmanager
    def weights(self):
        values = self.get_weights()
        yield values
        self.set_weights(values)

    def get_control_points(self):
        tags = [tag for tag in self.AcDbSpline if tag.code in (10, 20, 30)]
        return self._get_points(tags, end_code=30)

    def _get_points(self, tags, end_code):
        point = []
        points = []
        for tag in tags:
            point.append(tag.value)
            if tag.code == end_code:
                points.append(tuple(point))
                del point[:]
        return points

    def set_control_points(self, points):
        self.AcDbSpline.remove_tags(codes=(10, 20, 30))
        count = self._append_points(points, code=10)
        self.dxf.n_control_points = count

    def _append_points(self, points, code):
        count = 0
        x_code = code
        y_code = code + 10
        z_code = code + 20
        ptags = []
        for point in points:
            count += 1
            x, y, z = point
            ptags.extend( (DXFTag(x_code, x), DXFTag(y_code, y), DXFTag(z_code, z)) )
        self.AcDbSpline.extend(ptags)
        return count

    @contextmanager
    def control_points(self):
        values = self.get_control_points()
        yield values
        self.set_control_points(values)

    def get_fit_points(self):
        tags = [tag for tag in self.AcDbSpline if tag.code in (11, 21, 31)]
        return self._get_points(tags, end_code=31)

    def set_fit_points(self, points):
        self.AcDbSpline.remove_tags(codes=(11, 21, 31))
        count = self._append_points(points, code=11)
        self.dxf.n_fit_points = count

    @contextmanager
    def fit_points(self):
        values = self.get_fit_points()
        yield values
        self.set_fit_points(values)
