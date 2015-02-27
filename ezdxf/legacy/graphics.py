# Purpose: DXF 12 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..classifiedtags import ClassifiedTags
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass
from ..dxfentity import DXFEntity
from .. import const
from ..const import VERTEXNAMES
from ..facemixins import PolyfaceMixin, PolymeshMixin


class ColorMixin(object):
    def set_ext_color(self, color):
        """ Set color by color-name or rgb-tuple, for DXF R12 the nearest
        default DXF color index will be determined.
        """
        # TODO: implement ColorMixin.set_ext_color()
        raise NotImplementedError('set_ext_color()')

    def get_rgb_color(self):
        # TODO: implement ColorMixin.get_rgb_color()
        return 0, 0, 0

    def get_color_name(self):
        # TODO: implement ColorMixin.get_color_name()
        return 'Black'


class QuadrilateralMixin(object):
    def __getitem__(self, num):
        return self.get_dxf_attrib(VERTEXNAMES[num])

    def __setitem__(self, num, value):
        return self.set_dxf_attrib(VERTEXNAMES[num], value)


def make_attribs(additional=None):
    dxfattribs = {
        'handle': DXFAttr(5),
        'layer': DXFAttr(8, default='0'),  # layername as string
        'linetype': DXFAttr(6, default='BYLAYER'),  # linetype as string, special names BYLAYER/BYBLOCK
        'color': DXFAttr(62, default=256),  # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER
        'thickness': DXFAttr(39, default=0),  # thickness of 2D elements
        'paperspace': DXFAttr(67, default=0),  # 0 .. modelspace, 1 .. paperspace
        'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),  # Z-axis of OCS (Object-Coordinate-System)
    }
    if additional is not None:
        dxfattribs.update(additional)
    return DXFAttributes(DefSubclass(None, dxfattribs))


class GraphicEntity(DXFEntity):
    """ Default graphic entity wrapper, allows access to following dxf attributes:

     - handle
     - layer
     - linetype
     - color
     - paperspace
     - extrusion

     Wrapper for all unsupported graphic entities.
    """
    DXFATTRIBS = make_attribs()

_LINE_TPL = """  0
LINE
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
1.0
 21
1.0
 31
1.0
"""


class Line(GraphicEntity, ColorMixin):
    TEMPLATE = ClassifiedTags.from_text(_LINE_TPL)
    DXFATTRIBS = make_attribs({
        'start': DXFAttr(10, xtype='Point2D/3D'),
        'end': DXFAttr(11, xtype='Point2D/3D'),
    })

_POINT_TPL = """  0
POINT
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
"""


class Point(GraphicEntity, ColorMixin):
    TEMPLATE = ClassifiedTags.from_text(_POINT_TPL)
    DXFATTRIBS = make_attribs({
        'location': DXFAttr(10, xtype='Point2D/3D'),
    })

_CIRCLE_TPL = """  0
CIRCLE
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
 40
1.0
"""


class Circle(GraphicEntity, ColorMixin):
    TEMPLATE = ClassifiedTags.from_text(_CIRCLE_TPL)
    DXFATTRIBS = make_attribs({
        'center': DXFAttr(10, xtype='Point2D/3D'),
        'radius': DXFAttr(40),
    })

_ARC_TPL = """  0
ARC
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
 40
1.0
 50
0
 51
360
"""


class Arc(GraphicEntity, ColorMixin):
    TEMPLATE = ClassifiedTags.from_text(_ARC_TPL)
    DXFATTRIBS = make_attribs({
        'center': DXFAttr(10, xtype='Point2D/3D'),
        'radius': DXFAttr(40),
        'start_angle': DXFAttr(50),
        'end_angle': DXFAttr(51),
    })

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


class Trace(GraphicEntity, ColorMixin, QuadrilateralMixin):
    TEMPLATE = ClassifiedTags.from_text(_TRACE_TPL)
    DXFATTRIBS = make_attribs({
        'vtx0': DXFAttr(10, xtype='Point2D/3D'),
        'vtx1': DXFAttr(11, xtype='Point2D/3D'),
        'vtx2': DXFAttr(12, xtype='Point2D/3D'),
        'vtx3': DXFAttr(13, xtype='Point2D/3D'),
    })


