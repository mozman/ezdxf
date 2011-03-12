#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R12/AC1009
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .hdrvars import VARMAP

class AC1009Engine:
    def __init__(self):
        self.HEADERVARS = dict(VARMAP)

    def new_header_var(self, key, value):
        factory = self.HEADERVARS[key]
        return factory(value)

