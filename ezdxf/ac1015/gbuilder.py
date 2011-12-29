#!/usr/bin/env python
#coding:utf-8
# Purpose: AC1015 graphic builder
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

class AC1015GraphicsBuilder:
    def add_lwpolyline(self, points, dxfattribs={}):
        closed = dxfattribs.pop('closed', False)
        lwpolyline = self._create('LWPOLYLINE', dxfattribs)
        lwpolyline.close(closed)
        lwpolyline._setup_points(points)
        return lwpolyline
        
