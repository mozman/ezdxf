#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf factory for R2000/AC1015
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3
from ..tags import Tags

from .headervars import VARMAP
from ..ac1009 import AC1009Factory
from .tableentries import AC1015Layer, AC1015Style, AC1015BlockRecord, AC1015Linetype
from .tableentries import AC1015AppID, AC1015DimStyle, AC1015UCS, AC1015View, AC1015Viewport
from .layouts import AC1015Layouts, AC1015BlockLayout
from .graphics import AC1015Line

UPDATE_ENTITY_WRAPPERS = {
    'LAYER': AC1015Layer,
    'STYLE': AC1015Style,
    'LTYPE': AC1015Linetype,
    'DIMSTYLE': AC1015DimStyle,
    'VIEW': AC1015View,
    'VPORT': AC1015Viewport,
    'UCS': AC1015UCS,
    'APPID': AC1015AppID,
    'BLOCK_RECORD': AC1015BlockRecord,
    'LINE': AC1015Line,
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

    def new_block_layout(self):
        return AC1015BlockLayout(self.entitydb, self)
