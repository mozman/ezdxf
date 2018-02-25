# Purpose: support for the Ac1015 SPLINE entity
# Created: 24.05.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

from contextlib import contextmanager

from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf.tags import DXFTag
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.const import DXFValueError
from ..algebra.bspline import knot_uniform, knot_open_uniform

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
    'n_control_points': DXFAttr(73),  # control vertices define a control frame
    'n_fit_points': DXFAttr(74),  # by default, fit points coincide with the spline
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
    CLOSED = 1  # closed b-spline
    PERIODIC = 2  # uniform b-spline
    RATIONAL = 4  # rational b-spline
    PLANAR = 8  # all spline points in a plane, don't read or set this bit, just ignore like AutoCAD
    LINEAR = 16  # always set with PLANAR, don't read or set this bit, just ignore like AutoCAD

    @property
    def AcDbSpline(self):
        return self.tags.subclasses[2]

    @property
    def closed(self):
        return bool(self.dxf.flags & self.CLOSED)

    @closed.setter
    def closed(self, status):
        flagsnow = self.dxf.flags
        if status:
            self.dxf.flags = flagsnow | self.CLOSED
        else:
            self.dxf.flags = flagsnow & (~self.CLOSED)

    def get_knot_values(self):  # group code 40
        return [tag.value for tag in self.AcDbSpline.find_all(code=40)]

    def set_knot_values(self, knot_values):
        self._set_values(knot_values, code=40)
        self.dxf.n_knots = len(knot_values)

    def _set_values(self, values, code):
        tags = self.AcDbSpline
        tags.remove_tags(codes=(code, ))
        tags.extend([DXFTag(code, value) for value in values])

    def get_weights(self):  # group code 41
        return [tag.value for tag in self.AcDbSpline.find_all(code=41)]

    def set_weights(self, values):
        self._set_values(values, code=41)

    def get_control_points(self):  # group code 10
        return [tag.value for tag in self.AcDbSpline if tag.code == 10]

    def set_control_points(self, points):
        self.AcDbSpline.remove_tags(codes=(10, ))
        count = self._append_points(points, code=10)
        self.dxf.n_control_points = count

    def _append_points(self, points, code):
        tags = []
        for point in points:
            if len(point) != 3:
                raise DXFValueError("3D points required.")
            tags.append(DXFTag(code, point))
        self.AcDbSpline.extend(tags)
        return len(tags)

    def get_fit_points(self):  # group code 11
        return [tag.value for tag in self.AcDbSpline if tag.code == 11]

    def set_fit_points(self, points):
        self.AcDbSpline.remove_tags(codes=(11, ))
        count = self._append_points(points, code=11)
        self.dxf.n_fit_points = count

    def set_open_uniform(self, control_points, degree=3):
        """
        Open B-spline with uniform knot vector, start and end at your first and last control points.

        """
        self.dxf.flags = 0  # clear all flags
        self.dxf.degree = degree
        self.set_control_points(control_points)
        self.set_knot_values(knot_open_uniform(len(control_points), degree+1))

    def set_uniform(self, control_points, degree=3):
        """
        B-spline with uniform knot vector, does NOT start and end at your first and last control points.

        """
        self.dxf.flags = 0  # clear all flags
        self.dxf.degree = degree
        self.set_control_points(control_points)
        self.set_knot_values(knot_uniform(len(control_points), degree+1))

    def set_periodic(self, control_points, degree=3):
        """
        Closed B-spline with uniform knot vector, start and end at your first control point.

        """
        self.dxf.flags = self.PERIODIC | self.CLOSED
        self.dxf.degree = degree
        self.set_control_points(control_points)
        # AutoDesk Developer Docs:
        # If the spline is periodic, the length of knot vector will be greater than length of the control array by 1.
        self.set_knot_values(list(range(len(control_points)+1)))

    def set_open_rational(self, control_points, weights, degree=3):
        """
        Open rational B-spline with uniform knot vector, start and end at your first and last control points, and has
        additional control possibilities by weighting each control point.

        """
        self.set_open_uniform(control_points, degree=degree)
        self.dxf.flags = self.dxf.flags | self.RATIONAL
        if len(weights) != len(control_points):
            raise DXFValueError('Control point count must be equal to weights count.')
        self.set_weights(weights)

    def set_uniform_rational(self, control_points, weights, degree=3):
        """
        Rational B-spline with uniform knot vector, deos NOT start and end at your first and last control points, and
        has additional control possibilities by weighting each control point.

        """
        self.set_uniform(control_points, degree=degree)
        self.dxf.flags = self.dxf.flags | self.RATIONAL
        if len(weights) != len(control_points):
            raise DXFValueError('Control point count must be equal to weights count.')
        self.set_weights(weights)

    def set_periodic_rational(self, control_points, weights, degree=3):
        """
        Closed rational B-spline with uniform knot vector, start and end at your first control point, and has
        additional control possibilities by weighting each control point.

        """
        self.set_periodic(control_points, degree=degree)
        self.dxf.flags = self.dxf.flags | self.RATIONAL
        if len(weights) != len(control_points):
            raise DXFValueError('Control point count must be equal to weights count.')
        self.set_weights(weights)

    @contextmanager
    def edit_data(self):
        """
        Edit spline data by context manager, usage::

        with spline.edit_data() as data:
            # set uniform knot vector
            data.knots = list(range(spline.dxf.n_control_points+spline.dxf.degree+1))

        Yields: SplineData()

        """
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
