# Purpose: DXF 12 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..tags import DXFStructureError
from ..classifiedtags import ClassifiedTags
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass
from ..entity import GenericWrapper
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
        'handle': DXFAttr(5, None),
        'layer': DXFAttr(8, None),  # layername as string, default is '0'
        'linetype': DXFAttr(6, None),  # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
        'color': DXFAttr(62, None),  # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
        'paperspace': DXFAttr(67, None),  # 0 .. modelspace, 1 .. paperspace, default is 0
        'extrusion': DXFAttr(210, 'Point3D'),  # Z-axis of OCS (Object-Coordinate-System)
    }
    if additional is not None:
        dxfattribs.update(additional)
    return DXFAttributes(DefSubclass(None, dxfattribs))


class GraphicEntity(GenericWrapper):
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

    def set_layout(self, layout):
        self.layout = layout

    @property
    def dxffactory(self):
        return self.layout._dxffactory

    @property
    def drawing(self):
        return self.layout._dxffactory.drawing

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
        'start': DXFAttr(10, 'Point2D/3D'),
        'end': DXFAttr(11, 'Point2D/3D'),
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
        'location': DXFAttr(10, 'Point2D/3D'),
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
        'center': DXFAttr(10, 'Point2D/3D'),
        'radius': DXFAttr(40, None),
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
        'center': DXFAttr(10, 'Point2D/3D'),
        'radius': DXFAttr(40, None),
        'start_angle': DXFAttr(50, None),
        'end_angle': DXFAttr(51, None),
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
        'vtx0': DXFAttr(10, 'Point2D/3D'),
        'vtx1': DXFAttr(11, 'Point2D/3D'),
        'vtx2': DXFAttr(12, 'Point2D/3D'),
        'vtx3': DXFAttr(13, 'Point2D/3D'),
    })


class Solid(Trace):
    TEMPLATE = ClassifiedTags.from_text(_TRACE_TPL.replace('TRACE', 'SOLID'))


class Face(Trace):
    TEMPLATE = ClassifiedTags.from_text(_TRACE_TPL.replace('TRACE', '3DFACE'))
    DXFATTRIBS = make_attribs({
        'vtx0': DXFAttr(10, 'Point2D/3D'),
        'vtx1': DXFAttr(11, 'Point2D/3D'),
        'vtx2': DXFAttr(12, 'Point2D/3D'),
        'vtx3': DXFAttr(13, 'Point2D/3D'),
        'invisible_edge': DXFAttr(70, None),
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
        'insert': DXFAttr(10, 'Point2D/3D'),
        'height': DXFAttr(40,  None),
        'text': DXFAttr(1,  None),
        'rotation': DXFAttr(50, None),  # in degrees (circle = 360deg)
        'oblique': DXFAttr(51, None),  # in degrees, vertical = 0deg
        'style': DXFAttr(7, None),  # text style
        'width': DXFAttr(41, None),  # width FACTOR!
        'text_generation_flag': DXFAttr(71, None),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, None),  # horizontal justification
        'valign': DXFAttr(73,  None),  # vertical justification
        'align_point': DXFAttr(11, 'Point2D/3D'),
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
        p2 = self.dxf.alignpoint
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
        halign = self.get_dxf_attrib('halign')
        valign = self.get_dxf_attrib('valign')
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
        'name': DXFAttr(2, None),
        'name2': DXFAttr(3, None),
        'flags': DXFAttr(70, None),
        'base_point': DXFAttr(10, 'Point2D/3D'),
        'xref_path': DXFAttr(1, None),
    })


