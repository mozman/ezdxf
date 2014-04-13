# Purpose: AC1015 graphic builder
# Created: 10.03.2013
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


class GraphicsFactoryAC1015(object):
    def add_lwpolyline(self, points, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        closed = dxfattribs.pop('closed', False)
        lwpolyline = self.build_and_add_entity('LWPOLYLINE', dxfattribs)
        lwpolyline.set_points(points)
        lwpolyline.closed = closed
        return lwpolyline

    def add_mtext(self, text, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        mtext = self.build_and_add_entity('MTEXT', dxfattribs)
        mtext.set_text(text)
        return mtext

    def add_ray(self, start, unit_vector, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['start'] = start
        dxfattribs['unit_vector'] = unit_vector
        return self.build_and_add_entity('RAY', dxfattribs)

    def add_xline(self, start, unit_vector, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['start'] = start
        dxfattribs['unit_vector'] = unit_vector
        return self.build_and_add_entity('XLINE', dxfattribs)

    def add_spline(self, points=None, degree=3, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['degree'] = degree
        spline = self.build_and_add_entity('SPLINE', dxfattribs)
        if points is not None:
            spline.set_fit_points(points)
        return spline
