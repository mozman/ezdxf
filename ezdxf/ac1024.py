#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R2010/AC1024
# Created: 12.03.2011
# Copyright (C), Manfred Moitzi
# License: GPLv3

from .hdrvars import SingleValue, Point2D, Point3D

from .ac1021 import AC1021Engine

class AC1024Engine(AC1021Engine):
    def __init__(self):
        super(AC1024Engine, self).__init__()
        self.HEADERVARS.update(AC1024VARMAP)

AC1024VARMAP = {
}