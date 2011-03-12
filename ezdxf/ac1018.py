#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R2004/AC1018
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from .hdrvars import SingleValue, Point2D, Point3D

from .ac1015 import AC1015Engine

class AC1018Engine(AC1015Engine):
    def __init__(self):
        super(AC1018Engine, self).__init__()
        self.HEADERVARS.update(AC1018VARMAP)

AC1018VARMAP = {
}