# cython: language_level=3
# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
from typing import List, Tuple, TYPE_CHECKING, Iterable, Sequence
import math
from ezdxf.math import tridiagonal_matrix_solver
from ezdxf.math.ellipse import ConstructionEllipse

from .vector cimport Vec3, isclose, v3_lerp, v3_dist
from .matrix44 cimport Matrix44

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

__all__ = [
    'Bezier4P', 'cubic_bezier_interpolation', 'cubic_bezier_arc_parameters',
    'cubic_bezier_from_arc', 'cubic_bezier_from_ellipse',
    'tangents_cubic_bezier_interpolation',
]


cdef void bernstein3(double t, double *params):
    cdef double t2 = t * t
    cdef double _1_minus_t = 1.0 - t
    cdef double _1_minus_t_square = _1_minus_t * _1_minus_t
    params[0] = _1_minus_t_square * _1_minus_t
    params[1] = 3.0 * _1_minus_t_square * t
    params[2] = 3.0 * _1_minus_t * t2
    params[3] = t2 * t

cdef void bernstein3_d1(double t, double *params):
    cdef double t2 = t * t
    params[0] = -3.0 * (1.0 - t) * (1.0 - t)
    params[1] = 3.0 * (1.0 - 4.0 * t + 3.0 * t2)
    params[2] = 3.0 * t * (2.0 - 3.0 * t)
    params[3] = 3.0 * t2

cdef class Bezier4P:
    cdef Vec3 p0
    cdef Vec3 p1
    cdef Vec3 p2
    cdef Vec3 p3

    def __cinit__(self, defpoints: Sequence['Vertex']):
        if len(defpoints) == 4:
            self.p0 = Vec3(defpoints[0])
            self.p1 = Vec3(defpoints[1])
            self.p2 = Vec3(defpoints[2])
            self.p3 = Vec3(defpoints[3])
        else:
            raise ValueError("Four control points required.")

    @property
    def control_points(self) -> Tuple[Vec3]:
        return self.p0, self.p1, self.p2, self.p3

    def point(self, double t) -> Vec3:
        cdef double params[4]
        if 0.0 <= t <= 1.0:
            bernstein3(t, params)
            return self._get_curve_point(t, params)
        else:
            raise ValueError("t not in range [0 to 1]")

    def tangent(self, double t) -> Vec3:
        cdef double params[4]
        if 0.0 <= t <= 1.0:
            bernstein3_d1(t, params)
            return self._get_curve_point(t, params)
        else:
            raise ValueError("t not in range [0 to 1]")

    cdef Vec3 _get_curve_point(self, double t, double *params):
        cdef Vec3 p0 = self.p0
        cdef Vec3 p1 = self.p1
        cdef Vec3 p2 = self.p2
        cdef Vec3 p3 = self.p3
        cdef Vec3 res = Vec3()
        cdef double a = params[0], b = params[1], c = params[2], d = params[3]
        res.x = p0.x * a + p1.x * b + p2.x * c + p3.x * d
        res.y = p0.y * a + p1.x * b + p2.x * c + p3.x * d
        res.z = p0.z * a + p1.x * b + p2.x * c + p3.x * d
        return res

    def approximate(self, int segments) -> Iterable[Vec3]:
        cdef double params[4]
        cdef double delta_t, t
        cdef int segment

        if segments < 1:
            raise ValueError(segments)
        delta_t = 1.0 / segments
        yield self.p0
        for segment in range(1, segments):
            t = delta_t * segment
            bernstein3(t, params)
            yield self._get_curve_point(t, params)
        yield self.p3

    def flattening(self, double distance, int segments = 4) -> Iterable[Vec3]:
        def subdiv(Vec3 start_point, Vec3 end_point, double start_t,
                   double end_t):
            cdef double mid_t = (start_t + end_t) * 0.5
            bernstein3(mid_t, params)
            cdef Vec3 mid_point = self._get_curve_point(mid_t, params)
            cdef double d = v3_dist(v3_lerp(start_point, end_point, 0.5), mid_point)
            if d < distance:
                yield end_point
            else:
                yield from subdiv(start_point, mid_point, start_t, mid_t)
                yield from subdiv(mid_point, end_point, mid_t, end_t)

        cdef double params[4]
        cdef double dt = 1.0 / segments
        cdef double t0 = 0.0, t1
        cdef Vec3 start_point = self.p0
        cdef Vec3 end_point

        yield start_point
        while t0 < 1.0:
            t1 = t0 + dt
            if isclose(t1, 1.0):
                end_point = self.p3
                t1 = 1.0
            else:
                bernstein3(t1, params)
                end_point = self._get_curve_point(t1, params)
            yield from subdiv(start_point, end_point, t0, t1)
            t0 = t1
            start_point = end_point

    def approximated_length(self, segments: int = 128) -> float:
        cdef double length = 0.0
        cdef bint start_flag = 0
        cdef Vec3 prev_point, point

        for point in self.approximate(segments):
            if start_flag:
                length += v3_dist(prev_point, point)
            else:
                start_flag = 1
            prev_point = point
        return length

    def reverse(self) -> 'Bezier4P':
        return Bezier4P((self.p3, self.p2, self.p1, self.p0))

    def transform(self, Matrix44 m) -> 'Bezier4P':
        defpoints = tuple(m.transform_vertices(self.control_points))
        return Bezier4P(defpoints)