class EndBlk(GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text("  0\nENDBLK\n  5\n0\n")
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {'handle': DXFAttr(5, None)}))

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
    })

    def __iter__(self):
        def get_entity(index):
            try:
                return self.layout.get_entity_at_index(index)
            except IndexError:
                raise DXFStructureError('expected following ATTRIB or SEQEND, reached end of layout instead.')

        if self.dxf.attribs_follow == 0:
            return
        index = self.layout.get_index_of_entity(self) + 1
        while True:
            entity = get_entity(index)
            dxftype = entity.dxftype()
            if dxftype == 'ATTRIB':
                yield entity
                index += 1
            elif dxftype == 'SEQEND':
                return
            else:
                raise DXFStructureError('expected following ATTRIB or SEQEND, got instead %s.' % dxftype)

    def get_attrib(self, tag):
        for attrib in self:
            if tag == attrib.dxf.tag:
                return attrib
        return None

    def add_attrib(self, tag, text, insert, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['tag'] = tag
        dxfattribs['text'] = text
        dxfattribs['insert'] = insert
        attrib_entity = self.layout.build_entity('ATTRIB', dxfattribs)
        self._append_attrib_entity(attrib_entity)

    def _append_attrib_entity(self, entity):
        def find_seqend(pos):
            while True:
                try:
                    entity = self.layout.get_entity_at_index(pos)
                except IndexError:
                    return -1
                dxftype = entity.dxftype()
                if dxftype == 'ATTRIB':
                    pos += 1
                elif dxftype == 'SEQEND':
                    return pos
                else:
                    return -1

        entities = [entity]
        position = self.layout.get_index_of_entity(self) + 1
        seqend_position = find_seqend(position)
        if seqend_position < 0:
            entities.append(self.layout.build_entity('SEQEND', {}))
            seqend_position = position
        self.dxf.attribs_follow = 1
        self.layout.insert_entities(seqend_position, entities)


class SeqEnd(GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text("  0\nSEQEND\n  5\n0\n")
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5, None),
        'paperspace': DXFAttr(67, None),
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


class Attdef(GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_ATTDEF_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, 'Point2D/3D'),
        'height': DXFAttr(40, None),
        'text': DXFAttr(1, None),
        'prompt': DXFAttr(3, None),
        'tag': DXFAttr(2, None),
        'flags': DXFAttr(70, None),
        'field_length': DXFAttr(73, None),
        'rotation': DXFAttr(50, None),
        'oblique': DXFAttr(51, None),
        'width': DXFAttr(41, None),  # width factor
        'style': DXFAttr(7, None),
        'text_generation_flag': DXFAttr(71, None),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, None),  # horizontal justification
        'valign': DXFAttr(74, None),  # vertical justification
        'align_point': DXFAttr(11, 'Point2D/3D'),
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


