# Purpose: Bezier Curve optimized for 4 control points
# Created: 26.03.2010
# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
from typing import List, TYPE_CHECKING, Iterable, Union, Sequence
import math
from functools import lru_cache
from ezdxf.math import Vector, Vec2, tridiagonal_matrix_solver, Matrix44, linspace
from ezdxf.math.ellipse import ConstructionEllipse

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

__all__ = [
    'Bezier4P', 'cubic_bezier_interpolation', 'cubic_bezier_arc_parameters', 'cubic_bezier_from_arc',
    'cubic_bezier_from_ellipse', 'tangents_cubic_bezier_interpolation',
]


def check_if_in_valid_range(t: float):
    if not (0 <= t <= 1.):
        raise ValueError("t not in range [0 to 1]")


# Optimization:
# cubic P(t) = (1-t)^3*P0 + 3*(1-t)^2*t*P1 + 3*(1-t)*t^2*P2 + t^3*P3
# cubic P(t) = a*P0 + b*P1 + c*P2 + d*P3
# a, b, c, d = bernstein3(t) ... cached
@lru_cache(maxsize=300)
def bernstein3(t: float) -> Sequence[float]:
    """ Bernstein polynom of 3rd degree. """
    t2 = t * t
    _1_minus_t = 1.0 - t
    _1_minus_t_square = _1_minus_t * _1_minus_t
    a = _1_minus_t_square * _1_minus_t
    b = 3.0 * _1_minus_t_square * t
    c = 3.0 * _1_minus_t * t2
    d = t2 * t
    return a, b, c, d


@lru_cache(maxsize=300)
def bernstein3_d1(t: float) -> Sequence[float]:
    """ First derivative of Bernstein polynom of 3rd degree. """
    t2 = t * t
    a = -3.0 * (1.0 - t) ** 2
    b = 3.0 * (1.0 - 4.0 * t + 3.0 * t2)
    c = 3.0 * t * (2.0 - 3.0 * t)
    d = 3.0 * t2
    return a, b, c, d


class Bezier4P:
    """
    Implements an optimized cubic `Bézier curve`_ for exact 4 control points. A `Bézier curve`_ is a parametric
    curve, parameter `t` goes from ``0`` to ``1``, where ``0`` is the first control point and ``1`` is the
    fourth control point.

    Special behavior:

        - 2D control points in, returns 2D results as :class:`~ezdxf.math.Vec2` objects
        - 3D control points in, returns 3D results as :class:`~ezdxf.math.Vector` objects
        - Object is immutable.

    Args:
        defpoints: iterable of definition points as :class:`Vec2` or :class:`Vector` compatible objects.

    """

    def __init__(self, defpoints: Sequence['Vertex']):
        if len(defpoints) == 4:
            is3d = any(len(p) > 2 for p in defpoints)
            vector_class = Vector if is3d else Vec2
            self._control_points = vector_class.tuple(defpoints)
        else:
            raise ValueError("Four control points required.")

    @property
    def control_points(self) -> Sequence[Union[Vector, Vec2]]:
        """ Control points as tuple of :class:`~ezdxf.math.Vector` or :class:`~ezdxf.math.Vec2` objects. """
        return self._control_points

    def tangent(self, t: float) -> Union[Vector, Vec2]:
        """
        Returns direction vector of tangent for location `t` at the Bèzier-curve.

        Args:
            t: curve position in the range ``[0, 1]``

        """
        check_if_in_valid_range(t)
        return self._get_curve_tangent(t)

    def point(self, t: float) -> Union[Vector, Vec2]:
        """
        Returns point for location `t`` at the Bèzier-curve.

        Args:
            t: curve position in the range ``[0, 1]``

        """
        check_if_in_valid_range(t)
        return self._get_curve_point(t)

    def approximate(self, segments: int) -> Iterable[Union[Vector, Vec2]]:
        """
        Approximate `Bézier curve`_ by vertices, yields `segments` + 1 vertices as ``(x, y[, z])`` tuples.

        Args:
            segments: count of segments for approximation

        """
        if segments < 1:
            raise ValueError(segments)
        delta_t = 1. / segments
        yield self._control_points[0]
        for segment in range(1, segments):
            yield self._get_curve_point(delta_t * segment)
        yield self._control_points[3]

    def _get_curve_point(self, t: float) -> Union[Vector, Vec2]:
        b1, b2, b3, b4 = self._control_points
        a, b, c, d = bernstein3(t)
        return b1 * a + b2 * b + b3 * c + b4 * d

    def _get_curve_tangent(self, t: float) -> Union[Vector, Vec2]:
        b1, b2, b3, b4 = self._control_points
        a, b, c, d = bernstein3_d1(t)
        return b1 * a + b2 * b + b3 * c + b4 * d

    def approximated_length(self, segments: int = 128) -> float:
        """ Returns estimated length of Bèzier-curve as approximation by line `segments`. """
        length = 0.
        prev_point = None
        for point in self.approximate(segments):
            if prev_point is not None:
                length += prev_point.distance(point)
            prev_point = point
        return length

    def reverse(self) -> 'Bezier4P':
        """ Returns a new Bèzier-curve with reversed control point order. """
        return Bezier4P(list(reversed(self.control_points)))

    def transform(self, m: Matrix44) -> 'Bezier4P':
        """ General transformation interface, returns a new :class:`Bezier4p` curve and it is always a 3D curve.

        Args:
             m: 4x4 transformation matrix (:class:`ezdxf.math.Matrix44`)

        .. versionadded:: 0.14

        """
        if len(self._control_points[0]) == 2:
            defpoints = Vector.generate(self._control_points)
        else:
            defpoints = self._control_points

        defpoints = tuple(m.transform_vertices(defpoints))
        return Bezier4P(defpoints)