def cubic_bezier_from_arc(
        center: Vec3 = (0, 0), radius: float = 1, start_angle: float = 0,
        end_angle: float = 360,
        segments: int = 1) -> Iterable[Bezier4P]:
    """ Returns an approximation for a circular 2D arc by multiple cubic
    Bézier-curves.

    Args:
        center: circle center as :class:`Vec3` compatible object
        radius: circle radius
        start_angle: start angle in degrees
        end_angle: end angle in degrees
        segments: count of Bèzier-curve segments, at least one segment for each
            quarter (90 deg), 1 for as few as possible.

    .. versionadded:: 0.13

    """
    center = Vec3(center)
    radius = float(radius)
    start_angle = math.radians(start_angle) % math.tau
    end_angle = math.radians(end_angle) % math.tau
    if math.isclose(end_angle, 0.0):
        end_angle = math.tau

    if start_angle > end_angle:
        end_angle += math.tau

    if math.isclose(end_angle - start_angle, 0.0):
        return

    for control_points in cubic_bezier_arc_parameters(
            start_angle, end_angle, segments):
        defpoints = [center + (p * radius) for p in control_points]
        yield Bezier4P(defpoints)

PI_2 = math.pi / 2.0

def cubic_bezier_from_ellipse(
        ellipse: 'ConstructionEllipse',
        segments: int = 1) -> Iterable[Bezier4P]:
    """ Returns an approximation for an elliptic arc by multiple cubic
    Bézier-curves.

    Args:
        ellipse: ellipse parameters as :class:`~ezdxf.math.ConstructionEllipse`
            object
        segments: count of Bèzier-curve segments, at least one segment for each
            quarter (pi/2), 1 for as few as possible.

    .. versionadded:: 0.13

    """
    start_angle = ellipse.start_param % math.tau
    end_angle = ellipse.end_param % math.tau
    if math.isclose(end_angle, 0.0):
        end_angle = math.tau

    if start_angle > end_angle:
        end_angle += math.tau

    if math.isclose(end_angle - start_angle, 0.0):
        return

    def transform(points: Iterable[Vec3]) -> Iterable[Vec3]:
        center = Vec3(ellipse.center)
        x_axis = ellipse.major_axis
        y_axis = ellipse.minor_axis
        for p in points:
            yield center + x_axis * p.x + y_axis * p.y

    for defpoints in cubic_bezier_arc_parameters(
            start_angle, end_angle, segments):
        yield Bezier4P(tuple(transform(defpoints)))

