#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R2007/AC1021
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from .hdrvars import SingleValue, Point2D, Point3D

from .ac1018 import AC1018Engine

class AC1021Engine(AC1018Engine):
    def __init__(self):
        super(AC1021Engine, self).__init__()
        self.HEADERVARS.update(AC1021VARMAP)

AC1021VARMAP = {
}