class Solid(Trace):
    TEMPLATE = ClassifiedTags.from_text(_TRACE_TPL.replace('TRACE', 'SOLID'))


class Face(Trace):
    TEMPLATE = ClassifiedTags.from_text(_TRACE_TPL.replace('TRACE', '3DFACE'))
    DXFATTRIBS = make_attribs({
        'vtx0': DXFAttr(10, xtype='Point3D'),
        'vtx1': DXFAttr(11, xtype='Point3D'),
        'vtx2': DXFAttr(12, xtype='Point3D'),
        'vtx3': DXFAttr(13, xtype='Point3D'),
        'invisible_edge': DXFAttr(70, default=0),
    })

_TEXT_TPL = """  0
TEXT
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
 73
0
 11
0.0
 21
0.0
 31
0.0
"""


class Text(GraphicEntity, ColorMixin):
    TEMPLATE = ClassifiedTags.from_text(_TEXT_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'rotation': DXFAttr(50, default=0.0),  # in degrees (circle = 360deg)
        'oblique': DXFAttr(51, default=0.0),  # in degrees, vertical = 0deg
        'style': DXFAttr(7, default='STANDARD'),  # text style
        'width': DXFAttr(41, default=1.0),  # width FACTOR!
        'text_generation_flag': DXFAttr(71, default=0),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, default=0),  # horizontal justification
        'valign': DXFAttr(73,  default=0),  # vertical justification
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
    })

    def set_pos(self, p1, p2=None, align=None):
        if align is None:
            align = self.get_align()
        align = align.upper()
        self.set_align(align)
        self.set_dxf_attrib('insert', p1)
        if align in ('ALIGNED', 'FIT'):
            if p2 is None:
                raise ValueError("Alignment '{}' requires a second alignment point.".format(align))
        else:
            p2 = p1
        self.set_dxf_attrib('align_point', p2)
        return self

    def get_pos(self):
        p1 = self.dxf.insert
        p2 = self.get_dxf_attrib('align_point', (0., 0., 0.))
        align = self.get_align()
        if align == 'LEFT':
            return align, p1, None
        if align in ('FIT', 'ALIGN'):
            return align, p1, p2
        return align, p2, None

    def set_align(self, align='LEFT'):
        align = align.upper()
        halign, valign = const.TEXT_ALIGN_FLAGS[align]
        self.set_dxf_attrib('halign', halign)
        self.set_dxf_attrib('valign', valign)
        return self

    def get_align(self):
        halign = self.get_dxf_attrib('halign', 0)
        valign = self.get_dxf_attrib('valign', 0)
        if halign > 2:
            valign = 0
        return const.TEXT_ALIGNMENT_BY_FLAGS.get((halign, valign), 'LEFT')

_BLOCK_TPL = """  0
BLOCK
  5
0
  8
0
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


class Block(GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_BLOCK_TPL)
    DXFATTRIBS = make_attribs({
        'name': DXFAttr(2),
        'name2': DXFAttr(3),
        'flags': DXFAttr(70),
        'base_point': DXFAttr(10, xtype='Point2D/3D'),
        'xref_path': DXFAttr(1),
    })


class EndBlk(GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text("  0\nENDBLK\n  5\n0\n")
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {'handle': DXFAttr(5)}))

_INSERT_TPL = """  0
INSERT
  5
0
  8
0
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
# IMPORTANT: Bug in AutoCAD 2010
# attribsfollow = 0, for NO attribsfollow, does not work with ACAD 2010
# if no attribs attached to the INSERT entity, omit attribsfollow tag


