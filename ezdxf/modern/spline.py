# Created: 24.05.2015
# Copyright (c) 2015-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from contextlib import contextmanager
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.const import DXFValueError
from ..lldxf.packedtags import TagArray, VertexTags, replace_tags
from ..algebra.bspline import knot_uniform, knot_open_uniform
from ..lldxf import loader


class KnotTags(TagArray):
    __slots__ = ('value', )
    code = -40  # compatible with DXFTag.code
    VALUE_CODE = 40
    DTYPE = 'f'


class WeightTags(TagArray):
    __slots__ = ('value', )
    code = -41  # compatible with DXFTag.code
    VALUE_CODE = 41
    DTYPE = 'f'


class ControlPoints(VertexTags):
    __slots__ = ('value', )
    code = -10  # compatible with DXFTag.code
    VERTEX_CODE = 10
    VERTEX_SIZE = 3


class FitPoints(VertexTags):
    __slots__ = ('value', )
    code = -11  # compatible with DXFTag.code
    VERTEX_CODE = 11
    VERTEX_SIZE = 3


@loader.register('SPLINE', legacy=False)
def tag_processor(tags):
    spline_tags = tags.get_subclass('AcDbSpline')
    control_points = ControlPoints.from_tags(spline_tags)
    replace_tags(spline_tags, codes=(control_points.VERTEX_CODE, ), packed_data=control_points)
    fit_points = FitPoints.from_tags(spline_tags)
    replace_tags(spline_tags, codes=(fit_points.VERTEX_CODE, ), packed_data=fit_points)
    knots = KnotTags.from_tags(spline_tags)
    replace_tags(spline_tags, codes=(knots.VALUE_CODE, ), packed_data=knots)
    weights = WeightTags.from_tags(spline_tags)
    replace_tags(spline_tags, codes=(weights.VALUE_CODE,), packed_data=weights)
    return tags


_SPLINE_TPL = """0
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
    # 10: Control points (in WCS); one entry per control point
    # 11: Fit points (in WCS); one entry per fit point
    # 40: Knot value (one entry per knot)
    # 41: Weight (if not 1); with multiple group pairs, they are present if all are not 1
})


class Spline(ModernGraphicEntity):
    TEMPLATE = tag_processor(ExtendedTags.from_text(_SPLINE_TPL))
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
        return self.get_flag_state(self.CLOSED, name='flags')

    @closed.setter
    def closed(self, status):
        self.set_flag_state(self.CLOSED, state=status, name='flags')

    def get_knot_values(self):  # group code 40
        return self.AcDbSpline.get_first_tag(KnotTags.code).value

    def set_knot_values(self, knot_values):
        knots = self.AcDbSpline.get_first_tag(KnotTags.code)
        knots.set_values(knot_values)
        self.dxf.n_knots = len(knots.value)

    def get_weights(self):  # group code 41
        return self.AcDbSpline.get_first_tag(WeightTags.code).value

    def set_weights(self, values):
        weights = self.AcDbSpline.get_first_tag(WeightTags.code)
        weights.set_values(values)

    def get_control_points(self):  # group code 10
        return self.AcDbSpline.get_first_tag(ControlPoints.code)

    def set_control_points(self, points):
        vertices = self.get_control_points()
        vertices.clear()
        vertices.extend(points)
        self.dxf.n_control_points = len(vertices)

    def get_fit_points(self):  # group code 11
        return self.AcDbSpline.get_first_tag(FitPoints.code)

    def set_fit_points(self, points):
        vertices = self.get_fit_points()
        vertices.clear()
        vertices.extend(points)
        self.dxf.n_fit_points = len(vertices)

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
