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
from .tableentries import Layer, BlockRecord

UPDATE_ENTITY_WRAPPERS = {
    'LAYER': Layer,
    'BLOCK_RECORD': BlockRecord,
}

class AC1015Factory(AC1009Factory):
    HEADERVARS = dict(VARMAP)
    def __init__(self):
        super(AC1015Factory, self).__init__()
        self.ENTITY_WRAPPERS.update(UPDATE_ENTITY_WRAPPERS)

    @property
    def rootdict(self):
        return self.drawing.rootdict
