#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: DXF 12 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import DXFAttr, DXFStructureError
from ..entity import GenericWrapper, ExtendedType
from .. import const
from ..const import VERTEXNAMES
from .optfacebuilder import OptimizingFaceBuilder

class GraphicEntity(GenericWrapper):
    def set_builder(self, builder):
        self._builder = builder # IGraphicBuilder

class ColorMixin:
    def set_extcolor(self, color):
        """ Set color by color-name or rgb-tuple, for DXF R12 the nearest
        default DXF color index will be determined.
        """
        pass

    def get_rgbcolor(self):
        return (0, 0, 0)

    def get_colorname(self):
        return 'Black'

class QuadrilateralMixin:
    def __getitem__(self, num):
        return self.get_dxf_attrib(VERTEXNAMES[num])

    def __setitem__(self, num, value):
        return self.set_dxf_attrib(VERTEXNAMES[num], value)

def make_AC1009_attribs(additional={}):
    dxfattribs = {
        'handle': DXFAttr(5, None, None),
        'layer': DXFAttr(8, None, None), # layername as string, default is '0'
        'linetype': DXFAttr(6, None, None), # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
        'color': DXFAttr(62, None, None), # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
        'paperspace': DXFAttr(67, None, None), # 0 .. modelspace, 1 .. paperspace, default is 0
        'extrusion': DXFAttr(210, None, 'Point3D'), # never used !?
    }
    dxfattribs.update(additional)
    return dxfattribs

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

class AC1009Line(GraphicEntity, ColorMixin):
    TEMPLATE = _LINE_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'start': DXFAttr(10, None, 'Point2D/3D'),
        'end': DXFAttr(11, None, 'Point2D/3D'),
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

class AC1009Point(GraphicEntity, ColorMixin):
    TEMPLATE = _POINT_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'point': DXFAttr(10, None, 'Point2D/3D'),
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

class AC1009Circle(GraphicEntity, ColorMixin):
    TEMPLATE = _CIRCLE_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'center': DXFAttr(10, None, 'Point2D/3D'),
        'radius': DXFAttr(40, None, None),
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

class AC1009Arc(GraphicEntity, ColorMixin):
    TEMPLATE = _ARC_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'center': DXFAttr(10, None, 'Point2D/3D'),
        'radius': DXFAttr(40, None, None),
        'startangle': DXFAttr(50, None, None),
        'endangle': DXFAttr(51, None, None),
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

class AC1009Trace(GraphicEntity, ColorMixin, QuadrilateralMixin):
    TEMPLATE = _TRACE_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'vtx0' : DXFAttr(10, None, 'Point2D/3D'),
        'vtx1' : DXFAttr(11, None, 'Point2D/3D'),
        'vtx2' : DXFAttr(12, None, 'Point2D/3D'),
        'vtx3' : DXFAttr(13, None, 'Point2D/3D'),
    })

class AC1009Solid(AC1009Trace):
    TEMPLATE = _TRACE_TPL.replace('TRACE', 'SOLID')

class AC10093DFace(AC1009Trace):
    TEMPLATE = _TRACE_TPL.replace('TRACE', '3DFACE')
    DXFATTRIBS = make_AC1009_attribs({
        'vtx0' : DXFAttr(10, None, 'Point2D/3D'),
        'vtx1' : DXFAttr(11, None, 'Point2D/3D'),
        'vtx2' : DXFAttr(12, None, 'Point2D/3D'),
        'vtx3' : DXFAttr(13, None, 'Point2D/3D'),
        'invisible_edge': DXFAttr(70, None, None),
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

class AC1009Text(GraphicEntity, ColorMixin):
    TEMPLATE = _TEXT_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'insert': DXFAttr(10, None, 'Point2D/3D'),
        'height': DXFAttr(40, None, None),
        'text': DXFAttr(1, None, None),
        'rotation': DXFAttr(50, None, None), # in degrees (circle = 360deg)
        'oblique': DXFAttr(51, None, None), # in degrees, vertical = 0deg
        'style': DXFAttr(7, None, None), # text style
        'width': DXFAttr(41, None, None), # width FACTOR!
        'textgenerationflag': DXFAttr(71, None, None), # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, None, None), # horizontal justification
        'valign': DXFAttr(73, None, None), # vertical justification
        'alignpoint': DXFAttr(11, None, 'Point2D/3D'),
    })

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
class AC1009Block(GraphicEntity):
    TEMPLATE = _BLOCK_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'name': DXFAttr(2, None, None),
        'name2': DXFAttr(3, None, None),
        'flags': DXFAttr(70, None, None),
        'basepoint': DXFAttr(10, None, 'Point2D/3D'),
        'xrefpath': DXFAttr(1, None, None),
    })


