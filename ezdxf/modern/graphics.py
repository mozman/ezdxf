# Purpose: AC1015 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

# Support for new AC1015 entities planned for the future:
# - RText
# - ArcAlignedText
# - Hatch
# - Image
# - Viewport
# - Dimension
# - Tolerance
# - Leader
# - Wipeout ???
# - MLine ???
# - Body
# - Region
# - 3DSolid
# - Surface
# - Mesh
#
# Unsupported AutoCAD/Windows entities: (existing entities will be preserved)
# - ACAD_PROXY_ENTITY (compressed data)
# - OLEFRAME (compressed data)
# - OLE2FRAME (compressed data)
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager
import math

from ..legacy import graphics as legacy
from ..tags import DXFTag, Tags, CompressedTags
from ..dxftag import convert_tags_to_text_lines, convert_text_lines_to_tags
from ..classifiedtags import ClassifiedTags
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass
from .. import const
from ..facemixins import PolyfaceMixin, PolymeshMixin
from ..tools import safe_3D_point
from .. import crypt
from ..const import DXFStructureError


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


class GraphicEntity(legacy.GraphicEntity):
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


class Line(legacy.Line):
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


class Point(legacy.Point):
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


class Circle(legacy.Circle):
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

arc_subclass = DefSubclass('AcDbArc', {
    'start_angle': DXFAttr(50),
    'end_angle': DXFAttr(51),
})


class Arc(legacy.Arc):
    TEMPLATE = ClassifiedTags.from_text(_ARC_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, circle_subclass, arc_subclass)

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


class Trace(legacy.Trace):
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


class Face(legacy.Face):
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


class Text(legacy.Text):
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


class Polyline(legacy.Polyline):
    TEMPLATE = ClassifiedTags.from_text(_POLYLINE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, polyline_subclass)

    def post_new_hook(self):
        super(Polyline, self).post_new_hook()
        self.update_subclass_specifier()

    def update_subclass_specifier(self):
        # For dxf attribute access not the name of the subclass is important, but
        # the order of the subclasses 1st, 2nd, 3rd and so on.
        # The 3rd subclass is the AcDb3dPolyline or AcDb2dPolyline subclass
        subclass = self.tags.subclasses[2]
        subclass[0] = DXFTag(100, self.get_mode())

    def cast(self):
        mode = self.get_mode()
        if mode == 'AcDbPolyFaceMesh':
            return Polyface.convert(self)
        elif mode == 'AcDbPolygonMesh':
            return Polymesh.convert(self)
        else:
            return self


class Polyface(Polyline, PolyfaceMixin):
    """ PolyFace structure:
    POLYLINE
      AcDbEntity
      AcDbPolyFaceMesh
    VERTEX - Vertex
      AcDbEntity
      AcDbVertex
      AcDbPolyFaceMeshVertex
    VERTEX - Face
      AcDbEntity
      AcDbFaceRecord
    SEQEND
    """
    @staticmethod
    def convert(polyline):
        return Polyface(polyline.tags, polyline.drawing)


class Polymesh(Polyline, PolymeshMixin):
    """ PolyMesh structure:
    POLYLINE
      AcDbEntity
      AcDbPolygonMesh
    VERTEX
      AcDbEntity
      AcDbVertex
      AcDbPolygonMeshVertex
    """
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


EMPTY_VERTEX_SUBCLASS = Tags()


class Vertex(legacy.Vertex):
    TEMPLATE = ClassifiedTags.from_text(_VERTEX_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *vertex_subclass)

    def post_new_hook(self):
        self.update_subclass_specifier()

    def update_subclass_specifier(self):
        def set_subclass(subclassname):
            subclass = self.tags.subclasses[3]
            subclass[0] = DXFTag(100, subclassname)

        if self.is_3d_polyline_vertex:  # flags & const.VTX_3D_POLYLINE_VERTEX
            set_subclass('AcDb3dPolylineVertex')
        elif self.is_face_record:  # (flags & Vertex.FACE_FLAGS) == const.VTX_3D_POLYFACE_MESH_VERTEX:
            set_subclass('AcDbFaceRecord')
            self.tags.subclasses[2] = EMPTY_VERTEX_SUBCLASS  # clear subclass AcDbVertex
        elif self.is_poly_face_mesh_vertex:  # flags & Vertex.FACE_FLAGS == Vertex.FACE_FLAGS:
            set_subclass('AcDbPolyFaceMeshVertex')
        elif self.is_polygon_mesh_vertex:  # flags & const.VTX_3D_POLYGON_MESH_VERTEX:
            set_subclass('AcDbPolygonMeshVertex')
        else:
            set_subclass('AcDb2dVertex')

    @staticmethod
    def fix_tags(tags):
        """ If subclass[2] is not 'AcDbVertex', insert empty subclass
        """
        if tags.subclasses[2][0].value != 'AcDbVertex':
            tags.subclasses.insert(2, EMPTY_VERTEX_SUBCLASS)