def cubic_bezier_from_arc(
        center: Vector = (0, 0), radius: float = 1, start_angle: float = 0, end_angle: float = 360,
        segments: int = 1) -> Iterable[Bezier4P]:
    """
    Returns an approximation for a circular 2D arc by multiple cubic Bézier-curves.

    Args:
        center: circle center as :class:`Vector` compatible object
        radius: circle radius
        start_angle: start angle in degrees
        end_angle: end angle in degrees
        segments: count of Bèzier-curve segments, at least one segment for each quarter (90 deg),
                  ``1`` for as few as possible.

    .. versionadded:: 0.13

    """
    center = Vector(center)
    radius = float(radius)
    start_angle = math.radians(start_angle) % math.tau
    end_angle = math.radians(end_angle) % math.tau
    if math.isclose(end_angle, 0.0):
        end_angle = math.tau

    if start_angle > end_angle:
        end_angle += math.tau

    if math.isclose(end_angle - start_angle, 0.0):
        return

    for control_points in cubic_bezier_arc_parameters(start_angle, end_angle, segments):
        defpoints = [center + (p * radius) for p in control_points]
        yield Bezier4P(defpoints)


PI_2 = math.pi / 2.0


def cubic_bezier_from_ellipse(ellipse: 'ConstructionEllipse', segments: int = 1) -> Iterable[Bezier4P]:
    """
    Returns an approximation for an elliptic arc by multiple cubic Bézier-curves.

    Args:
        ellipse: ellipse parameters as :class:`~ezdxf.math.ConstructionEllipse` object
        segments: count of Bèzier-curve segments, at least one segment for each quarter (pi/2),
        ``1`` for as few as possible.

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

    def transform(points: Iterable[Vector]) -> Iterable[Vector]:
        center = Vector(ellipse.center)
        x_axis = ellipse.major_axis
        y_axis = ellipse.minor_axis
        for p in points:
            yield center + x_axis * p.x + y_axis * p.y

    for defpoints in cubic_bezier_arc_parameters(start_angle, end_angle, segments):
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


def cubic_bezier_arc_parameters(start_angle: float, end_angle: float, segments: int = 1) -> Sequence[Vector]:
    """
    Yields cubic Bézier-curve parameters for a circular 2D arc with center at (0, 0) and a radius of 1
    in the form of [start point, 1. control point, 2. control point, end point].

    Args:
        start_angle: start angle in radians
        end_angle: end angle in radians (end_angle > start_angle!)
        segments: count of Bèzier-curve segments, at least one segment for each quarter (pi/2)

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
        start_point = Vector.from_angle(angle) if end_point is None else end_point
        angle += segment_angle
        end_point = Vector.from_angle(angle)
        control_point_1 = start_point + (-start_point.y * tangent_length, start_point.x * tangent_length)
        control_point_2 = end_point + (end_point.y * tangent_length, -end_point.x * tangent_length)
        yield start_point, control_point_1, control_point_2, end_point


def cubic_bezier_interpolation(points: Iterable['Vertex']) -> Iterable[Bezier4P]:
    """
    Returns an interpolation curve for given data `points` as multiple cubic Bézier-curves.
    Returns n-1 cubic Bézier-curves for n given data points, curve i goes from point[i] to point[i+1].

    Args:
        points: data points

    .. versionadded:: 0.13

    """
    # Source: https://towardsdatascience.com/b%C3%A9zier-interpolation-8033e9a262c2
    points = Vector.list(points)
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
    points_vector.extend(2.0 * (2.0 * points[i] + points[i + 1]) for i in range(1, num - 1))
    points_vector.append(8.0 * points[num - 1] + points[num])

    # solve tri-diagonal linear equation system
    solution = tridiagonal_matrix_solver((a, b, c), points_vector)
    control_points_1 = Vector.list(solution.rows())
    control_points_2 = [p * 2.0 - cp for p, cp in zip(points[1:], control_points_1[1:])]
    control_points_2.append((control_points_1[num - 1] + points[num]) / 2.0)

    for defpoints in zip(points, control_points_1, control_points_2, points[1:]):
        yield Bezier4P(defpoints)


def tangents_cubic_bezier_interpolation(fit_points: List[Vector], normalize=True) -> List[Vector]:
    if len(fit_points) < 3:
        raise ValueError('At least 3 points required')

    curves = list(cubic_bezier_interpolation(fit_points))
    tangents = [(curve.control_points[1] - curve.control_points[0]) for curve in curves]

    last_points = curves[-1].control_points
    tangents.append(last_points[3] - last_points[2])
    if normalize:
        tangents = [t.normalize() for t in tangents]
    return tangents
