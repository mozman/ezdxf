#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: ac1009 tableentries
# Created: 16.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..entity import GenericWrapper
from ..tags import DXFTag, DXFAttr

_LAYERTEMPLATE = """  0
LAYER
  5
0
  2
LAYERNAME
 70
0
 62
7
  6
CONTINUOUS
"""

class AC1009Layer(GenericWrapper):
    TEMPLATE = _LAYERTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, None, None),
        'flags': DXFAttr(70, None, None),
        'color': DXFAttr(62,  None, None), # dxf color index, if < 0 layer is off
        'linetype': DXFAttr(6, None, None),
    }
    LOCK = 0b00000100
    UNLOCK = 0b11111011

    def is_locked(self):
        return self.flags & Layer.LOCK > 0
    def lock(self):
        self.flags = self.flags | Layer.LOCK
    def unlock(self):
        self.flags = self.flags & Layer.UNLOCK

    def is_off(self):
        return self.color < 0
    def is_on(self):
        return not self.is_off()
    def on(self):
        self.color = abs(self.color)
    def off(self):
        self.color = -(abs(self.color))

    def get_color(self):
        return abs(self.color)
    def set_color(self, color):
        sign = -1 if self.color < 0 else 1
        self.color = color * sign


_STYLETEMPLATE = """  0
STYLE
  5
0
  2
STYLENAME
 70
0
 40
0.0
 41
1.0
 50
0.0
 71
0
 42
1.0
  3
arial.ttf
  4

"""

class AC1009Style(GenericWrapper):
    TEMPLATE = _STYLETEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, None, None),
        'flags': DXFAttr(70, None, None),
        'height': DXFAttr(40, None, None), # fixed height, 0 if not fixed
        'width': DXFAttr(41, None, None), # width factor
        'oblique': DXFAttr(50, None, None), # oblique angle in degree, 0 = vertical
        'generation_flags': DXFAttr(71, None, None), # 2 = backward, 4 = mirrored in Y
        'last_height': DXFAttr(42, None, None), # last height used
        'font': DXFAttr(3, None, None), # primary font file name
        'bigfont': DXFAttr(4, None, None), # big font name, blank if none
    }


_LTYPETEMPLATE = """  0
LTYPE
  5
0
  2
LTYPENAME
 70
0
  3
LTYPEDESCRIPTION
 72
65
"""

class AC1009Linetype(GenericWrapper):
    TEMPLATE = _LTYPETEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, None, None),
        'description': DXFAttr(3, None, None),
        'length': DXFAttr(40, None, None),
        'items': DXFAttr( 73, None, None),
    }
    @classmethod
    def new(cls, handle, attribs=None, dxffactory=None):
        if attribs is not None:
            pattern = attribs.pop('pattern', [0.0])
        else:
            pattern = [0.0]
        entity = super(AC1009Linetype, cls).new(handle, attribs, dxffactory)
        entity._setup_pattern(pattern)
        return entity

    def _setup_pattern(self, pattern):
        self.tags.append(DXFTag(73, len(pattern)-1))
        self.tags.append(DXFTag(40, float(pattern[0])))
        self.tags.extend( (DXFTag(49, float(p)) for p in pattern[1:]) )


_VPORTTEMPLATE = """  0
VPORT
  5
0
  2
VPORTNAME
 70
0
 10
0.0
 20
0.0
 11
1.0
 21
1.0
 12
70.0
 22
50.0
 13
0.0
 23
0.0
 14
0.5
 24
0.5
 15
0.5
 25
0.5
 16
0.0
 26
0.0
 36
1.0
 17
0.0
 27
0.0
 37
0.0
 40
70.
 41
1.34
 42
50.0
 43
0.0
 44
0.0
 50
0.0
 51
0.0
 71
0
 72
1000
 73
1
 74
3
 75
0
 76
0
 77
0
 78
0
"""


class AC1009Viewport(GenericWrapper):
    TEMPLATE = _VPORTTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, None, None),
        'flags': DXFAttr(70, None, None),
        'lower_left': DXFAttr(10, None, 'Point2D'),
        'upper_right': DXFAttr(11, None, 'Point2D'),
        'center_point': DXFAttr(12, None, 'Point2D'),
        'snap_base': DXFAttr(13, None, 'Point2D'),
        'snap_spacing': DXFAttr(14, None, 'Point2D'),
        'grid_spacing': DXFAttr(15, None, 'Point2D'),
        'direction_point': DXFAttr(16, None, 'Point3D'),
        'target_point': DXFAttr(17, None, 'Point3D'),
        'height': DXFAttr(40, None, None),
        'aspect_ratio': DXFAttr(41, None, None),
        'lens_length': DXFAttr(42, None, None),
        'front_clipping': DXFAttr(43, None, None),
        'back_clipping': DXFAttr(44, None, None),
        'snap_rotation': DXFAttr(50, None, None),
        'view_twist': DXFAttr(51, None, None),
        'status': DXFAttr(68, None, None),
        'id': DXFAttr(69, None, None),
        'view_mode': DXFAttr(71, None, None),
        'circle_zoom': DXFAttr(72, None, None),
        'fast_zoom': DXFAttr(73, None, None),
        'ucs_icon': DXFAttr(74, None, None),
        'snap_on': DXFAttr(75, None, None),
        'grid_on': DXFAttr(76, None, None),
        'snap_style': DXFAttr(77, None, None),
        'snap_isopair': DXFAttr(78, None, None),
    }


