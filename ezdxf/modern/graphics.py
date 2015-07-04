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
# - Surface
#
# Unsupported AutoCAD/Windows entities: (existing entities will be preserved)
# - ACAD_PROXY_ENTITY (compressed data)
# - OLEFRAME (compressed data)
# - OLE2FRAME (compressed data)

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager

from ..legacy import graphics as legacy
from ..tags import DXFTag, Tags
from ..classifiedtags import ClassifiedTags
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass
from .. import const
from ..facemixins import PolyfaceMixin, PolymeshMixin
from ..truecolor import int2rgb, rgb2int

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
    'true_color': DXFAttr(420, dxfversion='AC1018'),  # true color as 0x00RRGGBB 24-bit value
    'color_name': DXFAttr(430, dxfversion='AC1018'),  # color name as string
    'transparency': DXFAttr(440, dxfversion='AC1018'),  # transparency value 0x020000TT 0 = fully transparent / 255 = opaque
    'shadow_mode': DXFAttr(284, dxfversion='AC1021'),  # shadow_mode
    # 0 = Casts and receives shadows
    # 1 = Casts shadows
    # 2 = Receives shadows
    # 3 = Ignores shadows

})
def float2transparency(value):
    return int((1. - float(value)) * 255) | 0x02000000

def transparency2float(value):
    return 1. - float(int(value) & 0xFF) / 255.

# noinspection PyUnresolvedReferences
class ModernGraphicEntityExtension(object):
    # TODO: test DXFEntity.rgb property
    @property
    def rgb(self):
        return int2rgb(self.get_dxf_attrib('true_color'))

    @rgb.setter  # line.rgb = (12, 34, 56)
    def rgb(self, rgb):
        self.set_dxf_attrib('true_color', rgb2int(rgb))

    # TODO: test DXFEntity.transparency property
    @property
    def transparency(self):
        return transparency2float(self.get_dxf_attrib('transparency'))

    @transparency.setter  # line.transparency = 0.50
    def transparency(self, transparency):
        # 0.0 = opaque & 1.0 if 100% transparent
        self.set_dxf_attrib('transparency', float2transparency(transparency))

class ModernGraphicEntity(legacy.GraphicEntity, ModernGraphicEntityExtension):
    """ Default graphic entity wrapper, allows access to following dxf attributes:
     - handle
     - owner handle
     - layer
     - linetype
     - color
     - paperspace
     - ltscale
     - invisible
     - true_color (as int)
     - color_name
     - transparency
     - shadow_mode

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


class Line(legacy.Line, ModernGraphicEntityExtension):
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


class Point(legacy.Point, ModernGraphicEntityExtension):
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


class Circle(legacy.Circle, ModernGraphicEntityExtension):
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


class Arc(legacy.Arc, ModernGraphicEntityExtension):
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


class Trace(legacy.Trace, ModernGraphicEntityExtension):
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


class Face(legacy.Face, ModernGraphicEntityExtension):
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


class Text(legacy.Text, ModernGraphicEntityExtension):
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


class Polyline(legacy.Polyline, ModernGraphicEntityExtension):
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


class Vertex(legacy.Vertex, ModernGraphicEntityExtension):
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


class LWPolyline(ModernGraphicEntity):
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


class Block(legacy.GraphicEntity, ModernGraphicEntityExtension):
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


class EndBlk(ModernGraphicEntity):
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


class Insert(legacy.Insert, ModernGraphicEntityExtension):
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


class Attdef(legacy.Attdef, ModernGraphicEntityExtension):
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


class Attrib(legacy.Attrib, ModernGraphicEntityExtension):
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


class Ellipse(ModernGraphicEntity):
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


class Ray(legacy.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_RAY_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, ray_subclass)


class XLine(Ray):
    TEMPLATE = ClassifiedTags.from_text(_RAY_TPL.replace('RAY', 'XLINE'))


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
class Shape(ModernGraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_SHAPE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, shape_subclass)
