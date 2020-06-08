# Purpose: Bezier Curve optimized for 4 control points
# Created: 26.03.2010
# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
from typing import List, TYPE_CHECKING, Iterable, Union, Sequence
import math
from itertools import chain
from ezdxf.math import Vector, Vec2, Matrix

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


def check_if_in_valid_range(t: float):
    if not (0 <= t <= 1.):
        raise ValueError("t not in range [0 to 1]")


class Bezier4P:
    """
    Implements an optimized cubic `Bézier curve`_ for exact 4 control points. A `Bézier curve`_ is a parametric
    curve, parameter `t` goes from ``0`` to ``1``, where ``0`` is the first control point and ``1`` is the
    fourth control point.

    Special behavior:

        - 2D control points in, returns 2D results as :class:`~ezdxf.math.Vec2` objects
        - 3D control points in, returns 3D results as :class:`~ezdxf.math.Vector` objects

    Args:
        defpoints: iterable of definition points as :class:`Vec2` or :class:`Vector` compatible objects.

    """

    def __init__(self, defpoints: Sequence['Vertex']):
        if len(defpoints) == 4:
            is3d = any(len(p) > 2 for p in defpoints)
            vector_class = Vector if is3d else Vec2
            self._control_points = vector_class.list(defpoints)
        else:
            raise ValueError("Four control points required.")

    @property
    def control_points(self) -> List[Union[Vector, Vec2]]:
        """ control points as list of ``(x, y, z)``, z-axis is ``0`` for 2D curves. """
        return self._control_points

    def tangent(self, t: float) -> Union[Vector, Vec2]:
        """
        Returns direction vector of tangent for location `t` at the `Bézier curve`_.

        Args:
            t: curve position in the range ``[0, 1]``

        """
        check_if_in_valid_range(t)
        return self._get_curve_tangent(t)

    def point(self, t: float) -> Union[Vector, Vec2]:
        """
        Returns point for location `t`` at the `Bézier curve`_.

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
        delta_t = 1. / segments
        yield self._control_points[0]
        for segment in range(1, segments):
            yield self.point(delta_t * segment)
        yield self._control_points[3]

    def _get_curve_point(self, t: float) -> Union[Vector, Vec2]:
        b1, b2, b3, b4 = self._control_points
        one_minus_t = 1. - t
        return b1 * (one_minus_t ** 3) + (b2 * (3. * one_minus_t ** 2 * t)) + (b3 * (3. * one_minus_t * t ** 2)) + (
                b4 * (t ** 3))

    def _get_curve_tangent(self, t: float) -> Union[Vector, Vec2]:
        b1, b2, b3, b4 = self._control_points
        return b1 * (-3. * (1. - t) ** 2) + (b2 * (3. * (1. - 4. * t + 3. * t ** 2))) + (
                b3 * (3. * t * (2. - 3. * t))) + (b4 * (3. * t ** 2))

    def approximated_length(self, segments: int = 100) -> float:
        """ Returns estimated length of `Bézier curve`_ as approximation by line `segments`. """
        length = 0.
        prev_point = None
        for point in self.approximate(segments):
            if prev_point is not None:
                length += prev_point.distance(point)
            prev_point = point
        return length


def cubic_bezier_arc_parameters(start_angle: float, end_angle: float, segments: int = 1):
    """
    Yields cubic Bezier curve parameters for a circular 2D arc with center at (0, 0) and a radius of 1
    in the form of [start point, 1. control point, 2. control point, end point].

    Args:
        start_angle: start angle in radians
        end_angle: end angle in radians (end_angle > start_angle!)
        segments: count of segments, at least one segment for each quarter (pi/2)

    """
    # Source: https://stackoverflow.com/questions/1734745/how-to-create-circle-with-b%C3%A9zier-curves
    if segments < 1:
        raise ValueError('Invalid argument segments (>= 1).')
    delta_angle = end_angle - start_angle
    if delta_angle > 0:
        arc_count = max(math.ceil(delta_angle / math.pi * 2.0), segments)
    else:
        raise ValueError('Delta angle from start- to end angle has to be > 0.')

    segment_angle = delta_angle / arc_count
    tangent_length = 4.0 / 3.0 * math.tan(segment_angle / 4.0)

    angle = start_angle
    end_point = None
    for _ in range(arc_count):
        start_point = Vector.from_angle(angle) if end_point is None else end_point
        angle += segment_angle
        end_point = Vector.from_angle(angle)
        control_point_1 = start_point + (-start_point.y * tangent_length, start_point.x * tangent_length)
        control_point_2 = end_point + (end_point.y * tangent_length, -end_point.x * tangent_length)
        yield start_point, control_point_1, control_point_2, end_point


def bezier_interpolation(points: Iterable['Vertex']) -> List[Bezier4P]:
    """
    Get n-1 cubic Bezier curves for n given data points, the i. curve goes from point[i] to point[i+1].

    Args:
        points: data points

    """
    # Source: https://towardsdatascience.com/b%C3%A9zier-interpolation-8033e9a262c2
    points = Vector.list(points)
    if len(points) < 3:
        raise ValueError('At least 3 points required.')

    num = len(points) - 1
    coefficients = Matrix(shape=(num, num))
    coefficients.set_diagonal(4.0)
    coefficients.set_diagonal(1.0, row_offset=1)
    coefficients.set_diagonal(1.0, col_offset=1)
    coefficients[0, 0] = 2.0
    coefficients[num - 1, num - 1] = 7.0
    coefficients[num - 1, num - 2] = 2.0

    points_vector = [points[0] + 2.0 * points[1]]
    points_vector.extend(2.0 * (2.0 * points[i] + points[i + 1]) for i in range(1, num-1))
    points_vector.append(8.0 * points[num - 1] + points[num])

    # solve linear equation system
    solution = coefficients.gauss_matrix(Matrix(shape=(num, 3), items=chain(points_vector)))
    control_points_1 = Vector.list(solution.rows())
    control_points_2 = [p * 2.0 - cp for p, cp in zip(points[1:], control_points_1[1:])]
    control_points_2.append((control_points_1[num - 1] + points[num]) / 2.0)

    for defpoints in zip(points[:-1], control_points_1, control_points_2, points[1:]):
        yield Bezier4P(defpoints)
