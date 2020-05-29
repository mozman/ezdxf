# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Dict
import math
from collections import namedtuple
from .vector import Vector, NULLVEC, X_AXIS, Z_AXIS
from .matrix44 import Matrix44
from .ucs import OCS
from .construct2d import rytz_axis_construction, enclosing_angles, linspace
from ezdxf.math import bspline

Params = namedtuple('Params', 'center major_axis minor_axis extrusion ratio start end')
pi2 = math.pi / 2

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

QUARTER_PARAMS = [0, math.pi * .5, math.pi, math.pi * 1.5]
HALF_PI = math.pi / 2.0


class ConstructionEllipse:
    """
    This is a helper class to create parameters for 3D ellipses.

    Args:
        center: 3D center point
        major_axis: major axis as 3D vector
        extrusion: normal vector of ellipse plane
        ratio: ratio of minor axis to major axis
        start: start param in radians
        end: end param in radians
        ccw: is counter clockwise flag - swaps start- and end param if ``False``

    """

    def __init__(self, center: 'Vertex' = NULLVEC, major_axis: 'Vertex' = X_AXIS, extrusion: 'Vertex' = Z_AXIS,
                 ratio: float = 1, start: float = 0, end: float = math.tau, ccw: bool = True):
        self.center = Vector(center)
        self.major_axis = Vector(major_axis)
        self.extrusion = Vector(extrusion)
        self.ratio = float(ratio)
        self.start_param = float(start)
        self.end_param = float(end)
        if not ccw:
            self.start_param, self.end_param = self.end_param, self.start_param
        self.minor_axis = minor_axis(self.major_axis, self.extrusion, self.ratio)

    @classmethod
    def from_arc(cls, center: 'Vertex' = NULLVEC, radius: float = 1, extrusion: 'Vertex' = Z_AXIS, start: float = 0,
                 end: float = 360, ccw: bool = True) -> 'ConstructionEllipse':
        """ Returns :class:`ConstructionEllipse` from arc or circle.

        Arc and Circle parameters defined in OCS.

        Args:
             center: center in OCS
             radius: arc or circle radius
             extrusion: OCS extrusion vector
             start: start angle in degrees
             end: end angle in degrees
             ccw: arc curve goes counter clockwise from start to end if ``True``
        """
        ratio = 1.0
        ocs = OCS(extrusion)
        # todo: start- and end angle in OCS!
        start_param = math.radians(start)
        end_param = math.radians(end)
        center = ocs.to_wcs(center)
        major_axis = ocs.to_wcs(Vector(radius, 0, 0))
        return cls(center, major_axis, extrusion, ratio, start_param, end_param, bool(ccw))

    def __copy__(self):
        return ConstructionEllipse(self.center, self.major_axis, self.extrusion, self.ratio, self.start_param,
                                   self.end_param)

    @property
    def start_point(self) -> Vector:
        """ Returns start point of ellipse as Vector. """
        return vertex(self.start_param, self.major_axis, self.minor_axis, self.center, self.ratio)

    @property
    def end_point(self) -> Vector:
        """ Returns end point of ellipse as Vector. """
        return vertex(self.end_param, self.major_axis, self.minor_axis, self.center, self.ratio)

    def dxfattribs(self) -> Dict:
        """ Returns required DXF attributes to build an ELLIPSE entity.

        Entity ELLIPSE has always a ratio in range from 1e-6 to 1.

        """
        if self.ratio > 1:
            e = self.__copy__()
            e.swap_axis()
        else:
            e = self
        return {
            'center': e.center,
            'major_axis': e.major_axis,
            'extrusion': e.extrusion,
            'ratio': max(e.ratio, 1e-6),
            'start_param': e.start_param,
            'end_param': e.end_param,
        }

    def main_axis_points(self) -> Iterable[Vector]:
        """ Yields main axis points of ellipse in the range from start- to end param. """
        start = self.start_param
        end = self.end_param
        for param in QUARTER_PARAMS:
            if enclosing_angles(param, start, end):
                yield vertex(param, self.major_axis, self.minor_axis, self.center, self.ratio)

    def transform(self, m: Matrix44) -> None:
        """ Transform ellipse in place by transformation matrix `m`. """
        params = Params(self.center, self.major_axis, self.minor_axis, self.extrusion, self.ratio, self.start_param,
                        self.end_param)
        (self.center,
         self.major_axis,
         self.minor_axis,
         self.extrusion,
         self.ratio,
         self.start_param,
         self.end_param) = transform(params, m)

    def params(self, num: int) -> Iterable[float]:
        """ Returns `num` params from start- to end param in counter clockwise order.

        All params are normalized in the range from [0, 2pi).

        """
        yield from get_params(self.start_param, self.end_param, num)

    def vertices(self, params: Iterable[float]) -> Iterable[Vector]:
        """
        Yields vertices on ellipse for iterable `params` in WCS.

        Args:
            params: param values in the range from ``0`` to ``2*pi`` in radians, param goes counter clockwise around the
                    extrusion vector, major_axis = local x-axis = 0 rad.

        """
        center = self.center
        ratio = self.ratio
        x_axis = self.major_axis.normalize()
        y_axis = self.minor_axis.normalize()
        radius_x = self.major_axis.magnitude
        radius_y = radius_x * ratio

        for param in params:
            x = math.cos(param) * radius_x * x_axis
            y = math.sin(param) * radius_y * y_axis
            yield center + x + y

    def swap_axis(self) -> None:
        """ Swap axis and adjust start- and end parameter. """
        self.major_axis = self.minor_axis
        ratio = 1.0 / self.ratio
        self.ratio = max(ratio, 1e-6)
        self.minor_axis = minor_axis(self.major_axis, self.extrusion, self.ratio)

        start_param = self.start_param
        end_param = self.end_param
        if math.isclose(start_param, 0) and math.isclose(end_param, math.tau):
            return
        self.start_param = (start_param - HALF_PI) % math.tau
        self.end_param = (end_param - HALF_PI) % math.tau

    def spline(self, num: int = 16) -> bspline.BSpline:
        """ Returns a curve approximation as spline with `num` control points. """
        fit_points = list(self.vertices(self.params(num)))
        count = len(fit_points)
        degree = 2
        order = degree + 1
        t_vector = list(bspline.uniform_t_vector(fit_points))
        knots = list(bspline.control_frame_knots(count - 1, degree, t_vector))
        control_points = bspline.global_curve_interpolation(fit_points, degree, t_vector, knots)
        spline = bspline.BSpline(control_points, order=order, knots=knots)
        spline.t_array = t_vector
        return spline


