# Purpose: support for the Ac1015 SPLINE entity
# Created: 24.05.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager

from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf.tags import DXFTag
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf import const

_SPLINE_TPL = """  0
SPLINE
  5
0
330
0
100
AcDbEntity
  8
0
100
AcDbSpline
 70
0
 71
3
 72
0
 73
0
 74
0
"""
spline_subclass = DefSubclass('AcDbSpline', {
    'flags': DXFAttr(70, default=0),
    'degree': DXFAttr(71),
    'n_knots': DXFAttr(72),
    'n_control_points': DXFAttr(73),
    'n_fit_points': DXFAttr(74),
    'knot_tolerance': DXFAttr(42, default=1e-10),
    'control_point_tolerance': DXFAttr(43, default=1e-10),
    'fit_tolerance': DXFAttr(44, default=1e-10),
    'start_tangent': DXFAttr(12, xtype='Point3D'),
    'end_tangent': DXFAttr(13, xtype='Point3D'),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Spline(ModernGraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_SPLINE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, spline_subclass)

    @property
    def AcDbSpline(self):
        return self.tags.subclasses[2]

    @property
    def closed(self):
        return bool(self.dxf.flags & const.CLOSED_SPLINE)

    @closed.setter
    def closed(self, status):
        flagsnow = self.dxf.flags
        if status:
            self.dxf.flags = flagsnow | const.CLOSED_SPLINE
        else:
            self.dxf.flags = flagsnow & (~const.CLOSED_SPLINE)

    def get_knot_values(self):
        return [tag.value for tag in self.AcDbSpline.find_all(code=40)]

    def set_knot_values(self, knot_values):
        self._set_values(knot_values, code=40)
        self.dxf.n_knots = len(knot_values)

    def _set_values(self, values, code):
        tags = self.AcDbSpline
        tags.remove_tags(codes=(code, ))
        tags.extend([DXFTag(code, value) for value in values])

    @contextmanager
    def knot_values(self):
        raise RuntimeError("Spline.knot_values() is deprecated, use Spline.edit_data()")

    def get_weights(self):
        return [tag.value for tag in self.AcDbSpline.find_all(code=41)]

    def set_weights(self, values):
        self._set_values(values, code=41)

    @contextmanager
    def weights(self):
        raise RuntimeError("Spline.weights() is deprecated, use Spline.edit_data()")

    def get_control_points(self):
        return [tag.value for tag in self.AcDbSpline if tag.code == 10]

    def set_control_points(self, points):
        self.AcDbSpline.remove_tags(codes=(10, ))
        count = self._append_points(points, code=10)
        self.dxf.n_control_points = count

    def _append_points(self, points, code):
        tags = []
        for point in points:
            if len(point) != 3:
                raise ValueError("require 3D points")
            tags.append(DXFTag(code, point))
        self.AcDbSpline.extend(tags)
        return len(tags)

    @contextmanager
    def control_points(self):
        raise RuntimeError("Spline.control_points() is deprecated, use Spline.edit_data()")

    def get_fit_points(self):
        return [tag.value for tag in self.AcDbSpline if tag.code == 11]

    def set_fit_points(self, points):
        self.AcDbSpline.remove_tags(codes=(11, ))
        count = self._append_points(points, code=11)
        self.dxf.n_fit_points = count

    @contextmanager
    def fit_points(self):
        raise RuntimeError("Spline.fit_points() is deprecated, use Spline.edit_data()")

    @contextmanager
    def edit_data(self):
        data = SplineData(self)
        yield data
        self.set_fit_points(data.fit_points)
        self.set_control_points(data.control_points)
        self.set_knot_values(data.knot_values)
        self.set_weights(data.weights)


class SplineData(object):
    def __init__(self, spline):
        self.fit_points = spline.get_fit_points()
        self.control_points = spline.get_control_points()
        self.knot_values = spline.get_knot_values()
        self.weights = spline.get_weights()