class Insert(GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_INSERT_TPL)
    DXFATTRIBS = make_attribs({
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
    })

    def attribs(self):
        """ Iterate over all appended ATTRIB entities, yields DXFEntity() or inherited.
        """
        if self.dxf.attribs_follow == 0:
            return
        dxffactory = self.dxffactory
        handle = self.tags.link
        while handle is not None:
            entity = dxffactory.wrap_handle(handle)
            next_entity = entity.tags.link
            if next_entity is None:  # found SeqEnd
                return
            else:
                yield entity
                handle = next_entity

    def place(self, insert=None, scale=None, rotation=None):
        if insert is not None:
            self.dxf.insert = insert
        if scale is not None:
            if len(scale) != 3:
                raise ValueError("Parameter scale has to be a 3-tuple.")
            x, y, z = scale
            self.dxf.xscale = x
            self.dxf.yscale = y
            self.dxf.zscale = z
        if rotation is not None:
            self.dxf.rotation = rotation
        return self

    def grid(self, size=(1, 1), spacing=(1, 1)):
        if len(size) != 2:
            raise ValueError("Parameter size has to be a (row_count, column_count)-tuple.")
        if len(spacing) != 2:
            raise ValueError("Parameter spacing has to be a (row_spacing, column_spacing)-tuple.")
        self.dxf.row_count = size[0]
        self.dxf.column_count = size[1]
        self.dxf.row_spacing = spacing[0]
        self.dxf.column_spacing = spacing[1]
        return self

    def get_attrib(self, tag):
        for attrib in self.attribs():
            if tag == attrib.dxf.tag:
                return attrib
        return None

    def get_attrib_text(self, tag, default=None):
        attrib = self.get_attrib(tag)
        if attrib is None:
            return default
        return attrib.dxf.text

    def has_attrib(self, tag):
        return self.get_attrib(tag) is not None

    def add_attrib(self, tag, text, insert, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['tag'] = tag
        dxfattribs['text'] = text
        dxfattribs['insert'] = insert
        attrib_entity = self._new_entity('ATTRIB', dxfattribs)
        self._append_attrib_entity(attrib_entity)

    def _append_attrib_entity(self, entity):
        if self.dxf.attribs_follow == 0:
            prev = self
            seqend = self._new_entity('SEQEND', {})
        else:
            attribs = list(self.attribs())
            prev = attribs[-1]
            seqend = self.dxffactory.wrap_handle(prev.tags.link)

        prev.tags.link = entity.dxf.handle
        entity.tags.link = seqend.dxf.handle
        self.dxf.attribs_follow = 1

    def destroy(self):
        db = self.entitydb
        handle = self.tags.link
        while handle is not None:
            tags = db[handle]
            db.delete_handle(handle)
            handle = tags.link
            tags.link = None

        #cleanup
        self.tags.link = None
        self.dxf.attribs_follow = 0


class SeqEnd(GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text("  0\nSEQEND\n  5\n0\n")
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5),
        'paperspace': DXFAttr(67, default=0),
    }))

_ATTDEF_TPL = """  0
ATTDEF
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
 40
1.0
  1
DEFAULTTEXT
  3
PROMPTTEXT
  2
TAG
 70
0
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


class Attdef(Text):
    TEMPLATE = ClassifiedTags.from_text(_ATTDEF_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'prompt': DXFAttr(3),
        'tag': DXFAttr(2),
        'flags': DXFAttr(70),
        'field_length': DXFAttr(73, default=0),
        'rotation': DXFAttr(50, default=0.0),
        'oblique': DXFAttr(51, default=0.0),
        'width': DXFAttr(41, default=1.0),  # width factor
        'style': DXFAttr(7, default='STANDARD'),
        'text_generation_flag': DXFAttr(71, default=0),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, default=0),  # horizontal justification
        'valign': DXFAttr(74, default=0),  # vertical justification
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
    })

_ATTRIB_TPL = """  0
ATTRIB
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
 40
1.0
  1
DEFAULTTEXT
  2
TAG
 70
0
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


