#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: DXF 12 graphics entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import DXFAttr
from ..entity import GenericWrapper, ExtendedType

class AC1009GraphicBuilder:
    def add_line(self, start, end, attribs={}):
        def update_attribs():
            self._set_paper_space(attribs)
            attribs['start'] = start
            attribs['end'] = end

        update_attribs()
        entity = self._build_entity('LINE', attribs)
        self._add_entity(entity)
        return entity

    def _build_entity(self, type_, attribs):
        pass # abstract method

    def _add_entity(self, entity):
        pass # abstract method

    def _set_paper_space(self, attribs):
        pass # abstract method

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

class FourPointsMixin:
    def __getitem__(self, num):
        if num in (0, 1, 2, 3):
            tags = ExtendedType(self.tags)
            return self._get_value(10+num, 'Point2D/3D')
        else:
            raise IndexError(num)

    def __setitem__(self, num, value):
        if num in (0, 1, 2, 3):
            tags = ExtendedType(self.tags)
            return self._set_value(10+num, 'Point2D/3D', value)
        else:
            raise IndexError(num)

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

class AC1009Line(GenericWrapper, ColorMixin):
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

class AC1009Point(GenericWrapper, ColorMixin):
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

class AC1009Circle(GenericWrapper, ColorMixin):
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

class AC1009Arc(GenericWrapper, ColorMixin):
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

class AC1009Trace(GenericWrapper, ColorMixin, FourPointsMixin):
    TEMPLATE = _TRACE_TPL
    DXFATTRIBS = make_AC1009_attribs()

_SOLID_TPL = _TRACE_TPL.replace('TRACE', 'SOLID')

class AC1009Solid(AC1009Trace):
    TEMPLATE = _SOLID_TPL

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

class AC1009Text(GenericWrapper, ColorMixin):
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
class AC1009Block(GenericWrapper):
    TEMPLATE = _BLOCK_TPL
    DXFATTRIBS = make_AC1009_attribs({
        'name': DXFAttr(2, None, None),
        'name2': DXFAttr(3, None, None),
        'flags': DXFAttr(70, None, None),
        'insert': DXFAttr(10, None, 'Point2D/3D'),
        'xrefpath': DXFAttr(1, None, None),
    })

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
class AC1009Insert(GenericWrapper):
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