#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: ac1015 tableentries
# Created: 16.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import casttagvalue, DXFTag
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
        'handle': 5,
        'name': 2, # layer name
        'flags': 70,
        'color': 62, # dxf color index
        'linetype': 6, # linetype name
        'plot': 290, # dont plot this layer if 0 else 1
        'lineweight': 370, # enum value???
        'plotstylename': 390, # handle to PlotStyleName object
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
class AC1015Style(AC1009Layer):
    TEMPLATE = _STYLETEMPLATE

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

    def _setup_pattern(self, pattern):
        self.tags.append(DXFTag(73, len(pattern)-1))
        self.tags.append(DXFTag(40, float(pattern[0])))
        for element in pattern[1:]:
            self.tags.append(DXFTag(49, float(element)))
            self.tags.append(DXFTag(74, 0))

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
        'handle': 5,
        'owner': 330,
        'name': 2,
        'layout': 340,
    }