class Attrib(Text):
    TEMPLATE = ClassifiedTags.from_text(_ATTRIB_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'tag': DXFAttr(2),
        'flags': DXFAttr(70),
        'field_length': DXFAttr(73, default=0),
        'rotation': DXFAttr(50, default=0.0),
        'oblique': DXFAttr(51, default=0.0),
        'width': DXFAttr(41, default=1.0),  # width factor
        'style': DXFAttr(7, default='STANDARD'),
        'text_generation_flag': DXFAttr(71, default=0),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, default=0),  # horizontal justification
        'valign': DXFAttr(74, default=0),  # vertical justification
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
    })

_POLYLINE_TPL = """  0
POLYLINE
  5
0
  8
0
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


class Polyline(GraphicEntity, ColorMixin):
    ANY3D = const.POLYLINE_3D_POLYLINE + const.POLYLINE_3D_POLYMESH + const.POLYLINE_POLYFACE
    TEMPLATE = ClassifiedTags.from_text(_POLYLINE_TPL)
    DXFATTRIBS = make_attribs({
        'elevation': DXFAttr(10, xtype='Point2D/3D'),
        'flags': DXFAttr(70, default=0),
        'default_start_width': DXFAttr(40, default=0.0),
        'default_end_width': DXFAttr(41, default=0.0),
        'm_count': DXFAttr(71, default=0),
        'n_count': DXFAttr(72, default=0),
        'm_smooth_density': DXFAttr(73, default=0),
        'n_smooth_density': DXFAttr(74, default=0),
        'smooth_type': DXFAttr(75, default=0),
    })

    def post_new_hook(self):
        seqend = self._new_entity('SEQEND', {})
        self.tags.link = seqend.dxf.handle

    def get_vertex_flags(self):
        return const.VERTEX_FLAGS[self.get_mode()]

    def get_mode(self):
        if self.is_3d_polyline:
            return 'AcDb3dPolyline'
        elif self.is_polygon_mesh:
            return 'AcDbPolygonMesh'
        elif self.is_poly_face_mesh:
            return 'AcDbPolyFaceMesh'
        else:
            return 'AcDb2dPolyline'

    @property
    def is_2d_polyline(self):
        return self.dxf.flags & Polyline.ANY3D == 0

    @property
    def is_3d_polyline(self):
        return self.dxf.flags & const.POLYLINE_3D_POLYLINE

    @property
    def is_polygon_mesh(self):
        return self.dxf.flags & const.POLYLINE_3D_POLYMESH

    @property
    def is_poly_face_mesh(self):
        return self.dxf.flags & const.POLYLINE_POLYFACE

    def m_close(self):
        self.dxf.flags = self.dxf.flags | const.POLYLINE_MESH_CLOSED_M_DIRECTION

    def n_close(self):
        self.dxf.flags = self.dxf.flags | const.POLYLINE_MESH_CLOSED_N_DIRECTION

    def close(self, m_close, n_close=False):
        if m_close:
            self.m_close()
        if n_close:
            self.n_close()

    def __len__(self):
        count = 0
        db = self.entitydb
        tags = db[self.tags.link]
        while tags.link is not None:
            count += 1
            tags = db[tags.link]
        return count

    def __getitem__(self, pos):
        count = 0
        db = self.entitydb
        tags = db[self.tags.link]
        while tags.link is not None:
            if count == pos:
                return self.dxffactory.wrap_entity(tags)
            count += 1
            tags = db[tags.link]
        raise IndexError("vertex index out of range")

    def vertices(self):
        wrapper = self.dxffactory.wrap_handle
        handle = self.tags.link
        while handle is not None:
            entity = wrapper(handle)
            handle = entity.tags.link
            if entity.dxftype() == 'VERTEX':
                yield entity

    def points(self):
        return (vertex.dxf.location for vertex in self.vertices())

    def append_vertices(self, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        if len(points) > 0:
            last_vertex = self._get_last_vertex()
            for new_vertex in self._points_to_dxf_vertices(points, dxfattribs):
                self._insert_after(last_vertex, new_vertex)
                last_vertex = new_vertex

    @staticmethod
    def _insert_after(prev_vertex, new_vertex):
        succ = prev_vertex.tags.link
        prev_vertex.tags.link = new_vertex.dxf.handle
        new_vertex.tags.link = succ

    def _get_last_vertex(self):
        db = self.entitydb
        tags = self.tags
        handle = self.dxf.handle
        while tags.link is not None:  # while not SEQEND
            prev_handle = handle
            handle = tags.link
            tags = db[handle]
        return self.dxffactory.wrap_handle(prev_handle)

    def insert_vertices(self, pos, points, dxfattribs=None):
        """ Insert *points* at position *pos*.

        :param points: list of (x, y, z)-tuples
        :param dxfattribs: dict of DXF attributes
        """
        if dxfattribs is None:
            dxfattribs = {}
        if pos > 0:
            insert_vertex = self.__getitem__(pos - 1)
        else:
            insert_vertex = self
        for new_vertex in self._points_to_dxf_vertices(points, dxfattribs):
            self._insert_after(insert_vertex, new_vertex)
            insert_vertex = new_vertex

    def _append_vertices(self, vertices):
        """ Append DXF Vertex() objects.

        :param vertices: list of DXF Vertex() objects
        """
        last_vertex = self._get_last_vertex()
        for vertex in vertices:
            self._insert_after(last_vertex, vertex)
            last_vertex = vertex

    def _points_to_dxf_vertices(self, points, dxfattribs):
        """ Converts point (x,y, z)-tuples into DXF Vertex() objects.

        :param points: list of (x, y,z)-tuples
        :param dxfattribs: dict of DXF attributes
        """
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | self.get_vertex_flags()
        vertices = []
        for point in points:
            dxfattribs['location'] = point
            vertices.append(self._new_entity('VERTEX', dxfattribs))
        return vertices

    def delete_vertices(self, pos, count=1):
        db = self.entitydb
        prev_vertex = self.__getitem__(pos-1).tags if pos > 0 else self.tags
        vertex = db[prev_vertex.link]
        while vertex.dxftype() == 'VERTEX':
            db.delete_handle(prev_vertex.link)  # remove from database
            prev_vertex.link = vertex.link  # remove vertex from list
            count -= 1
            if count == 0:
                return
            vertex = db[prev_vertex.link]
        raise ValueError("invalid count")

    def _unlink_all_vertices(self):
        # but don't delete it from database
        last_vertex = self._get_last_vertex()
        self.tags.link = last_vertex.tags.link  # link POLYLINE -> SEQEND

    def cast(self):
        mode = self.get_mode()
        if mode == 'AcDbPolyFaceMesh':
            return Polyface.convert(self)
        elif mode == 'AcDbPolygonMesh':
            return Polymesh.convert(self)
        else:
            return self

    def destroy(self):
        db = self.entitydb
        handle = self.tags.link
        while handle is not None:
            tags = db[handle]
            db.delete_handle(handle)
            handle = tags.link
        self.tags.link = None


class Polyface(Polyline, PolyfaceMixin):
    @staticmethod
    def convert(polyline):
        face = Polyface(polyline.tags, polyline.drawing)
        return face

        
class Polymesh(Polyline, PolymeshMixin):
    @staticmethod
    def convert(polyline):
        mesh = Polymesh(polyline.tags, polyline.drawing)
        return mesh

_VERTEX_TPL = """ 0
VERTEX
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
 40