class AC1009EndBlk(GraphicEntity):
    TEMPLATE = "  0\nENDBLK\n  5\n0\n"
    DXFATTRIBS = { 'handle': DXFAttr(5, None, None) }

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
# attribsfollow = 0, for NO attribsfollow does not work with ACAD 2010
# if no attribs attached to the INSERT entity, omit attribsfollow tag
class AC1009Insert(GraphicEntity):
    TEMPLATE = _INSERT_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'attribsfollow': DXFAttr(66, None, None),
        'name': DXFAttr(2, None, None),
        'insert': DXFAttr(10, None, 'Point2D/3D'),
        'xscale': DXFAttr(41, None, None),
        'yscale': DXFAttr(42, None, None),
        'zscale': DXFAttr(43, None, None),
        'rotation': DXFAttr(50, None, None),
        'colcount': DXFAttr(70, None, None),
        'rowcount': DXFAttr(71, None, None),
        'colspacing': DXFAttr(44, None, None),
        'rowspacing': DXFAttr(45, None, None),
    })

    def __iter__(self):
        def get_entity(index):
            try:
                return self._builder._get_entity_at_index(index)
            except IndexError:
                raise DXFStructureError('expected following ATTRIB or SEQEND, reached end of layout instead.')

        if self.dxf.attribsfollow == 0:
            return
        index = self._builder._get_index(self) + 1
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

    def add_attrib(self, tag, text, insert, dxfattribs={}):
        dxfattribs['tag'] = tag
        dxfattribs['text'] = text
        dxfattribs['insert'] = insert
        attrib_entity = self._builder._build_entity('ATTRIB', dxfattribs)
        self._append_attrib_entity(attrib_entity)

    def _append_attrib_entity(self, entity):
        def find_seqend(pos):
            while True:
                try:
                    entity = self._builder._get_entity_at_index(pos)
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
        position = self._builder._get_index(self) + 1
        seqend_position = find_seqend(position)
        if seqend_position < 0:
            entities.append(self._builder._build_entity('SEQEND', {}))
            seqend_position = position
        self.dxf.attribsfollow = 1
        self._builder._insert_entities(seqend_position, entities)

