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

from ..ac1009 import graphics as ac1009
from ..tags import DXFTag
from ..classifiedtags import ClassifiedTags
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass
from .. import const
from ..facemixins import PolyfaceMixin, PolymeshMixin

none_subclass = DefSubclass(None, {
    'handle': DXFAttr(5, None),
    'owner': DXFAttr(330, None),  # Soft-pointer ID/handle to owner BLOCK_RECORD object
})

entity_subclass = DefSubclass('AcDbEntity', {
    'paperspace': DXFAttr(67, None),  # 0 .. modelspace, 1 .. paperspace, default is 0
    'layer': DXFAttr(8, None),  # layername as string, default is '0'
    'linetype': DXFAttr(6, None),  # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
    'ltscale': DXFAttr(48, None),  # linetype scale, default is 1.0
    'invisible': DXFAttr(60, None),  # invisible .. 1, visible .. 0, default is 0
    'color': DXFAttr(62, None),  # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
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
    'start': DXFAttr(10, 'Point2D/3D'),
    'end': DXFAttr(11, 'Point2D/3D'),
    'thickness': DXFAttr(39, None),
    'extrusion': DXFAttr(210, 'Point3D'),
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
    'point': DXFAttr(10, 'Point2D/3D'),
    'thickness': DXFAttr(39, None),
    'extrusion': DXFAttr(210, 'Point3D'),
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
    'center': DXFAttr(10, 'Point2D/3D'),
    'radius': DXFAttr(40, None),
    'thickness': DXFAttr(39, None),
    'extrusion': DXFAttr(210, 'Point3D'),
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
        'center': DXFAttr(10, 'Point2D/3D'),
        'radius': DXFAttr(40, None),
        'thickness': DXFAttr(39, None),
    }),
    DefSubclass('AcDbArc', {
        'start_angle': DXFAttr(50, None),
        'end_angle': DXFAttr(51, None),
        'extrusion': DXFAttr(210, 'Point3D'),
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
    'vtx0': DXFAttr(10, 'Point2D/3D'),
    'vtx1': DXFAttr(11, 'Point2D/3D'),
    'vtx2': DXFAttr(12, 'Point2D/3D'),
    'vtx3': DXFAttr(13, 'Point2D/3D'),
    'thickness': DXFAttr(39, None),
    'extrusion': DXFAttr(210, 'Point3D'),
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
    'vtx0': DXFAttr(10, 'Point2D/3D'),
    'vtx1': DXFAttr(11, 'Point2D/3D'),
    'vtx2': DXFAttr(12, 'Point2D/3D'),
    'vtx3': DXFAttr(13, 'Point2D/3D'),
    'invisible_edge': DXFAttr(70, None),
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
        'insert': DXFAttr(10, 'Point2D/3D'),
        'height': DXFAttr(40, None),
        'text': DXFAttr(1, None),
        'rotation': DXFAttr(50, None),  # in degrees (circle = 360deg)
        'oblique': DXFAttr(51, None),  # in degrees, vertical = 0deg
        'style': DXFAttr(7, None),  # text style
        'width': DXFAttr(41, None),  # width FACTOR!
        'text_generation_flag': DXFAttr(71, None),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, None),  # horizontal justification
        'align_point': DXFAttr(11, 'Point2D/3D'),
        'thickness': DXFAttr(39, None),
        'extrusion': DXFAttr(210, 'Point3D'),
    }),
    DefSubclass('AcDbText', {'valign': DXFAttr(73, None)}))


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
    'elevation': DXFAttr(10, 'Point3D'),
    'flags': DXFAttr(70, None),
    'default_start_width': DXFAttr(40, None),
    'default_end_width': DXFAttr(41, None),
    'm_count': DXFAttr(71, None),
    'n_count': DXFAttr(72, None),
    'm_smooth_density': DXFAttr(73, None),
    'n_smooth_density': DXFAttr(74, None),
    'smooth_type': DXFAttr(75, None),
    'thickness': DXFAttr(39, None),
    'extrusion': DXFAttr(210, 'Point3D'),
})


class Polyline(ac1009.Polyline):
    TEMPLATE = ClassifiedTags.from_text(_POLYLINE_TPL)
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
        face = Polyface(polyline.tags)
        face.set_layout(polyline.layout)
        return face