class SeqEnd(legacy.SeqEnd):
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


class LWPolyline(legacy.GraphicEntity):
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
        """ Yielding tuples of (x, y, start_width, end_width, bulge), start_width, end_width and bulge is 0 if not
        present.
        """
        def get_vertex():
            point.append(attribs.get(40, 0))
            point.append(attribs.get(41, 0))
            point.append(attribs.get(42, 0))
            return tuple(point)

        point = None
        attribs = {}
        for tag in self.AcDbPolyline:
            if tag.code in LWPOINTCODES:
                if tag.code == 10:
                    if point is not None:
                        yield get_vertex()
                    point = list(tag.value)
                    attribs = {}
                else:
                    attribs[tag.code] = tag.value
        if point is not None:
            yield get_vertex()  # last point

    def get_rstrip_points(self):
        last0 = 4
        for point in self:
            while point[last0] == 0 and last0 > 1:
                last0 -= 1
            yield tuple(point[:last0+1])

    def append_points(self, points):
        """ Append new *points* to polyline, *points* is a list of (x, y, [start_width, [end_width, [bulge]]])
        tuples. Set start_width, end_width to 0 to ignore (x, y, 0, 0, bulge).
        """
        tags = self.AcDbPolyline

        def append_point(point):

            def add_tag_if_not_zero(code, value):
                if value != 0.0:
                    tags.append(DXFTag(code, value))
            tags.append(DXFTag(10, (point[0], point[1])))  # x, y values
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

    get_points = __iter__

    def set_points(self, points):
        """ Remove all points and append new *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]])
        tuples. Set start_width, end_width to 0 to ignore (x, y, 0, 0, bulge).
        """
        self.discard_points()
        self.append_points(points)

    @contextmanager
    def points(self):
        points = list(self)
        yield points
        self.set_points(points)

    @contextmanager
    def rstrip_points(self):
        points = list(self.get_rstrip_points())
        yield points
        self.set_points(points)

    def discard_points(self):
        self.AcDbPolyline.remove_tags(codes=LWPOINTCODES)
        self.dxf.count = 0

    def __getitem__(self, index):
        """ Returns polyline point at *index* as (x, y, start_width, end_width, bulge) tuple, start_width, end_width and
        bulge is 0 if not present.
        """
        if index < 0:
            index += self.dxf.count
        for x, point in enumerate(self):
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


class Block(legacy.GraphicEntity):
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


class EndBlk(legacy.GraphicEntity):
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


class Insert(legacy.Insert):
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


class Attdef(legacy.Attdef):
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


class Attrib(legacy.Attrib):
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


class Ellipse(legacy.GraphicEntity, legacy.ColorMixin):
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


class Ray(legacy.GraphicEntity, legacy.ColorMixin):
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


class MText(legacy.GraphicEntity):  # MTEXT will be extended in DXF version AC1021 (ACAD 2007)
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
    def edit_data(self):
        buffer = MTextData(self.get_text())
        yield buffer
        self.set_text(buffer.text)

    buffer = edit_data  # alias

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


class MTextData(object):
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
    NBSP = '\\~'  # none breaking space

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
class Shape(legacy.GraphicEntity):
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