class AC1009SeqEnd(GraphicEntity):
    TEMPLATE = "  0\nSEQEND\n  5\n0\n"
    DXFATTRIBS = { 'handle': DXFAttr(5, None, None),
                   'paperspace': DXFAttr(67, None, None),}

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
class AC1009Attdef(GraphicEntity):
    TEMPLATE = _ATTDEF_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'insert': DXFAttr(10, None, 'Point2D/3D'),
        'height': DXFAttr(40, None, None),
        'text': DXFAttr(1, None, None),
        'prompt': DXFAttr(3, None, None),
        'tag': DXFAttr(2, None, None),
        'flags': DXFAttr(70, None, None),
        'fieldlength': DXFAttr(73, None, None),
        'rotation': DXFAttr(50, None, None),
        'oblique': DXFAttr(51, None, None),
        'width': DXFAttr(41, None, None), # width factor
        'style': DXFAttr(7, None, None),
        'textgenerationflag': DXFAttr(71, None, None), # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, None, None), # horizontal justification
        'valign': DXFAttr(74, None, None), # vertical justification
        'alignpoint': DXFAttr(11, None, 'Point2D/3D'),
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
class AC1009Attrib(GraphicEntity):
    TEMPLATE = _ATTRIB_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'insert': DXFAttr(10, None, 'Point2D/3D'),
        'height': DXFAttr(40, None, None),
        'text': DXFAttr(1, None, None),
        'tag': DXFAttr(2, None, None),
        'flags': DXFAttr(70, None, None),
        'fieldlength': DXFAttr(73, None, None),
        'rotation': DXFAttr(50, None, None),
        'oblique': DXFAttr(51, None, None),
        'width': DXFAttr(41, None, None), # width factor
        'style': DXFAttr(7, None, None),
        'textgenerationflag': DXFAttr(71, None, None), # 2 = backward (mirr-x), 4 = upside down (mirr-y)
        'halign': DXFAttr(72, None, None), # horizontal justification
        'valign': DXFAttr(74, None, None), # vertical justification
        'alignpoint': DXFAttr(11, None, 'Point2D/3D'),
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
class AC1009Polyline(GraphicEntity, ColorMixin):
    TEMPLATE = _POLYLINE_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'elevation': DXFAttr(10, None, 'Point2D/3D'),
        'flags': DXFAttr(70, None, None),
        'defaultstartwidth': DXFAttr(40, None, None),
        'defaultendwidth': DXFAttr(41, None, None),
        'mcount': DXFAttr(71, None, None),
        'ncount': DXFAttr(72, None, None),
        'msmoothdensity': DXFAttr(73, None, None),
        'nsmoothdensity': DXFAttr(74, None, None),
        'smoothtype': DXFAttr(75, None, None),
    })

    def get_vertex_flags(self):
        return const.VERTEX_FLAGS[self.getmode()]

    def getmode(self):
        flags = self.dxf.flags
        if flags & const.POLYLINE_3D_POLYLINE > 0:
            return 'polyline3d'
        elif flags & const.POLYLINE_3D_POLYMESH > 0:
            return 'polymesh'
        elif flags & const.POLYLINE_POLYFACE > 0:
            return 'polyface'
        else:
            return 'polyline2d'

    def mclose(self):
        self.flags = self.flags | const.POLYLINE_MESH_CLOSED_M_DIRECTION
    def nclose(self):
        self.flags = self.flags | const.POLYLINE_MESH_CLOSED_N_DIRECTION

    def close(self, mclose, nclose=False):
        if mclose:
            self.mclose()
        if nclose:
            self.nclose()

    def __len__(self):
        return len(list(iter(self)))

    def __iter__(self):
        """ Iterate over all vertices. """
        index = self._builder._get_index(self) + 1
        entity = self._builder._get_entity_at_index(index)
        while entity.dxftype() != 'SEQEND':
            yield entity
            index += 1
            entity = self._builder._get_entity_at_index(index)

    def __getitem__(self, pos):
        return list(iter(self)).__getitem__(pos)

    @property
    def points(self):
        return [vertex.dxf.location for vertex in self]

    def append_vertices(self, points, dxfattribs={}):
        if len(points) > 0:
            first_vertex_index, last_vertex_index = self._get_index_range()
            self._insert_vertices(last_vertex_index+1, points, dxfattribs)

    def insert_vertices(self, pos, points, dxfattribs={}):
        if len(points) > 0:
            first_vertex_index, last_vertex_index = self._get_index_range()
            self._insert_vertices(first_vertex_index+pos, points, dxfattribs)

    def _insert_vertices(self, index, points, dxfattribs):
        vertices = self._points_to_vertices(points, dxfattribs)
        self._builder._insert_entities(index, vertices)

    def _points_to_vertices(self, points, dxfattribs):
        dxfattribs['flags'] =  dxfattribs.get('flags', 0) | self.get_vertex_flags()
        vertices = []
        for point in points:
            dxfattribs['location'] = point
            vertices.append(self._builder._build_entity('VERTEX', dxfattribs))
        return vertices

    def delete_vertices(self, pos, count=1):
        index = self._pos_to_index_with_range_check(pos, count)
        self._builder._remove_entities(index, count)

    def _pos_to_index_with_range_check(self, pos, count=1):
        first_vertex_index, last_vertex_index = self._get_index_range()
        length = last_vertex_index - first_vertex_index + 1
        if pos < 0:
            pos = length + pos
        if 0 <= pos and pos+count-1 < length:
            return first_vertex_index + pos
        else:
            raise IndexError(repr((pos, count)))

    def _get_index_range(self):
        first_vertex_index = self._builder._get_index(self) + 1
        last_vertex_index = first_vertex_index
        while True:
            entity = self._builder._get_entity_at_index(last_vertex_index)
            if entity.dxftype() == 'SEQEND':
                return (first_vertex_index, last_vertex_index-1)
            last_vertex_index += 1

    def cast(self):
        mode = self.getmode()
        if mode == 'polyface':
            return AC1009Polyface.convert(self)
        elif mode == 'polymesh':
            return AC1009Polymesh.convert(self)
        else:
            return self

    def _get_vertex_at_trusted_position(self, pos):
        # performs not index check - for meshes and faces
        index = self._builder._get_index(self) + 1 + pos
        return self._builder._get_entity_at_index(index)

