#!/usr/bin/env python
#coding:utf-8
# Purpose: dxf factory for R2000/AC1015
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..tags import Tags

from .headervars import VARMAP
from ..ac1009 import AC1009Factory
from . import tableentries
from . import graphics
from .layouts import AC1015Layouts, AC1015BlockLayout

UPDATE_ENTITY_WRAPPERS = {
    'LAYER': tableentries.Layer,
    'STYLE': tableentries.Style,
    'LTYPE': tableentries.Linetype,
    'DIMSTYLE': tableentries.DimStyle,
    'VIEW': tableentries.View,
    'VPORT': tableentries.Viewport,
    'UCS': tableentries.UCS,
    'APPID': tableentries.AppID,
    'BLOCK_RECORD': tableentries.BlockRecord,
    'LINE': graphics.Line,
    'POINT': graphics.Point,
    'CIRCLE': graphics.Circle,
    'ARC': graphics.Arc,
    'TRACE': graphics.Trace,
    'SOLID': graphics.Solid,
    '3DFACE': graphics.Face,
    'TEXT': graphics.Text,
    'POLYLINE': graphics.Polyline,
    'VERTEX': graphics.Vertex,
    'SEQEND': graphics.SeqEnd,
    'LWPOLYLINE': graphics.LWPolyline,
    'BLOCK': graphics.Block,
    'ENDBLK': graphics.EndBlk,
    'INSERT': graphics.Insert,
    'ATTDEF': graphics.Attdef,
    'ATTRIB': graphics.Attrib,
    'ELLIPSE': graphics.Ellipse,
    'RAY': graphics.Ray,
    'XLINE': graphics.Ray,
}

class AC1015Factory(AC1009Factory):
    HEADERVARS = dict(VARMAP)
    def __init__(self):
        super(AC1015Factory, self).__init__()
        self.ENTITY_WRAPPERS.update(UPDATE_ENTITY_WRAPPERS)

    @property
    def rootdict(self):
        return self.drawing.rootdict

    def get_layouts(self):
        return AC1015Layouts(self.drawing)

    def new_block_layout(self, block_handle, endblk_handle):
        return AC1015BlockLayout(self.entitydb, self, block_handle, endblk_handle)
    