class Spline(legacy.GraphicEntity):
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
        raise RuntimeError("Spline.knot_values() is deprecated, use Spline.edit_data()")

    def get_weights(self):
        return [tag.value for tag in self.AcDbSpline.find_all(code=41)]

    def set_weights(self, values):
        self._set_values(values, code=41)

    @contextmanager
    def weights(self):
        raise RuntimeError("Spline.weights() is deprecated, use Spline.edit_data()")

    def get_control_points(self):
        return [tag.value for tag in self.AcDbSpline if tag.code == 10]

    def set_control_points(self, points):
        self.AcDbSpline.remove_tags(codes=(10, ))
        count = self._append_points(points, code=10)
        self.dxf.n_control_points = count

    def _append_points(self, points, code):
        tags = []
        for point in points:
            if len(point) != 3:
                raise ValueError("require 3D points")
            tags.append(DXFTag(code, point))
        self.AcDbSpline.extend(tags)
        return len(tags)

    @contextmanager
    def control_points(self):
        raise RuntimeError("Spline.control_points() is deprecated, use Spline.edit_data()")

    def get_fit_points(self):
        return [tag.value for tag in self.AcDbSpline if tag.code == 11]

    def set_fit_points(self, points):
        self.AcDbSpline.remove_tags(codes=(11, ))
        count = self._append_points(points, code=11)
        self.dxf.n_fit_points = count

    @contextmanager
    def fit_points(self):
        raise RuntimeError("Spline.fit_points() is deprecated, use Spline.edit_data()")

    @contextmanager
    def edit_data(self):
        data = SplineData(self)
        yield data
        self.set_fit_points(data.fit_points)
        self.set_control_points(data.control_points)
        self.set_knot_values(data.knot_values)
        self.set_weights(data.weights)


class SplineData(object):
    def __init__(self, spline):
        self.fit_points = spline.get_fit_points()
        self.control_points = spline.get_control_points()
        self.knot_values = spline.get_knot_values()
        self.weights = spline.get_weights()

_BODY_TPL = """  0
BODY
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbModelerGeometry
 70
1
"""

modeler_geometry_subclass = DefSubclass('AcDbModelerGeometry', {
    'version': DXFAttr(70, default=1),
})


class Body(legacy.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_BODY_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, modeler_geometry_subclass)

    def get_acis_data(self):
        modeler_geometry = self.tags.subclasses[2]
        text_lines = convert_tags_to_text_lines(tag for tag in modeler_geometry if tag.code in (1, 3))
        return crypt.decode(text_lines)

    def set_acis_data(self, text_lines):
        def cleanup(lines):
            for line in lines:
                yield line.rstrip().replace('\n', '')

        modeler_geometry = self.tags.subclasses[2]
        # remove existing text
        modeler_geometry[:] = (tag for tag in modeler_geometry if tag.code not in (1, 3))
        modeler_geometry.extend(convert_text_lines_to_tags(crypt.encode(cleanup(text_lines))))

    @contextmanager
    def edit_data(self):
        data = ModelerGeometryData(self)
        yield data
        self.set_acis_data(data.text_lines)


class ModelerGeometryData:
    def __init__(self, body):
        self.text_lines = list(body.get_acis_data())

    def __str__(self):
        return "\n".join(self.text_lines)

    def set_text(self, text, sep='\n'):
        self.text_lines = text.split(sep)


class Region(Body):
    TEMPLATE = ClassifiedTags.from_text(_BODY_TPL.replace('BODY', 'REGION'))


_3DSOLID_TPL = """  0
3DSOLID
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbModelerGeometry
 70
1
100
AcDb3dSolid
350
0
"""


class Solid3d(Body):
    TEMPLATE = ClassifiedTags.from_text(_3DSOLID_TPL)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        entity_subclass,
        modeler_geometry_subclass,
        DefSubclass('AcDb3dSolid', {'history': DXFAttr(350, default=0)})
    )

_MESH_TPL = """  0
MESH
  5
0
330
1F
100
AcDbEntity
  8
0
100
AcDbSubDMesh
 71
2
 72
0
 91
1
 92
0
 93
0
 94
0
 95
0
"""

mesh_subclass = DefSubclass('AcDbSubDMesh', {
    'version': DXFAttr(71),
    'blend_crease': DXFAttr(72),  # 0 = off, 1 = on
    'subdivision_levels': DXFAttr(91),  # int >= 1
})