class Attrib(GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_ATTRIB_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, 'Point2D/3D'),
        'height': DXFAttr(40, None),
        'text': DXFAttr(1, None),
        'tag': DXFAttr(2, None),
        'flags': DXFAttr(70, None),
        'field_length': DXFAttr(73, None),
        'rotation': DXFAttr(50, None),
        'oblique': DXFAttr(51, None),
        'width': DXFAttr(41, None),  # width factor
        'style': DXFAttr(7, None),
        'text_generation_flag': DXFAttr(71, None),  # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, None),  # horizontal justification
        'valign': DXFAttr(74, None),  # vertical justification
        'align_point': DXFAttr(11, 'Point2D/3D'),
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
    TEMPLATE = ClassifiedTags.from_text(_POLYLINE_TPL)
    DXFATTRIBS = make_attribs({
        'elevation': DXFAttr(10, 'Point2D/3D'),
        'flags': DXFAttr(70, None),
        'default_start_width': DXFAttr(40, None),
        'default_end_width': DXFAttr(41, None),
        'm_count': DXFAttr(71, None),
        'n_count': DXFAttr(72, None),
        'm_smooth_density': DXFAttr(73, None),
        'n_smooth_density': DXFAttr(74, None),
        'smooth_type': DXFAttr(75, None),
    })

    def get_vertex_flags(self):
        return const.VERTEX_FLAGS[self.get_mode()]

    def get_mode(self):
        flags = self.dxf.flags
        if flags & const.POLYLINE_3D_POLYLINE > 0:
            return 'polyline3d'
        elif flags & const.POLYLINE_3D_POLYMESH > 0:
            return 'polymesh'
        elif flags & const.POLYLINE_POLYFACE > 0:
            return 'polyface'
        else:
            return 'polyline2d'

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
        return len(list(iter(self)))

    def __iter__(self):
        """ Iterate over all vertices. """
        index = self.layout.get_index_of_entity(self) + 1
        entity = self.layout.get_entity_at_index(index)
        while entity.dxftype() != 'SEQEND':
            yield entity
            index += 1
            entity = self.layout.get_entity_at_index(index)

    def __getitem__(self, pos):
        return list(self)[pos]

    def points(self):
        return (vertex.dxf.location for vertex in self)

    def append_vertices(self, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        if len(points) > 0:
            first_vertex_index, last_vertex_index = self._get_index_range()
            self._insert_vertices(last_vertex_index + 1, points, dxfattribs)

    def insert_vertices(self, pos, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        if len(points) > 0:
            first_vertex_index, last_vertex_index = self._get_index_range()
            self._insert_vertices(first_vertex_index + pos, points, dxfattribs)

    def _insert_vertices(self, index, points, dxfattribs):
        vertices = self._points_to_vertices(points, dxfattribs)
        self.layout.insert_entities(index, vertices)

    def _points_to_vertices(self, points, dxfattribs):
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | self.get_vertex_flags()
        vertices = []
        for point in points:
            dxfattribs['location'] = point
            vertices.append(self.layout.build_entity('VERTEX', dxfattribs))
        return vertices

    def delete_vertices(self, pos, count=1):
        index = self._pos_to_index_with_range_check(pos, count)
        self.layout.remove_entities(index, count)

    def _pos_to_index_with_range_check(self, pos, count=1):
        first_vertex_index, last_vertex_index = self._get_index_range()
        length = last_vertex_index - first_vertex_index + 1
        if pos < 0:
            pos += length
        if 0 <= pos and (pos + count - 1) < length:
            return first_vertex_index + pos
        else:
            raise IndexError(repr((pos, count)))

    def _get_index_range(self):
        first_vertex_index = self.layout.get_index_of_entity(self) + 1
        last_vertex_index = first_vertex_index
        while True:
            entity = self.layout.get_entity_at_index(last_vertex_index)
            if entity.dxftype() == 'SEQEND':
                return first_vertex_index, last_vertex_index - 1
            last_vertex_index += 1

    def cast(self):
        mode = self.get_mode()
        if mode == 'polyface':
            return Polyface.convert(self)
        elif mode == 'polymesh':
            return Polymesh.convert(self)
        else:
            return self

    def _get_vertex_at_trusted_position(self, pos):
        # does no index check - for meshes and faces
        index = self.layout.get_index_of_entity(self) + 1 + pos
        return self.layout.get_entity_at_index(index)


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
    TEMPLATE = ClassifiedTags.from_text(_VERTEX_TPL)
    DXFATTRIBS = make_attribs({
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
        'center': DXFAttr(10, 'Point2D/3D'),
        # center point of entity in paper space coordinates)
        'width': DXFAttr(40, None),
        # width in paper space units
        'height': DXFAttr(41, None),
        # height in paper space units
        'status': DXFAttr(68, None),
        'id': DXFAttr(69, None),
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
        'geometry': DXFAttr(2, None),
        # name of pseudo-Block containing the current dimension  entity geometry
        'dimstyle': DXFAttr(3, None),
        'defpoint1': DXFAttr(10, 'Point2D/3D'),
        'midpoint': DXFAttr(11, 'Point2D/3D'),
        'translationvector': DXFAttr(12, 'Point3D'),
        'dimtype': DXFAttr(70, None),
        'usertext': DXFAttr(1, None),
        'defpoint2': DXFAttr(13, 'Point2D/3D'),
        'defpoint3': DXFAttr(14, 'Point2D/3D'),
        'defpoint4': DXFAttr(15, 'Point2D/3D'),
        'defpoint5': DXFAttr(16, 'Point2D/3D'),
        'leaderlength': DXFAttr(40, None),
        'angle': DXFAttr(50, None),
    })