_UCSTEMPLATE = """  0
UCS
  5
0
  2
UCSNAME
 70
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
0.0
 31
0.0
 12
0.0
 22
1.0
 32
0.0
"""

class AC1009UCS(GenericWrapper):
    TEMPLATE = _UCSTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, None, None),
        'flags': DXFAttr(70, None, None),
        'origin': DXFAttr(10, None, 'Point3D'),
        'xaxis': DXFAttr(11, None, 'Point3D'),
        'yaxis': DXFAttr(12, None, 'Point3D'),
    }


_APPIDTEMPLATE = """  0
APPID
  5
0
  2
APPNAME
 70
0
"""

class AC1009AppID(GenericWrapper):
    TEMPLATE = _APPIDTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, None, None),
        'flags': DXFAttr(70, None, None),
    }

_VIEWTEMPLATE = """  0
VIEW
  5
0
  2
VIEWNAME
 70
0
 10
0.0
 20
0.0
 11
1.0
 21
1.0
 31
1.0
 12
0.0
 22
0.0
 32
0.0
 40
70.
 41
1.0
 42
50.0
 43
0.0
 44
0.0
 50
0.0
 71
0
"""

class AC1009View(GenericWrapper):
    TEMPLATE = _VIEWTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, None, None),
        'flags': DXFAttr(70, None, None),
        'height': DXFAttr(40, None, None),
        'width': DXFAttr(41, None, None),
        'center_point': DXFAttr(10, None, 'Point2D'),
        'direction_point': DXFAttr(11, None, 'Point3D'),
        'target_point': DXFAttr(12, None, 'Point3D'),
        'lens_length': DXFAttr(42, None, None),
        'front_clipping': DXFAttr(43, None, None),
        'back_clipping': DXFAttr(44, None, None),
        'view_twist': DXFAttr(50, None, None),
        'view_mode': DXFAttr(71, None, None),
    }

_DIMSTYLETEMPLATE = """  0
DIMSTYLE
105
0
  2
DIMSTYLENAME
 70
0
  3

  4

  5

  6

  7

 40
1.0
 41
3.0
 42
2.0
 43
9.0
 44
5.0
 45
0.0
 46
0.0
 47
0.0
 48
0.0
140
3.0
141
2.0
142
0.0
143
25.399999999999999
144
1.0
145
0.0
146
1.0
147
2.0
 71
     0
 72
     0
 73
     1
 74
     1
 75
     0
 76
     0
 77
     0
 78
     0
170
     0
171
     2
172
     0
173
     0
174
     0
175
     0
176
     0
177
     0
178
     0
"""

class AC1009DimStyle(GenericWrapper):
    TEMPLATE = _DIMSTYLETEMPLATE
    CODE = {
        'handle': DXFAttr(105, None, None),
        'name': DXFAttr(2, None, None),
        'flags': DXFAttr(70, None, None),
        'dimpost': DXFAttr(3, None, None),
        'dimapost': DXFAttr(4, None, None),
        'dimblk': DXFAttr(5, None, None),
        'dimblk1': DXFAttr(6, None, None),
        'dimblk2': DXFAttr(7, None, None),
        'dimscale': DXFAttr(40, None, None),
        'dimasz': DXFAttr(41, None, None),
        'dimexo': DXFAttr(42, None, None),
        'dimdli': DXFAttr(43, None, None),
        'dimexe': DXFAttr(44, None, None),
        'dimrnd': DXFAttr(45, None, None),
        'dimdle': DXFAttr(46, None, None),
        'dimtp': DXFAttr(47, None, None),
        'dimtm': DXFAttr(48, None, None),
        'dimtxt': DXFAttr(140, None, None),
        'dimcen': DXFAttr(141, None, None),
        'dimtsz': DXFAttr(142, None, None),
        'dimaltf': DXFAttr(143, None, None),
        'dimlfac': DXFAttr(144, None, None),
        'dimtvp': DXFAttr(145, None, None),
        'dimtfac': DXFAttr(146, None, None),
        'dimgap': DXFAttr(147, None, None),
        'dimtol': DXFAttr(71, None, None),
        'dimlim': DXFAttr(72, None, None),
        'dimtih': DXFAttr(73, None, None),
        'dimtoh': DXFAttr(74, None, None),
        'dimse1': DXFAttr(75, None, None),
        'dimse2': DXFAttr(76, None, None),
        'dimtad': DXFAttr(77, None, None),
        'dimzin': DXFAttr(78, None, None),
        'dimalt': DXFAttr(170, None, None),
        'dimaltd': DXFAttr(171, None, None),
        'dimtofl': DXFAttr(172, None, None),
        'dimsah': DXFAttr(173, None, None),
        'dimtix': DXFAttr(174, None, None),
        'dimsoxd': DXFAttr(175, None, None),
        'dimclrd': DXFAttr(176, None, None),
        'dimclre': DXFAttr(177, None, None),
        'dimclrt': DXFAttr(178, None, None),
    }
