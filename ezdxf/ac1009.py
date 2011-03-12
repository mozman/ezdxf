#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R12/AC1009
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .ac1009hdrvars import VARMAP
from .handle import HandleGenerator

class AC1009Engine:
    HEADERVARS = dict(VARMAP)
    def __init__(self):
        self.drawing = None

    def nexthandle(self):
        return "%X" % self.drawing.handlegenerator.next()

    def new_header_var(self, key, value):
        factory = self.HEADERVARS[key]
        return factory(value)


