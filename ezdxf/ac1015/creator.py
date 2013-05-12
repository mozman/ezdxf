# Purpose: AC1015 graphic builder
# Created: 10.03.2013
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


class EntityCreator(object):
    def add_lwpolyline(self, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        closed = dxfattribs.pop('closed', False)
        lwpolyline = self._create('LWPOLYLINE', dxfattribs)
        lwpolyline.close(closed)
        lwpolyline._setup_points(points)
        return lwpolyline
