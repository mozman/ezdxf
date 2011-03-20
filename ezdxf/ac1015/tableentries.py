#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: ac1015 tableentries
# Created: 16.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import casttagvalue
from ..ac1009.tableentries import Layer as AC1009Layer
from ..ac1009.tableentries import DimStyle

_LAYERTEMPLATE = """  0
LAYER
  5
LayerHandle
100
AcDbSymbolTableRecord
100
AcDbLayerTableRecord
  2
LayerName
 70
0
 62
7
  6
Continuous
"""

class Layer(AC1009Layer):
    TEMPLATE = _LAYERTEMPLATE
    CODE = {
        'handle': 5,
        'name': 2, # layer name
        'flags': 70,
        'color': 62, # dxf color index
        'linetype': 6, # linetype name
        'plot': 290, # dont plot this layer if 0 else 1
        'lineweight': 370, # enum value???
    }


"""
ATTRIBUTES = {
    'LTYPE': {
        'name': AttribDef(DXFString, 2, priority=52),
        'flags': AttribDef(DXFInt, 70, priority=53),
        'description': AttribDef(DXFString, 3, priority=101),
        'pattern': AttribDef(PassThroughFactory, priority=102),
        },
    'STYLE': {
        'name': AttribDef(DXFString, 2, priority=52),
        'flags': AttribDef(DXFInt, 70, priority=53),
        'height': AttribDef(DXFFloat, 40, priority=101),
        'width': AttribDef(DXFFloat, 41, priority=102),
        'last_height': AttribDef(DXFFloat, 42, priority=103),
        'oblique': AttribDef(DXFAngle, 50, priority=104),
        'generation_flags': AttribDef(DXFInt, 71, priority=105),
        'font': AttribDef(DXFString, 3, priority=106),
        'bigfont': AttribDef(DXFString, 4, priority=107),
        },
    'VIEW': {
        'name': AttribDef(DXFString, 2, priority=52),
        'flags': AttribDef(DXFInt, 70, priority=53),
        'height': AttribDef(DXFFloat, 40, priority=101),
        'width': AttribDef(DXFFloat, 41, priority=102),
        'center_point': AttribDef(DXFPoint2D, 0, priority=103),
        'direction_point': AttribDef(DXFPoint3D, 1, priority=104),
        'target_point': AttribDef(DXFPoint3D, 2, priority=105),
        'lens_length': AttribDef(DXFFloat, 42, priority=106),
        'front_clipping': AttribDef(DXFFloat, 43, priority=107),
        'back_clipping': AttribDef(DXFFloat, 44, priority=108),
        'view_twist': AttribDef(DXFAngle, 50, priority=109),
        'view_mode': AttribDef(DXFInt, 71, priority=110),
        },
    'VPORT': {
        'name': AttribDef(DXFString, 2, priority=52),
        'flags': AttribDef(DXFInt, 70, priority=53),
        'lower_left': AttribDef(DXFPoint2D, 0,priority=101),
        'upper_right': AttribDef(DXFPoint2D, 1, priority=102),
        'center_point': AttribDef(DXFPoint2D, 2, priority=103),
        'snap_base': AttribDef(DXFPoint2D, 3, priority=104),
        'snap_spacing': AttribDef(DXFPoint2D, 4, priority=105),
        'grid_spacing': AttribDef(DXFPoint2D, 5, priority=106),
        'direction_point': AttribDef(DXFPoint3D, 6, priority=107),
        'target_point': AttribDef(DXFPoint3D, 7, priority=108),
        'height': AttribDef(DXFFloat, 40, priority=112),
        'aspect_ratio': AttribDef(DXFFloat, 41, priority=113),
        'lens_length': AttribDef(DXFFloat, 42, priority=109),
        'front_clipping': AttribDef(DXFFloat, 43, priority=110),
        'back_clipping': AttribDef(DXFFloat, 44, priority=111),
        'snap_rotation': AttribDef(DXFAngle, 50, priority=115),
        'view_twist': AttribDef(DXFAngle, 51, priority=116),
        'status': AttribDef(DXFInt, 68, priority=117),
        'id': AttribDef(DXFInt, 69, priority=118),
        'view_mode': AttribDef(DXFInt, 71, priority=122),
        'circle_zoom': AttribDef(DXFInt, 72, priority=123),
        'fast_zoom': AttribDef(DXFInt, 73, priority=124),
        'ucs_icon': AttribDef(DXFInt, 74, priority=126),
        'snap_on': AttribDef(DXFInt, 75, priority=127),
        'grid_on': AttribDef(DXFInt, 76, priority=128),
        'snap_style': AttribDef(DXFInt, 77, priority=129),
        'snap_isopair': AttribDef(DXFInt, 78, priority=130)
        },
    'APPID': {
        'name': AttribDef(DXFString, 2, priority=52),
        'flags': AttribDef(DXFInt, 70, priority=53),
        },
    'UCS': {
        'name': AttribDef(DXFString, 2, priority=52),
        'flags': AttribDef(DXFInt, 70, priority=53),
        'origin': AttribDef(DXFPoint3D, 0,priority=101),
        'xaxis': AttribDef(DXFPoint3D, 1, priority=102),
        'yaxis': AttribDef(DXFPoint3D, 2, priority=103),
        },
    }

"""