class Mesh(legacy.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_MESH_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, mesh_subclass)

    @property
    def AcDbSubDMesh(self):
        return self.tags.subclasses[2]

    def get_data(self):
        return MeshData(self)

    def set_data(self, data):
        try:
            pos92 = self.AcDbSubDMesh.tag_index(92)
        except ValueError:
            raise DXFStructureError("Tag 92 (vertex count) in MESH entity not found.")
        pending_tags = self._remove_existing_data(pos92)
        self._append_vertices(data.vertices)
        self._append_faces(data.faces)
        self._append_edges(data.edges)
        self._append_edge_crease_values(data.edge_crease_values)
        self.AcDbSubDMesh.extend(pending_tags)

    def _remove_existing_data(self, insert_pos):
        tags = self.AcDbSubDMesh
        code = 95
        # search count tags 95, 94, 93 at least face list (93) should exist
        while True:
            try:
                count_tag = tags.tag_index(code)
            except ValueError:
                code -= 1
                if code == 92:
                    raise DXFStructureError("No count tag 93, 94 or 95 in MESH entity found.")
            else:
                break
        last_pos = count_tag + 1 + tags[count_tag].value
        pending_tags = tags[last_pos:]
        del tags[insert_pos:]
        return pending_tags

    def _append_vertices(self, vertices):
        # (92) vertex count
        tags = self.AcDbSubDMesh
        tags.append(DXFTag(92, len(vertices)))
        tags.extend(DXFTag(10, vertex) for vertex in vertices)

    def _append_faces(self, faces):
        # (93) count of face tags
        tags = []
        list_size = 0
        for face in faces:
            list_size += (len(face) + 1)
            tags.append(DXFTag(90, len(face)))
            for index in face:
                tags.append(DXFTag(90, index))
        tags.insert(0, DXFTag(93, list_size))
        self.AcDbSubDMesh.extend(tags)

    def _append_edges(self, edges):
        # (94) count of edge tags
        tags = self.AcDbSubDMesh
        tags.append(DXFTag(94, len(edges)*2))
        for edge in edges:
            tags.append(DXFTag(90, edge[0]))
            tags.append(DXFTag(90, edge[1]))

    def _append_edge_crease_values(self, values):
        # (95) edge crease count
        tags = self.AcDbSubDMesh
        tags.append(DXFTag(95, len(values)))
        tags.extend(DXFTag(140, value) for value in values)

    @contextmanager
    def edit_data(self):
        data = self.get_data()
        yield data
        self.set_data(data)

    def get_vertices(self):
        vertices = []
        try:
            pos = self.AcDbSubDMesh.tag_index(92)
        except ValueError:
            return vertices
        itags = iter(self.AcDbSubDMesh[pos+1:])
        while True:
            try:
                tag = next(itags)
            except StopIteration:  # premature end of tags, return what you got
                break
            if tag.code == 10:
               vertices.append(tag.value)
            else:  # end of vertex list
                break
        return vertices

    def get_faces(self):
        faces = []
        try:
            pos = self.AcDbSubDMesh.tag_index(93)
        except ValueError:
            return faces
        face = []
        itags = iter(self.AcDbSubDMesh[pos+1:])
        try:
            while True:
                tag = next(itags)
                # loop until first tag.code != 90
                if tag.code != 90:
                    break
                count = tag.value  # count of vertex indices
                while count > 0:
                    tag = next(itags)
                    face.append(tag.value)
                    count -= 1
                faces.append(tuple(face))
                del face[:]
        except StopIteration:  # premature end of tags, return what you got
            pass
        return faces

    def get_edges(self):
        edges = []
        try:
            pos = self.AcDbSubDMesh.tag_index(94)
        except ValueError:
            return edges
        start_index = None
        for index in Mesh.get_raw_list(self.AcDbSubDMesh, pos+1, code=90):
            if start_index is None:
                start_index = index
            else:
                edges.append((start_index, index))
                start_index = None
        return edges

    def get_edge_crease_values(self):
        try:
            pos = self.AcDbSubDMesh.tag_index(95)
        except ValueError:
            return []
        return Mesh.get_raw_list(self.AcDbSubDMesh, pos+1, code=140)

    @staticmethod
    def get_raw_list(tags, pos, code):
        raw_list = []
        itags = iter(tags[pos:])
        while True:
            try:
                tag = next(itags)
            except StopIteration:
                break
            if tag.code == code:
                raw_list.append(tag.value)
            else:
                break
        return raw_list


class MeshData(object):
    def __init__(self, mesh):
        self.vertices = mesh.get_vertices()
        self.faces = mesh.get_faces()
        self.edges = mesh.get_edges()
        self.edge_crease_values = mesh.get_edge_crease_values()

    def add_face(self, vertices):  # todo
        pass

    def add_edge(self, vertices):  # todo
        pass

    def optimize(self):  # todo
        pass