class AC1009Polyface(AC1009Polyline):
    """ Order of vertices and faces IS important (ACAD2010)
    1. vertices (describes the coordinates)
    2. faces (describes the face forming vertices)

    """
    @staticmethod
    def convert(polyline):
        face = AC1009Polyface(polyline.tags)
        face.set_builder(polyline._builder)
        return face

    def append_face(self, face, dxfattribs={}):
        self.append_faces([face], dxfattribs)

    def append_faces(self, faces, dxfattribs={}):
        def facevertex():
            vertex = self._builder._build_entity('VERTEX', dxfattribs)
            vertex.dxf.flags = const.VTX_3D_POLYFACE_MESH_VERTEX
            return vertex

        existing_faces = list(self.faces())
        for face in faces:
            vertices = self._points_to_vertices(face, {})
            vertices.append(facevertex())
            existing_faces.append(vertices)
        self._generate(existing_faces)

    def _generate(self, faces):
        def remove_all_vertices():
            startindex, endindex = self._get_index_range()
            if startindex <= endindex:
                self._builder._remove_entities(startindex, (endindex - startindex) + 1)

        def insert_new_vertices(vertices):
            index = self._builder._get_index(self) + 1
            self._builder._insert_entities(index, vertices)

        facebuilder = OptimizingFaceBuilder(faces)
        remove_all_vertices()
        insert_new_vertices(facebuilder.get_vertices())
        self.update_count(facebuilder.nvertices, facebuilder.nfaces)

    def update_count(self, nvertices, nfaces):
        self.dxf.mcount = nvertices
        self.dxf.ncount = nfaces

    def faces(self):
        """ Iterate over all faces, a face is a tuple of vertices.
        result: [vertex, vertex, ..., face-vertex]
        """
        def isface(vertex):
            flags = vertex.dxf.flags
            if flags & const.VTX_3D_POLYFACE_MESH_VERTEX > 0 and \
               flags & const.VTX_3D_POLYGON_MESH_VERTEX == 0:
                return True
            else:
                return False

        def getface(vertex):
            face = []
            for vtx in VERTEXNAMES:
                index = vertex.get_dxf_attrib(vtx, 0)
                if index != 0:
                    index = abs(index) - 1
                    face.append(vertices[index])
                else:
                    break
            face.append(vertex)
            return face

        vertices = list(iter(self))
        for vertex in vertices:
            if isface(vertex):
                yield getface(vertex)

class AC1009Polymesh(AC1009Polyline):
    @staticmethod
    def convert(polyline):
        mesh = AC1009Polymesh(polyline.tags)
        mesh.set_builder(polyline._builder)
        return mesh

    def set_mesh_vertex(self, pos, point, dxfattribs={}):
        dxfattribs['location'] = point
        vertex = self.get_mesh_vertex(pos)
        vertex.update_dxf_attribs(dxfattribs)

    def get_mesh_vertex(self, pos):
        mcount = self.dxf.mcount
        ncount = self.dxf.ncount
        m, n = pos
        if 0 <= m < mcount and 0 <= n < ncount:
            pos = m * ncount + n
            return self._get_vertex_at_trusted_position(pos)
        else:
            raise IndexError(repr(pos))

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
class AC1009Vertex(GraphicEntity, ColorMixin, QuadrilateralMixin):
    TEMPLATE = _VERTEX_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'location': DXFAttr(10, None, 'Point2D/3D'),
        'startwidth': DXFAttr(40, None, None),
        'endwidth': DXFAttr(41, None, None),
        'bulge': DXFAttr(42, None, None),
        'flags': DXFAttr(70, None, None),
        'tangent': DXFAttr(50, None, None),
        'vtx0': DXFAttr(71, None, None),
        'vtx1': DXFAttr(72, None, None),
        'vtx2': DXFAttr(73, None, None),
        'vtx3': DXFAttr(74, None, None),
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
class AC1009Viewport(GraphicEntity):
    TEMPLATE = _VPORT_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'center': DXFAttr(10, None, 'Point2D/3D'),
        # center point of entity in paper space coordinates)
        'width': DXFAttr(40, None, None),
        # width in paper space units
        'height': DXFAttr(41, None, None),
        # height in paper space units
        'status': DXFAttr(68, None, None),
        'id': DXFAttr(69, None, None),
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
class AC1009Dimension(GraphicEntity):
    TEMPLATE = _DIMENSION_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'geometry': DXFAttr(2, None, None),
        # name of pseudo-Block containing the current dimension  entity geometry
        'dimstyle': DXFAttr(3, None, None),
        'defpoint1': DXFAttr(10, None, 'Point2D/3D'),
        'midpoint': DXFAttr(11, None, 'Point2D/3D'),
        'translationvector': DXFAttr(12, None, 'Point3D'),
        'dimtype': DXFAttr(70, None, None),
        'usertext': DXFAttr(1, None, None),
        'defpoint2': DXFAttr(13, None, 'Point2D/3D'),
        'defpoint3': DXFAttr(14, None, 'Point2D/3D'),
        'defpoint4': DXFAttr(15, None, 'Point2D/3D'),
        'defpoint5': DXFAttr(16, None, 'Point2D/3D'),
        'leaderlength': DXFAttr(40, None, None),
        'angle': DXFAttr(50, None, None),
    })