0.0
 41
0.0
 42
0.0
 70
0
"""


class Vertex(GraphicEntity, ColorMixin, QuadrilateralMixin):
    FACE_FLAGS = const.VTX_3D_POLYGON_MESH_VERTEX + const.VTX_3D_POLYFACE_MESH_VERTEX
    VTX3D = const.VTX_3D_POLYLINE_VERTEX + const.VTX_3D_POLYGON_MESH_VERTEX + const.VTX_3D_POLYFACE_MESH_VERTEX
    TEMPLATE = ClassifiedTags.from_text(_VERTEX_TPL)
    DXFATTRIBS = make_attribs({
        'location': DXFAttr(10, xtype='Point2D/3D'),
        'start_width': DXFAttr(40, default=0.0),
        'end_width': DXFAttr(41, default=0.0),
        'bulge': DXFAttr(42, default=0),
        'flags': DXFAttr(70, default=0),
        'tangent': DXFAttr(50),
        'vtx0': DXFAttr(71),
        'vtx1': DXFAttr(72),
        'vtx2': DXFAttr(73),
        'vtx3': DXFAttr(74),
    })

    @property
    def is_2d_polyline_vertex(self):
        return self.dxf.flags & Vertex.VTX3D == 0

    @property
    def is_3d_polyline_vertex(self):
        return self.dxf.flags & const.VTX_3D_POLYLINE_VERTEX

    @property
    def is_polygon_mesh_vertex(self):
        return self.dxf.flags & const.VTX_3D_POLYGON_MESH_VERTEX

    @property
    def is_poly_face_mesh_vertex(self):
        return self.dxf.flags & Vertex.FACE_FLAGS == Vertex.FACE_FLAGS

    @property
    def is_face_record(self):
        return (self.dxf.flags & Vertex.FACE_FLAGS) == const.VTX_3D_POLYFACE_MESH_VERTEX

_VPORT_TPL = """  0
VIEWPORT
  5
