#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: ac1009 tableentries
# Created: 16.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..entity import GenericWrapper
from ..tags import DXFTag

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

class Layer(GenericWrapper):
    TEMPLATE = _LAYERTEMPLATE
    CODE = {
        'handle': 5,
        'name': 2,
        'flags': 70,
        'color': 62, # dxf color index, if < 0 layer is off
        'linetype': 6,
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

class Style(GenericWrapper):
    TEMPLATE = _STYLETEMPLATE
    CODE = {
        'handle': 5,
        'name': 2,
        'flags': 70,
        'height': 40, # fixed height, 0 if not fixed
        'width': 41, # width factor
        'oblique': 50, # oblique angle in degree, 0 = vertical
        'generation_flags': 71, # 2 = backward, 4 = mirrored in Y
        'last_height': 42, # last height used
        'font': 3, # primary font file name
        'bigfont': 4, # big font name, blank if none
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

class Linetype(GenericWrapper):
    TEMPLATE = _LTYPETEMPLATE
    CODE = {
        'handle': 5,
        'name': 2,
        'description': 3,
    }
    @classmethod
    def new(cls, handle, attribs=None, dxffactory=None):
        if attribs is not None:
            pattern = attribs.pop('pattern', [0.0])
        else:
            pattern = [0.0]
        entity = super(Linetype, cls).new(handle, attribs, dxffactory)
        entity._setup_pattern(pattern)
        return entity

    def _setup_pattern(self, pattern):
        self.tags.append(DXFTag(73), len(pattern)-1)
        self.tags.append(DXFTag(40), float(pattern[0]))
        self.tags.extend( (DXFTag(49, float(p)) for p in pattern[1:]) )


_VPORTTEMPLATE = """  0
VPORT
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


class Viewport(GenericWrapper):
    TEMPLATE = _VPORTTEMPLATE
    CODE = {
        'handle': 5,
        'name': 2,
        'flags': 70,
        'lower_left': (10, 'Point2D'),
        'upper_right': (11, 'Point2D'),
        'center_point': (12, 'Point2D'),
        'snap_base': (13, 'Point2D'),
        'snap_spacing': (14, 'Point2D'),
        'grid_spacing': (15, 'Point2D'),
        'direction_point': (16, 'Point3D'),
        'target_point': (17, 'Point3D'),
        'height': 40,
        'aspect_ratio': 41,
        'lens_length': 42,
        'front_clipping': 43,
        'back_clipping': 44,
        'snap_rotation': 50,
        'view_twist': 51,
        'status': 68,
        'id': 69,
        'view_mode': 71,
        'circle_zoom': 72,
        'fast_zoom': 73,
        'ucs_icon': 74,
        'snap_on': 75,
        'grid_on': 76,
        'snap_style': 77,
        'snap_isopair': 78,
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

class UCS(GenericWrapper):
    TEMPLATE = _UCSTEMPLATE
    CODE = {
        'handle': 5,
        'name': 2,
        'flags': 70,
        'origin': (10, 'Point3D'),
        'xaxis': (11, 'Point3D'),
        'yaxis': (12, 'Point3D'),
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

class AppID(GenericWrapper):
    TEMPLATE = _APPIDTEMPLATE
    CODE = {
        'handle': 5,
        'name': 2,
        'flags': 70,
    }


class View(GenericWrapper):
    CODE = {
        'handle': 5,
        'name': 2,
        'flags': 70,
        'height': 40,
        'width': 41,
        'center_point': (10, 'Point2D'),
        'direction_point': (11, 'Point3D'),
        'target_point': (12, 'Point3D'),
        'lens_length': 42,
        'front_clipping': 43,
        'back_clipping': 44,
        'view_twist': 50,
        'view_mode': 71,
    }
    @classmethod
    def new(cls, handle, attribs=None, dxffactory=None):
        raise NotImplementedError("View creation is not supported.")


class DimStyle(GenericWrapper):
    CODE = {
        'handle': 105,
        'name': 2,
        'flags': 70,
        'dimpost':3,
        'dimapost': 4,
        'dimblk': 5,
        'dimblk1': 6,
        'dimblk2': 7,
        'dimscale': 40,
        'dimasz': 41,
        'dimexo': 42,
        'dimdli': 43,
        'dimexe': 44,
        'dimrnd':45,
        'dimdle':46,
        'dimtp':47,
        'dimtm':48,
        'dimtxt': 140,
        'dimcen': 141,
        'dimtsz': 142,
        'dimaltf': 143,
        'dimlfac': 144,
        'dimtvp': 145,
        'dimtfac': 146,
        'dimgap': 147,
        'dimtol': 71,
        'dimlim': 72,
        'dimtih': 73,
        'dimtoh': 74,
        'dimse1': 75,
        'dimse2': 76,
        'dimtad': 77,
        'dimzin': 78,
        'dimalt': 170,
        'dimaltd': 171,
        'dimtofl': 172,
        'dimsah': 173,
        'dimtix': 174,
        'dimsoxd': 175,
        'dimclrd': 176,
        'dimclre': 177,
        'dimclrt': 178,
    }
    @classmethod
    def new(cls, handle, attribs=None, dxffactory=None):
        raise NotImplementedError("DimStyle creation is not supported.")