class Polymesh(Polyline, PolymeshMixin):
    @staticmethod
    def convert(polyline):
        mesh = Polymesh(polyline.tags)
        mesh.set_layout(polyline.layout)
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
    DefSubclass('AcDbVertex', {}),  # subclasses[2]
    DefSubclass('AcDb2dVertex', {  # subclasses[3]
        'location': DXFAttr(10, 'Point2D/3D'),
        'start_width': DXFAttr(40, None),
        'end_width': DXFAttr(41, None),
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
 43
0
"""

lwpolyline_subclass = DefSubclass('AcDbPolyline', {
    'elevation': DXFAttr(38, None),
    'flags': DXFAttr(70, None),
    'constwidth': DXFAttr(43, None),
    'count': DXFAttr(90, None),
    'extrusion': DXFAttr(210, 'Point3D'),
})

LWPOINTCODES = (10, 20, 40, 41, 42)


class LWPolyline(ac1009.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_LWPOLYLINE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, lwpolyline_subclass)
    
    def __len__(self):
        return self.dxf.count
        
    def close(self, status=True):
        flagsnow = self.dxf.flags
        if status:
            self.dxf.flags = flagsnow | const.LWPOLYLINE_CLOSED
        else:
            self.dxf.flags = flagsnow & (~const.LWPOLYLINE_CLOSED)
    
    def _setup_points(self, points):
        if self.dxf.count > 0:
            raise ValueError('only callable for new LWPolylines')
        subclass = self.tags.subclasses[2]
        count = 0
        
        def append_point(point):
            subclass.append(DXFTag(10, point[0]))
            subclass.append(DXFTag(20, point[1]))
            try:
                subclass.append(DXFTag(40, point[2]))
                subclass.append(DXFTag(41, point[3]))
                subclass.append(DXFTag(42, point[4]))
            except IndexError:
                pass
            
        for point in points:
            append_point(point)
            count += 1
        self.dxf.count = count
        
    def __iter__(self):
        subclass = self.tags.subclasses[2]  # subclass AcDbPolyline
        point = []
        for tag in subclass:
            if tag.code in LWPOINTCODES:
                if tag.code == 10:
                    if point:
                        yield tuple(point)
                        point = []
                point.append(tag)
        if point:
            yield tuple(point)

    def points(self):
        return ((point[0].value, point[1].value) for point in self)

    def __getitem__(self, index):
        if index < 0:
            index += self.dxf.count
        for x, point in enumerate(self.points()):
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
    DefSubclass('AcDbEntity', {'layer': DXFAttr(8, None)}),
    DefSubclass('AcDbBlockBegin', {
        'name': DXFAttr(2, None),
        'name2': DXFAttr(3, None),
        'description': DXFAttr(4, None),
        'flags': DXFAttr(70, None),
        'base_point': DXFAttr(10, 'Point2D/3D'),
        'xref_path': DXFAttr(1, None),
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
    DefSubclass('AcDbEntity', {'layer': DXFAttr(8, None)}),
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
    'attribs_follow': DXFAttr(66, None),
    'name': DXFAttr(2, None),
    'insert': DXFAttr(10, 'Point2D/3D'),
    'xscale': DXFAttr(41, None),
    'yscale': DXFAttr(42, None),
    'zscale': DXFAttr(43, None),
    'rotation': DXFAttr(50, None),
    'column_count': DXFAttr(70, None),
    'row_count': DXFAttr(71, None),
    'column_spacing': DXFAttr(44, None),
    'row_spacing': DXFAttr(45, None),
    'extrusion': DXFAttr(210, 'Point3D'),
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
        'insert': DXFAttr(10, 'Point2D/3D'),
        'thickness': DXFAttr(39, None),
        'height': DXFAttr(40, None),
        'text': DXFAttr(1, None),
        'rotation': DXFAttr(50, None),
        'width': DXFAttr(41, None),
        'oblique': DXFAttr(51, None),
        'style': DXFAttr(7, None),
        'text_generation_flag': DXFAttr(71, None),
        'halign': DXFAttr(72, None),
        'align_point': DXFAttr(11, 'Point2D/3D'),
        'extrusion': DXFAttr(210, 'Point3D'),
    }),
    DefSubclass('AcDbAttributeDefinition', {
        'prompt': DXFAttr(3, None),
        'tag': DXFAttr(2, None),
        'flags': DXFAttr(70, None),
        'field_length': DXFAttr(73, None),
        'valign': DXFAttr(74, None),
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
        'insert': DXFAttr(10, 'Point2D/3D'),
        'thickness': DXFAttr(39, None),
        'height': DXFAttr(40, None),
        'text': DXFAttr(1, None),
        'rotation': DXFAttr(50, None), #  error in DXF description, because placed in 'AcDbAttribute'
        'width': DXFAttr(41, None), #  error in DXF description, because placed in 'AcDbAttribute'
        'oblique': DXFAttr(51, None), #  error in DXF description, because placed in 'AcDbAttribute'
        'style': DXFAttr(7, None), #  error in DXF description, because placed in 'AcDbAttribute'
    }),
    DefSubclass('AcDbAttribute', {
        'tag': DXFAttr(2, None),
        'flags': DXFAttr(70, None),
        'field_length': DXFAttr(73, None),
        'text_generation_flag': DXFAttr(71, None),
        'halign': DXFAttr(72, None),
        'valign': DXFAttr(74, None),
        'align_point': DXFAttr(11, 'Point2D/3D'),
        'extrusion': DXFAttr(210, 'Point3D'),
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
    'center': DXFAttr(10, 'Point2D/3D'),
    'majoraxis': DXFAttr(11, 'Point2D/3D'),  # relative to the center
    'extrusion': DXFAttr(210, 'Point3D'),
    'ratio': DXFAttr(40, None),
    'startparam': DXFAttr(41, None),  # this value is 0.0 for a full ellipse
    'endparam': DXFAttr(42, None),  # this value is 2*pi for a full ellipse
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
    'start': DXFAttr(10, 'Point3D'),
    'unitvector': DXFAttr(11, 'Point3D'),
})


class Ray(ac1009.GraphicEntity, ac1009.ColorMixin):
    TEMPLATE = ClassifiedTags.from_text(_RAY_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, ray_subclass)

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
    'insert': DXFAttr(10, 'Point3D'),
    'height': DXFAttr(40, None),  # nominal (initial) text height
    'rect_width': DXFAttr(41, None),  # reference rectangle width
    'attachment_point': DXFAttr(71, None),
    # 1 = Top left; 2 = Top center; 3 = Top right
    # 4 = Middle left; 5 = Middle center; 6 = Middle right
    # 7 = Bottom left; 8 = Bottom center; 9 = Bottom right
    'write_direction': DXFAttr(72, None),
    # 1 = Left to right
    # 3 = Top to bottom
    # 5 = By style (the flow direction is inherited from the associated text style)
    'style': DXFAttr(7, None),  # text style name, 'STANDARD' if not provided
    'extrusion': DXFAttr(210, 'Point3D'),
    'text_direction': DXFAttr(11, 'Point3D'), # x-axis direction vector (in WCS)
    # If *rotation* and *text_direction* are present, *text_direction* wins
    'width': DXFAttr(43, None),  # Horizontal width of the characters that make up the mtext entity.
    # This value will always be equal to or less than the value of *rect_width*, (read-only, ignored if supplied)
    'rect_height': DXFAttr(43, None),  # vertical height of the mtext entity (read-only, ignored if supplied)
    'rotation': DXFAttr(50, None),  # in degrees (circle=360 deg) -  error in DXF description says radians
    'line_spacing_style': DXFAttr(73, None),  # line spacing style (optional):
    # 1 = At least (taller characters will override)
    # 2 = Exact (taller characters will not override)
    'line_spacing_factor': DXFAttr(44, None),  # line spacing factor (optional):
    # Percentage of default (3-on-5) line spacing to be applied. Valid values
    # range from 0.25 to 4.00
})

class MText(ac1009.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_MTEXT_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, mtext_subclass)
    def set_pos(self, pos, align=None):
        if align is None:
            align = self.get_align()
        align = align.upper()
        self.set_align(align)
        self.set_dxf_attrib('insert', pos)
        return self

    def get_pos(self):
        p1 = self.dxf.insert
        align = self.get_align()
        return align, p1

    def set_align(self, align='TOP_LEFT'):
        align = align.upper()
        attachment_point = const.MTEXT_ALIGN_FLAGS[align]
        self.set_dxf_attrib('attachment_point', attachment_point)
        return self

    def get_align(self):
        attachment_point = self.get_dxf_attrib('attachment_point', default=1)
        return const.MTEXT_ALIGNMENT_BY_FLAGS.get(attachment_point, 'TOP_LEFT')

    def set_write_direction(self, direction='LEFT_TO_RIGHT'):
        direction = direction.upper()
        flag = const.MTEXT_WRITE_DIRECTION_FLAGS[direction]
        self.set_dxf_attrib('write_direction', flag)

    def get_write_direction(self):
        flag = self.get_dxf_attrib('write_direction', default=const.MTEXT_LEFT_TO_RIGHT)
        return const.MTEXT_WRITE_DIRECTION_BY_FLAGS[flag]

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
        str_chunks = split_string_in_chunks(text)
        if len(str_chunks) == 0:
            str_chunks.append("")
        while len(str_chunks) > 1:
            tags.append(DXFTag(3, str_chunks.pop(0)))
        tags.append(DXFTag(1, str_chunks[0]))

    @contextmanager
    def buffer(self):
        buffer = MTextBuffer(self.get_text())
        yield buffer
        self.set_text(buffer.get_text())

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
    GROUP_STOP = '}'
    GROUP = GROUP_START + '%s' + GROUP_STOP
    NBSP = '\\~' # none breaking space

    def __init__(self, text):
        self.text = text

    def set(self, text):
        self.text = text

    def __iadd__(self, text):
        self.text += text
        return self
    append = __iadd__

    def get_text(self):
        return self.text

    def set_font(self, name, bold=False, italic=False, codepage=1252, pitch=0):
        bold_flag = 1 if bold else 0
        italic_flag = 1 if italic else 0
        s = "\\F{}|b{}|i{}|c{}|p{};".format(name, bold_flag, italic_flag, codepage, pitch)
        self.append(s)


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
