#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: ac1015 tableentries
# Created: 16.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import casttagvalue, DXFTag, DXFAttr
from ..ac1009.tableentries import AC1009Layer, AC1009Style, AC1009Linetype
from ..ac1009.tableentries import AC1009AppID, AC1009DimStyle, AC1009UCS
from ..ac1009.tableentries import AC1009View, AC1009Viewport
from ..entity import GenericWrapper

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
390
0
"""

# code 390 is required for AutoCAD
# Pointer/handle to PlotStyleName
# uses tag(390, ...) from the '0' layer

class AC1015Layer(AC1009Layer):
    TEMPLATE = _LAYERTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2,  'AcDbLayerTableRecord', None), # layer name
        'flags': DXFAttr(70, 'AcDbLayerTableRecord', None),
        'color': DXFAttr(62,  'AcDbLayerTableRecord', None), # dxf color index
        'linetype': DXFAttr(6,  'AcDbLayerTableRecord', None), # linetype name
        'plot': DXFAttr(290, 'AcDbLayerTableRecord', None), # dont plot this layer if 0 else 1
        'lineweight': DXFAttr(370, 'AcDbLayerTableRecord', None), # enum value???
        'plotstylename': DXFAttr(390,'AcDbLayerTableRecord', None), # handle to PlotStyleName object
    }

    @classmethod
    def new(cls, handle, attribs=None, dxffactory=None):
        layer = super(AC1015Layer, cls).new(handle, attribs)
        layer.plotstylename= dxffactory.rootdict['ACAD_PLOTSTYLENAME']
        return layer

_STYLETEMPLATE = """  0
STYLE
  5
0
100
AcDbSymbolTableRecord
100
AcDbTextStyleTableRecord
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
0.2
  3
arial.ttf
  4

"""
class AC1015Style(AC1009Style):
    TEMPLATE = _STYLETEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, 'AcDbTextStyleTableRecord', None),
        'flags': DXFAttr(70, 'AcDbTextStyleTableRecord', None),
        'height': DXFAttr(40, 'AcDbTextStyleTableRecord', None), # fixed height, 0 if not fixed
        'width': DXFAttr(41, 'AcDbTextStyleTableRecord', None), # width factor
        'oblique': DXFAttr(50, 'AcDbTextStyleTableRecord', None), # oblique angle in degree, 0 = vertical
        'generation_flags': DXFAttr(71, 'AcDbTextStyleTableRecord', None), # 2 = backward, 4 = mirrored in Y
        'last_height': DXFAttr(42, 'AcDbTextStyleTableRecord', None), # last height used
        'font': DXFAttr(3, 'AcDbTextStyleTableRecord', None), # primary font file name
        'bigfont': DXFAttr(4, 'AcDbTextStyleTableRecord', None), # big font name, blank if none
    }

_LTYPETEMPLATE = """  0
LTYPE
  5
0
100
AcDbSymbolTableRecord
100
AcDbLinetypeTableRecord
  2
LTYPENAME
 70
0
  3
LTYPEDESCRIPTION
 72
65
"""
class AC1015Linetype(AC1009Linetype):
    TEMPLATE = _LTYPETEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, 'AcDbLinetypeTableRecord', None),
        'description': DXFAttr(3, 'AcDbLinetypeTableRecord', None),
        'length': DXFAttr(40, 'AcDbLinetypeTableRecord', None),
        'items': DXFAttr( 73, 'AcDbLinetypeTableRecord', None),
    }

    def _setup_pattern(self, pattern):
        subclass = self.tags.subclass['AcDbLinetypeTableRecord']
        subclass.append(DXFTag(73, len(pattern)-1))
        subclass.append(DXFTag(40, float(pattern[0])))

        for element in pattern[1:]:
            subclass.append(DXFTag(49, float(element)))
            subclass.append(DXFTag(74, 0))

_APPIDTEMPLATE = """  0
APPID
  5
0
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
APPIDNAME
 70
0
"""
class AC1015AppID(AC1009AppID):
    TEMPLATE = _APPIDTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, 'AcDbRegAppTableRecord', None),
        'flags': DXFAttr(70, 'AcDbRegAppTableRecord', None),
    }

_DIMSTYLETEMPLATE = """  0
DIMSTYLE
105
0
100
AcDbSymbolTableRecord
100
AcDbDimStyleTableRecord
  2
