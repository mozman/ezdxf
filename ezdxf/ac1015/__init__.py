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
from .tableentries import Layer, DimStyle

class AC1015Factory(AC1009Factory):
    HEADERVARS = dict(VARMAP)
    TABLE_ENTRY_WRAPPERS = {
        'LAYER': Layer,
        'DIMSTYLE': DimStyle,
    }
    def _get_default_plot_style_handle(self):
        return self.drawing._system_default_table['DefaultPlotStyleHandle']
