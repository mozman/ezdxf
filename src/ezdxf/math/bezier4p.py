# Purpose: Bezier Curve optimized for 4 control points
# Created: 26.03.2010
# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
from typing import List, TYPE_CHECKING, Iterable, Union
import math
from ezdxf.math import Vector, Vec2

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

    def __init__(self, defpoints: List['Vertex']):
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
        point_gen = self.approximate(segments)
        prev_point = next(point_gen)
        for point in point_gen:
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