# Circular arc to Bezier curve:
# Source: https://stackoverflow.com/questions/1734745/how-to-create-circle-with-b%C3%A9zier-curves
# Optimization: https://spencermortensen.com/articles/bezier-circle/
# actual c = 0.5522847498307935  = 4.0/3.0*(sqrt(2)-1.0) and max. deviation of ~0.03%
DEFAULT_TANGENT_FACTOR = 4.0 / 3.0  # 1.333333333333333333
# optimal c = 0.551915024494 and max. deviation of ~0.02%
OPTIMIZED_TANGENT_FACTOR = 1.3324407374108935
# Not sure if this is the correct way to apply this optimization,
# so i stick to the original version for now:
TANGENT_FACTOR = DEFAULT_TANGENT_FACTOR

def cubic_bezier_arc_parameters(
        start_angle: float, end_angle: float,
        segments: int = 1) -> Sequence[Vec3]:
    """ Yields cubic Bézier-curve parameters for a circular 2D arc with center
    at (0, 0) and a radius of 1 in the form of [start point, 1. control point,
    2. control point, end point].

    Args:
        start_angle: start angle in radians
        end_angle: end angle in radians (end_angle > start_angle!)
        segments: count of Bèzier-curve segments, at least one segment for each
            quarter (pi/2)

    """
    if segments < 1:
        raise ValueError('Invalid argument segments (>= 1).')
    delta_angle = end_angle - start_angle
    if delta_angle > 0:
        arc_count = max(math.ceil(delta_angle / math.pi * 2.0), segments)
    else:
        raise ValueError('Delta angle from start- to end angle has to be > 0.')

    segment_angle = delta_angle / arc_count
    tangent_length = TANGENT_FACTOR * math.tan(segment_angle / 4.0)

    angle = start_angle
    end_point = None
    for _ in range(arc_count):
        start_point = Vec3.from_angle(
            angle) if end_point is None else end_point
        angle += segment_angle
        end_point = Vec3.from_angle(angle)
        control_point_1 = start_point + (
            -start_point.y * tangent_length, start_point.x * tangent_length)
        control_point_2 = end_point + (
            end_point.y * tangent_length, -end_point.x * tangent_length)
        yield start_point, control_point_1, control_point_2, end_point

def cubic_bezier_interpolation(
        points: Iterable['Vertex']) -> Iterable[Bezier4P]:
    """ Returns an interpolation curve for given data `points` as multiple cubic
    Bézier-curves. Returns n-1 cubic Bézier-curves for n given data points,
    curve i goes from point[i] to point[i+1].

    Args:
        points: data points

    .. versionadded:: 0.13

    """
    # Source: https://towardsdatascience.com/b%C3%A9zier-interpolation-8033e9a262c2
    points = Vec3.list(points)
    if len(points) < 3:
        raise ValueError('At least 3 points required.')

    num = len(points) - 1

    # setup tri-diagonal matrix (a, b, c)
    b = [4.0] * num
    a = [1.0] * num
    c = [1.0] * num
    b[0] = 2.0
    b[num - 1] = 7.0
    a[num - 1] = 2.0

    # setup right-hand side quantities
    points_vector = [points[0] + 2.0 * points[1]]
    points_vector.extend(
        2.0 * (2.0 * points[i] + points[i + 1]) for i in range(1, num - 1))
    points_vector.append(8.0 * points[num - 1] + points[num])

    # solve tri-diagonal linear equation system
    solution = tridiagonal_matrix_solver((a, b, c), points_vector)
    control_points_1 = Vec3.list(solution.rows())
    control_points_2 = [p * 2.0 - cp for p, cp in
                        zip(points[1:], control_points_1[1:])]
    control_points_2.append((control_points_1[num - 1] + points[num]) / 2.0)

    for defpoints in zip(points, control_points_1, control_points_2,
                         points[1:]):
        yield Bezier4P(defpoints)

def tangents_cubic_bezier_interpolation(
        fit_points: List[Vec3], normalize=True) -> List[Vec3]:
    if len(fit_points) < 3:
        raise ValueError('At least 3 points required')

    curves = list(cubic_bezier_interpolation(fit_points))
    tangents = [(curve.control_points[1] - curve.control_points[0]) for curve in
                curves]

    last_points = curves[-1].control_points
    tangents.append(last_points[3] - last_points[2])
    if normalize:
        tangents = [t.normalize() for t in tangents]
    return tangents