STANDARD
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
class AC1015DimStyle(AC1009DimStyle):
    TEMPLATE = _DIMSTYLETEMPLATE
    CODE = {
        'handle': DXFAttr(105, None, None),
        'name': DXFAttr(2, 'AcDbDimStyleTableRecord', None),
        'flags': DXFAttr(70, 'AcDbDimStyleTableRecord', None),
        'dimpost': DXFAttr(3, 'AcDbDimStyleTableRecord', None),
        'dimapost': DXFAttr(4, 'AcDbDimStyleTableRecord', None),
        'dimblk': DXFAttr(5, 'AcDbDimStyleTableRecord', None),
        'dimblk1': DXFAttr(6, 'AcDbDimStyleTableRecord', None),
        'dimblk2': DXFAttr(7, 'AcDbDimStyleTableRecord', None),
        'dimscale': DXFAttr(40, 'AcDbDimStyleTableRecord', None),
        'dimasz': DXFAttr(41, 'AcDbDimStyleTableRecord', None),
        'dimexo': DXFAttr(42, 'AcDbDimStyleTableRecord', None),
        'dimdli': DXFAttr(43, 'AcDbDimStyleTableRecord', None),
        'dimexe': DXFAttr(44, 'AcDbDimStyleTableRecord', None),
        'dimrnd': DXFAttr(45, 'AcDbDimStyleTableRecord', None),
        'dimdle': DXFAttr(46, 'AcDbDimStyleTableRecord', None),
        'dimtp': DXFAttr(47, 'AcDbDimStyleTableRecord', None),
        'dimtm': DXFAttr(48, 'AcDbDimStyleTableRecord', None),
        'dimtxt': DXFAttr(140, 'AcDbDimStyleTableRecord', None),
        'dimcen': DXFAttr(141, 'AcDbDimStyleTableRecord', None),
        'dimtsz': DXFAttr(142, 'AcDbDimStyleTableRecord', None),
        'dimaltf': DXFAttr(143, 'AcDbDimStyleTableRecord', None),
        'dimlfac': DXFAttr(144, 'AcDbDimStyleTableRecord', None),
        'dimtvp': DXFAttr(145, 'AcDbDimStyleTableRecord', None),
        'dimtfac': DXFAttr(146, 'AcDbDimStyleTableRecord', None),
        'dimgap': DXFAttr(147, 'AcDbDimStyleTableRecord', None),
        'dimtol': DXFAttr(71, 'AcDbDimStyleTableRecord', None),
        'dimlim': DXFAttr(72, 'AcDbDimStyleTableRecord', None),
        'dimtih': DXFAttr(73, 'AcDbDimStyleTableRecord', None),
        'dimtoh': DXFAttr(74, 'AcDbDimStyleTableRecord', None),
        'dimse1': DXFAttr(75, 'AcDbDimStyleTableRecord', None),
        'dimse2': DXFAttr(76, 'AcDbDimStyleTableRecord', None),
        'dimtad': DXFAttr(77, 'AcDbDimStyleTableRecord', None),
        'dimzin': DXFAttr(78, 'AcDbDimStyleTableRecord', None),
        'dimalt': DXFAttr(170, 'AcDbDimStyleTableRecord', None),
        'dimaltd': DXFAttr(171, 'AcDbDimStyleTableRecord', None),
        'dimtofl': DXFAttr(172, 'AcDbDimStyleTableRecord', None),
        'dimsah': DXFAttr(173, 'AcDbDimStyleTableRecord', None),
        'dimtix': DXFAttr(174, 'AcDbDimStyleTableRecord', None),
        'dimsoxd': DXFAttr(175, 'AcDbDimStyleTableRecord', None),
        'dimclrd': DXFAttr(176, 'AcDbDimStyleTableRecord', None),
        'dimclre': DXFAttr(177, 'AcDbDimStyleTableRecord', None),
        'dimclrt': DXFAttr(178, 'AcDbDimStyleTableRecord', None),
    }
_UCSTEMPLATE = """  0
UCS
  5
0
100
AcDbSymbolTableRecord
100
AcDbUCSTableRecord
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
class AC1015UCS(AC1009UCS):
    TEMPLATE = _UCSTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, 'AcDbUCSTableRecord', None),
        'flags': DXFAttr(70, 'AcDbUCSTableRecord', None),
        'origin': DXFAttr(10, 'AcDbUCSTableRecord', 'Point3D'),
        'xaxis': DXFAttr(11, 'AcDbUCSTableRecord', 'Point3D'),
        'yaxis': DXFAttr(12, 'AcDbUCSTableRecord', 'Point3D'),
    }

_VIEWTEMPLATE = """  0
VIEW
  5