def transform(params: Params, m: Matrix44) -> Params:
    new_center = m.transform(params.center)
    old_start_param = start_param = params.start % math.tau
    old_end_param = end_param = params.end % math.tau
    old_minor_axis = minor_axis(params.major_axis, params.extrusion, params.ratio)
    new_major_axis, new_minor_axis = m.transform_directions((params.major_axis, old_minor_axis))

    # Original ellipse parameters stay untouched until end of transformation
    if not math.isclose(new_major_axis.dot(new_minor_axis), 0, abs_tol=1e-9):
        new_major_axis, new_minor_axis, new_ratio = rytz_axis_construction(new_major_axis, new_minor_axis)
        adjust_params = True
    else:
        new_ratio = new_minor_axis.magnitude / new_major_axis.magnitude
        adjust_params = False

    if adjust_params and not math.isclose(start_param, end_param, abs_tol=1e-9):
        # open ellipse, adjusting start- and end parameter
        x_axis = new_major_axis.normalize()
        y_axis = new_minor_axis.normalize()
        old_param_span = (end_param - start_param) % math.tau

        def param(vec: 'Vector') -> float:
            dy = y_axis.dot(vec) / new_ratio  # adjust to circle
            dx = x_axis.dot(vec)
            return math.atan2(dy, dx) % math.tau

        # transformed start- and end point of old ellipse
        start_point = m.transform(vertex(start_param, params.major_axis, old_minor_axis, params.center, params.ratio))
        end_point = m.transform(vertex(end_param, params.major_axis, old_minor_axis, params.center, params.ratio))

        start_param = param(start_point - new_center)
        end_param = param(end_point - new_center)

        # Test if drawing the correct side of the curve
        if not math.isclose(old_param_span, math.pi, abs_tol=1e-9):
            # equal param span check works well, except for a span of exact pi (180 deg)
            new_param_span = (end_param - start_param) % math.tau
            if not math.isclose(old_param_span, new_param_span, abs_tol=1e-9):
                start_param, end_param = end_param, start_param
        else:  # param span is exact pi (180 deg)
            # expensive but it seem to work:
            old_chk_point = m.transform(vertex(
                mid_param(old_start_param, old_end_param),
                params.major_axis,
                old_minor_axis,
                params.center,
                params.ratio,
            ))
            new_chk_point = vertex(
                mid_param(start_param, end_param),
                new_major_axis,
                new_minor_axis,
                new_center,
                new_ratio,
            )
            if not old_chk_point.isclose(new_chk_point, abs_tol=1e-9):
                start_param, end_param = end_param, start_param

    new_extrusion = new_major_axis.cross(new_minor_axis).normalize()
    if new_ratio > 1:
        new_major_axis = minor_axis(new_major_axis, new_extrusion, new_ratio)
        new_ratio = 1.0 / new_ratio
        new_minor_axis = minor_axis(new_major_axis, new_extrusion, new_ratio)
        if not (math.isclose(start_param, 0) and math.isclose(end_param, math.tau)):
            start_param -= pi2
            end_param -= pi2

    # normalize start- and end params
    start_param = start_param % math.tau
    end_param = end_param % math.tau
    if math.isclose(start_param, end_param):
        start_param = 0.0
        end_param = math.tau

    return Params(
        new_center,
        new_major_axis,
        new_minor_axis,
        new_extrusion,
        max(new_ratio, 1e-6),
        start_param,
        end_param,
    )


def mid_param(start: float, end: float) -> float:
    if end < start:
        end += math.tau
    return (start + end) / 2.0


def minor_axis(major_axis: Vector, extrusion: Vector, ratio: float) -> Vector:
    return extrusion.cross(major_axis).normalize(major_axis.magnitude * ratio)


def vertex(param: float, major_axis: Vector, minor_axis: Vector, center: Vector, ratio: float) -> Vector:
    x_axis = major_axis.normalize()
    y_axis = minor_axis.normalize()
    radius_x = major_axis.magnitude
    radius_y = radius_x * ratio
    x = math.cos(param) * radius_x * x_axis
    y = math.sin(param) * radius_y * y_axis
    return center + x + y


def get_params(start: float, end: float, num: int) -> Iterable[float]:
    """ Returns `num` params from start- to end param in counter clockwise order.

    All params are normalized in the range from [0, 2pi).

    """
    if num < 2:
        raise ValueError('num >= 2')
    if end <= start:
        end += math.tau

    for param in linspace(start, end, num):
        yield param % math.tau
