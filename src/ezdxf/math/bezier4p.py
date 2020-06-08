# Purpose: Bezier Curve optimized for 4 control points
# Created: 26.03.2010
# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
from typing import List, TYPE_CHECKING, Iterable, Sequence
import math
from ezdxf.math import Vector

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

        - 2D control points in, returns 2D results as ``(x, y)`` tuples
        - 3D control points in, returns 3D results as ``(x, y, z)`` tuples

    Args:
        defpoints: iterable of definition points as ``(x, y[, z])`` tuples

    """

    def __init__(self, defpoints: List[Sequence[float]]):
        if len(defpoints) == 4:
            is3d = any(len(p) > 2 for p in defpoints)
            self.math = D3D if is3d else D2D
            self._cpoints = [self.math.tovector(vector) for vector in defpoints]
        else:
            raise ValueError("Four control points required.")

    @property
    def control_points(self) -> List[Sequence[float]]:
        """ control points as list of ``(x, y, z)``, z-axis is ``0`` for 2D curves. """
        return self._cpoints

    def tangent(self, t: float) -> Sequence[float]:
        """
        Returns direction vector of tangent for location `t` at the `Bézier curve`_.

        Args:
            t: curve position in the range ``[0, 1]``

        Returns:
            tuple: ``(x, y[, z])`` tuple, the direction vector at location `t`.

        """
        check_if_in_valid_range(t)
        return self._get_curve_tangent(t)

    def point(self, t: float) -> Sequence[float]:
        """
        Returns point for location `t`` at the `Bézier curve`_.

        Args:
            t: curve position in the range ``[0, 1]``

        Returns:
            tuple: ``(x, y[, z])`` tuple

        """
        check_if_in_valid_range(t)
        return self._get_curve_point(t)

    def approximate(self, segments: int) -> Iterable[Sequence[float]]:
        """
        Approximate `Bézier curve`_ by vertices, yields `segments` + 1 vertices as ``(x, y[, z])`` tuples.

        Args:
            segments: count of segments for approximation

        Returns:
            iterable of ``(x, y[, z])`` tuples

        """
        delta_t = 1. / segments
        yield self._cpoints[0]
        for segment in range(1, segments):
            yield self.point(delta_t * segment)
        yield self._cpoints[3]

    def _get_curve_point(self, t: float) -> 'Vertex':
        b1, b2, b3, b4 = self._cpoints
        one_minus_t = 1. - t
        m = self.math
        point = m.vmul_scalar(b1, one_minus_t ** 3)
        point = m.vadd(point, m.vmul_scalar(b2, 3. * one_minus_t ** 2 * t))
        point = m.vadd(point, m.vmul_scalar(b3, 3. * one_minus_t * t ** 2))
        point = m.vadd(point, m.vmul_scalar(b4, t ** 3))
        return tuple(point)

    def _get_curve_tangent(self, t: float) -> 'Vertex':
        b1, b2, b3, b4 = self._cpoints
        m = self.math
        tangent = m.vmul_scalar(b1, -3. * (1. - t) ** 2)
        tangent = m.vadd(tangent, m.vmul_scalar(b2, 3. * (1. - 4. * t + 3. * t ** 2)))
        tangent = m.vadd(tangent, m.vmul_scalar(b3, 3. * t * (2. - 3. * t)))
        tangent = m.vadd(tangent, m.vmul_scalar(b4, 3. * t ** 2))
        return tuple(tangent)

    def approximated_length(self, segments: int = 100) -> float:
        """ Returns estimated length of `Bézier curve`_ as approximation by line `segments`. """
        length = 0.
        point_gen = self.approximate(segments)
        prev_point = next(point_gen)
        distance = self.math.distance
        for point in point_gen:
            length += distance(prev_point, point)
            prev_point = point
        return length


class D2D:
    @staticmethod
    def vadd(vector1: 'Vertex', vector2: 'Vertex') -> 'Vertex':
        """ Returns addition of `vector1` and `vector2`. """
        return vector1[0] + vector2[0], vector1[1] + vector2[1]

    @staticmethod
    def vmul_scalar(vector: 'Vertex', scalar: float) -> 'Vertex':
        """ Returns multiplication of `vector` by `scalar` """
        return vector[0] * scalar, vector[1] * scalar

    @staticmethod
    def tovector(vector: 'Vertex') -> 'Vertex':
        """ Returns a 2D point. """
        return float(vector[0]), float(vector[1])

    @staticmethod
    def distance(point1: 'Vertex', point2: 'Vertex') -> float:
        """ Returns distance between two 2D points. """
        return ((point1[0] - point2[0]) ** 2 +
                (point1[1] - point2[1]) ** 2) ** 0.5


class D3D:
    @staticmethod
    def vadd(vector1: 'Vertex', vector2: 'Vertex') -> 'Vertex':
        """ Returns addition of `vector1` and `vector2`. """
        return vector1[0] + vector2[0], vector1[1] + vector2[1], vector1[2] + vector2[2]

    @staticmethod
    def vmul_scalar(vector: 'Vertex', scalar: float) -> 'Vertex':
        """ Returns multiplication of `vector` by `scalar` """
        return vector[0] * scalar, vector[1] * scalar, vector[2] * scalar

    @staticmethod
    def tovector(vector: 'Vertex') -> 'Vertex':
        """ Returns a 3D point. """
        try:
            z = float(vector[2])
        except IndexError:
            z = 0.
        return float(vector[0]), float(vector[1]), z

    @staticmethod
    def distance(point1: 'Vertex', point2: 'Vertex') -> float:
        """ Returns distance between two 3D points. """
        return ((point1[0] - point2[0]) ** 2 +
                (point1[1] - point2[1]) ** 2 +
                (point1[2] - point2[2]) ** 2) ** 0.5


def cubic_bezier_arc_parameters(start_angle: float, end_angle: float, segments: int = 1):
    """
    Yields cubic Bezier curve parameters for a circular 2D arc with center at (0, 0) and a radius of 1
    in the form of [start point, 1. control point, 2. control point, endpoint].

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