0
100
AcDbSymbolTableRecord
100
AcDbViewTableRecord
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
class AC1015View(AC1009View):
    TEMPLATE = _VIEWTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, 'AcDbViewTableRecord', None),
        'flags': DXFAttr(70, 'AcDbViewTableRecord', None),
        'height': DXFAttr(40, 'AcDbViewTableRecord', None),
        'width': DXFAttr(41, 'AcDbViewTableRecord', None),
        'center_point': DXFAttr(10, 'AcDbViewTableRecord', 'Point2D'),
        'direction_point': DXFAttr(11, 'AcDbViewTableRecord', 'Point3D'),
        'target_point': DXFAttr(12, 'AcDbViewTableRecord', 'Point3D'),
        'lens_length': DXFAttr(42, 'AcDbViewTableRecord', None),
        'front_clipping': DXFAttr(43, 'AcDbViewTableRecord', None),
        'back_clipping': DXFAttr(44, 'AcDbViewTableRecord', None),
        'view_twist': DXFAttr(50, 'AcDbViewTableRecord', None),
        'view_mode': DXFAttr(71, 'AcDbViewTableRecord', None),
    }

_VPORTTEMPLATE = """  0
VPORT
  5
0
100
AcDbSymbolTableRecord
100
AcDbViewportTableRecord
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
class AC1015Viewport(AC1009Viewport):
    TEMPLATE = _VPORTTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'name': DXFAttr(2, 'AcDbViewportTableRecord', None),
        'flags': DXFAttr(70, 'AcDbViewportTableRecord', None),
        'lower_left': DXFAttr(10, 'AcDbViewportTableRecord', 'Point2D'),
        'upper_right': DXFAttr(11, 'AcDbViewportTableRecord', 'Point2D'),
        'center_point': DXFAttr(12, 'AcDbViewportTableRecord', 'Point2D'),
        'snap_base': DXFAttr(13, 'AcDbViewportTableRecord', 'Point2D'),
        'snap_spacing': DXFAttr(14, 'AcDbViewportTableRecord', 'Point2D'),
        'grid_spacing': DXFAttr(15, 'AcDbViewportTableRecord', 'Point2D'),
        'direction_point': DXFAttr(16, 'AcDbViewportTableRecord', 'Point3D'),
        'target_point': DXFAttr(17, 'AcDbViewportTableRecord', 'Point3D'),
        'height': DXFAttr(40, 'AcDbViewportTableRecord', None),
        'aspect_ratio': DXFAttr(41, 'AcDbViewportTableRecord', None),
        'lens_length': DXFAttr(42, 'AcDbViewportTableRecord', None),
        'front_clipping': DXFAttr(43, 'AcDbViewportTableRecord', None),
        'back_clipping': DXFAttr(44, 'AcDbViewportTableRecord', None),
        'snap_rotation': DXFAttr(50, 'AcDbViewportTableRecord', None),
        'view_twist': DXFAttr(51, 'AcDbViewportTableRecord', None),
        'status': DXFAttr(68, 'AcDbViewportTableRecord', None),
        'id': DXFAttr(69, 'AcDbViewportTableRecord', None),
        'view_mode': DXFAttr(71, 'AcDbViewportTableRecord', None),
        'circle_zoom': DXFAttr(72, 'AcDbViewportTableRecord', None),
        'fast_zoom': DXFAttr(73, 'AcDbViewportTableRecord', None),
        'ucs_icon': DXFAttr(74, 'AcDbViewportTableRecord', None),
        'snap_on': DXFAttr(75, 'AcDbViewportTableRecord', None),
        'grid_on': DXFAttr(76, 'AcDbViewportTableRecord', None),
        'snap_style': DXFAttr(77, 'AcDbViewportTableRecord', None),
        'snap_isopair': DXFAttr(78, 'AcDbViewportTableRecord', None),
    }
_BLOCKRECORDTEMPLATE = """  0
BLOCK_RECORD
  5
0
330
0
100
AcDbSymbolTableRecord
100
AcDbBlockTableRecord
  2
BLOCK_RECORD_NAME
340
0
"""
class AC1015BlockRecord(GenericWrapper):
    """ Internal Object - use at your own risk!

    Required fields:
    owner: Soft-pointer ID/handle to owner object
    layout: Hard-pointer ID/handle to associated LAYOUT object
    """
    TEMPLATE = _BLOCKRECORDTEMPLATE
    CODE = {
        'handle': DXFAttr(5, None, None),
        'owner': DXFAttr(330, 'AcDbBlockTableRecord', None),
        'name': DXFAttr(2, 'AcDbBlockTableRecord', None),
        'layout': DXFAttr(340, 'AcDbBlockTableRecord', None),
    }
