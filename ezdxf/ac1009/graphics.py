#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: DXF 12 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import DXFAttr
from ..entity import GenericWrapper, ExtendedType

class GraphicEntity(GenericWrapper):
    pass

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
        if num in (0, 1, 2, 3):
            tags = self._get_subtags()
            return tags._get_value(10+num, 'Point2D/3D')
        else:
            raise IndexError(num)

    def __setitem__(self, num, value):
        if num in (0, 1, 2, 3):
            tags = self._get_subtags()
            return tags._set_value(10+num, 'Point2D/3D', value)
        else:
            raise IndexError(num)

    def _get_subtags(self):
        return ExtendedType(self.tags)

def make_AC1009_attribs(additional={}):
    attribs = {
        'handle': DXFAttr(5, None, None),
        'layer': DXFAttr(8, None, None), # layername as string, default is '0'
        'linetype': DXFAttr(6, None, None), # linetype as string, special names BYLAYER/BYBLOCK, default is BYLAYER
        'color': DXFAttr(62, None, None), # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER, default is 256
        'paperspace': DXFAttr(67, None, None), # 0 .. modelspace, 1 .. paperspace, default is 0
        'extrusion': DXFAttr(210, None, 'Point3D'), # never used !?
    }
    attribs.update(additional)
    return attribs

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
    DXFATTRIBS = make_AC1009_attribs()

_SOLID_TPL = _TRACE_TPL.replace('TRACE', 'SOLID')

class AC1009Solid(AC1009Trace):
    TEMPLATE = _SOLID_TPL

_3DFACE_TPL = _TRACE_TPL.replace('TRACE', '3DFACE')

class AC10093DFace(AC1009Trace):
    TEMPLATE = _3DFACE_TPL

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
        'insert': DXFAttr(10, None, 'Point2D/3D'),
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
 66
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

class AC1009SeqEnd(GraphicEntity):
    TEMPLATE = "  0\nSEQEND\n  5\n0\n"
    DXFATTRIBS = { 'handle': DXFAttr(5, None, None) }

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
 70
0
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
    MCLOSED = 1
    POLYLINE3D = 8
    POLYMESH = 16
    NCLOSED = 32
    POLYFACE = 64

    def setbuilder(self, builder):
        self._builder = builder

    def setmode(self, mode):
        if mode == 'polyline3d':
            self.flags = self.flags | self.POLYLINE3D
        elif mode == 'polymesh':
            self.flags = self.flags | self.POLYMESH
        elif mode == 'polyface':
            self.flags = self.flags | self.POLYFACE
        else:
            raise ValueError(mode)

    def getmode(self):
        flags = self.flags
        if flags & self.POLYLINE3D > 0:
            return 'polyline3d'
        elif flags & self.POLYMESH > 0:
            return 'polymesh'
        elif flags & self.POLYFACE > 0:
            return 'polyface'
        else:
            return 'polyline2d'

    def mclose(self):
        self.flags = self.flags | self.MCLOSED
    def nclose(self):
        self.flags = self.flags | self.NCLOSED

    def close(self, mclose, nclose=False):
        if mclose:
            self.mclose()
        if nclose:
            self.nclose()

    def __len__(self):
        return self._getendpos() - self._getstartpos() - 1

    def __iter__(self):
        """ Iterate over all vertices. """
        index = self._getstartpos() + 1
        while True:
            entity = self._builder._get_entity(index)
            if entiy.dxftype == 'VERTEX':
                yield entity
            index += 1

    def __getitem__(self, pos):
        return self._builder._get_entity(self._getstartpos() + pos + 1)

    def append_vertices(self, points, attribs={}):
        index = self._getendpos()
        self.insert_vertices(index, points, attribs)

    def insert_vertices(self, pos, points, attribs={}):
        index = self._getstartpos() + pos + 1
        for point in points:
            newattr = dict(attribs)
            newattr['location'] = point
            vertex = self._builder._build_entity('VERTEX', newattr)
            self.builder._insert_entity(index, vertex)
            index += 1

    def delete_vertices(self, pos, count=1):
        index = self._getstartpos() + pos + 1
        for x in range(count):
            self.builder._remove_entity(index + x)

    def _getendpos(self):
        # position can not be cached, because insertion and deletion in
        # entity-space, can change the polyline position
        pos = self._getstartpos()
        while True:
            pos += 1
            entity = self._builder._get_entity(pos)
            if entity.dxftype == 'SEQEND':
                return pos

    def _getstartpos(self):
        # position can not be cached, because insertion and deletion in
        # entity-space, can change the polyline position
        return self.builder._get_position(self)

    def cast(self):
        mode = self.getmode()
        if mode == 'polyface':
            return AC1009Polyface(self)
        elif mode == 'polymesh':
            return AC1009Polymesh(self)
        else:
            return self

class AC1009Polyface(AC1009Polyline):
    def __init__(self, polyline):
        self.setbuilder(polyline._builder)
        self.tags = polyline.tags

    def append_face(self, face, attribs={}):
        raise NotImplementedError

    def faces(self):
        """ Iterate over all faces. """
        raise NotImplementedError

class AC1009Polymesh(AC1009Polyline):
    def __init__(self, polyline):
        self.setbuilder(polyline._builder)
        self.tags = polyline.tags

    def set_vertex(self, mnpos, point, attribs={}):
        raise NotImplementedError

    def get_vertex(self, mnpos):
        raise NotImplementedError

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
class AC1009Vertex(GraphicEntity, ColorMixin):
    TEMPLATE = _VERTEX_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'location': DXFAttr(10, None, 'Point2D/3D'),
        'startwidth': DXFAttr(40, None, None),
        'endwidth': DXFAttr(41, None, None),
        'bulge': DXFAttr(42, None, None),
        'flags': DXFAttr(70, None, None),
        'tangent': DXFAttr(50, None, None),
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