0
 10
0.0
 20
0.0
 30
0.0
 40
1.0
 41
1.0
 68
 1
1001
ACAD
1000
MVIEW
1002
{
1070
16
1002
{
1002
{
1002
{
"""


class Viewport(GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_VPORT_TPL)
    DXFATTRIBS = make_attribs({
        'center': DXFAttr(10, xtype='Point2D/3D'),  # center point of entity in paper space coordinates)
        'width': DXFAttr(40),  # width in paper space units
        'height': DXFAttr(41),  # height in paper space units
        'status': DXFAttr(68),
        'id': DXFAttr(69),
    })

_DIMENSION_TPL = """  0
DIMENSION
  5
0
  2
*BLOCKNAME
  3
DIMSTYLE
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
 70
0
  1

 13
0.0
 23
0.0
 33
0.0
 14
0.0
 24
0.0
 34
0.0
 15
0.0
 25
0.0
 35
0.0
 16
0.0
 26
0.0
 36
0.0
 40
1.0
 50
0.0
"""


class Dimension(GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_DIMENSION_TPL)
    DXFATTRIBS = make_attribs({
        'geometry': DXFAttr(2),  # name of pseudo-Block containing the current dimension  entity geometry
        'dimstyle': DXFAttr(3),
        'defpoint1': DXFAttr(10, xtype='Point2D/3D'),
        'midpoint': DXFAttr(11, xtype='Point2D/3D'),
        'translation_vector': DXFAttr(12, 'Point3D'),
        'dimtype': DXFAttr(70),
        'user_text': DXFAttr(1),
        'defpoint2': DXFAttr(13, xtype='Point2D/3D'),
        'defpoint3': DXFAttr(14, xtype='Point2D/3D'),
        'defpoint4': DXFAttr(15, xtype='Point2D/3D'),
        'defpoint5': DXFAttr(16, xtype='Point2D/3D'),
        'leader_length': DXFAttr(40),
        'angle': DXFAttr(50),
        'horizontal_direction': DXFAttr(51),
        'oblique_angle': DXFAttr(52),
        'rotation_angle': DXFAttr(53),
    })

_SHAPE_TPL = """  0
SHAPE
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


# SHAPE is not tested with real world DXF drawings!
class Shape(GraphicEntity, ColorMixin):
    TEMPLATE = ClassifiedTags.from_text(_SHAPE_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'size': DXFAttr(40),
        'name': DXFAttr(2),
        'rotation': DXFAttr(50, default=0.0),
        'xscale': DXFAttr(41, default=1.0),
        'oblique': DXFAttr(51, default=0.0),
    })
