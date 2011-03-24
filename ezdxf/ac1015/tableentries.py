#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: ac1015 tableentries
# Created: 16.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..tags import casttagvalue
from ..ac1009.tableentries import Layer as AC1009Layer
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

from ..tags import UniqueTags

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
        'plotstylename': 390, # handle to PlotStyleName object
    }

    @classmethod
    def new(cls, handle, attribs=None, dxffactory=None):
        layer = super(Layer, cls).new(handle, attribs)
        layer.plotstylename= dxffactory.rootdict['ACAD_PLOTSTYLENAME']
        return layer

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

class BlockRecord(GenericWrapper):
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
