# Purpose: Bezier Curve optimized for 4 control points
# Created: 26.03.2010
# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
from typing import Sequence, List

Vector = Sequence[float]


def check_if_in_valid_range(t: float):
    if not (0 <= t <= 1.):
        raise ValueError("t not in range [0 to 1]")


class Bezier4P:
    """
    Implements an optimized Cubic Bezier Curve with 4 control points.

    Special behavior: 2d in -> 2d out and 3d in -> 3d out!

    """

    def __init__(self, control_points: List[Vector]):
        if len(control_points) == 4:
            is3d = any(len(p) > 2 for p in control_points)
            self.math = D3D if is3d else D2D
            self._cpoints = [self.math.tovector(vector) for vector in control_points]
        else:
            raise ValueError("Four control points required.")

    @property
    def control_points(self) -> List[Vector]:
        return self._cpoints

    def tangent(self, t: float) -> Vector:
        """
        Calculate tangent at parameter t [0, 1].

        Args:
            t: curve position in the range [0, 1]

        Returns: (x, y, z) tuple, a vector which defines the direction of the tangent.

        """
        check_if_in_valid_range(t)
        return self._get_curve_tangent(t)

    def point(self, t: float) -> Vector:
        """
        Calculate curve point at parameter t [0, 1].

        Args:
            t: curve position in the range [0, 1]

        Returns: (x, y, z) tuple

        """
        check_if_in_valid_range(t)
        return self._get_curve_point(t)

    def approximate(self, segments: int):
        delta_t = 1. / segments
        yield self._cpoints[0]
        for segment in range(1, segments):
            yield self.point(delta_t * segment)
        yield self._cpoints[3]

    def _get_curve_point(self, t: float) -> Vector:
        """
        Calculate curve point at parameter t [0, 1].

        Returns: (x, y, z) tuple

        """
        b1, b2, b3, b4 = self._cpoints
        one_minus_t = 1. - t
        m = self.math
        point = m.vmul_scalar(b1, one_minus_t ** 3)
        point = m.vadd(point, m.vmul_scalar(b2, 3. * one_minus_t ** 2 * t))
        point = m.vadd(point, m.vmul_scalar(b3, 3. * one_minus_t * t ** 2))
        point = m.vadd(point, m.vmul_scalar(b4, t ** 3))
        return tuple(point)

    def _get_curve_tangent(self, t: float) -> Vector:
        """
        Calculate tangent at parameter t [0, 1]. Implementation optimized for 4 control points.

        Returns: (x, y, z) tuple, a vector which defines the direction of the tangent.

        """
        b1, b2, b3, b4 = self._cpoints
        m = self.math
        tangent = m.vmul_scalar(b1, -3. * (1. - t) ** 2)
        tangent = m.vadd(tangent, m.vmul_scalar(b2, 3. * (1. - 4. * t + 3. * t ** 2)))
        tangent = m.vadd(tangent, m.vmul_scalar(b3, 3. * t * (2. - 3. * t)))
        tangent = m.vadd(tangent, m.vmul_scalar(b4, 3. * t ** 2))
        return tuple(tangent)

    def approximated_length(self, segments: int = 100) -> float:
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
    def vadd(vector1: Vector, vector2: Vector) -> Vector:
        """ Add vectors """
        return vector1[0] + vector2[0], vector1[1] + vector2[1]

    @staticmethod
    def vmul_scalar(vector: Vector, scalar: float) -> Vector:
        """ Mul vector with scalar """
        return vector[0] * scalar, vector[1] * scalar

    @staticmethod
    def tovector(vector: Vector) -> Vector:
        """ Return a 2d point """
        return float(vector[0]), float(vector[1])

    @staticmethod
    def distance(point1: Vector, point2: Vector) -> float:
        """ calc distance between two 2d points """
        return ((point1[0] - point2[0]) ** 2 +
                (point1[1] - point2[1]) ** 2) ** 0.5


class D3D:
    @staticmethod
    def vadd(vector1: Vector, vector2: Vector) -> Vector:
        """ Add vectors """
        return vector1[0] + vector2[0], vector1[1] + vector2[1], vector1[2] + vector2[2]

    @staticmethod
    def vmul_scalar(vector: Vector, scalar: float) -> Vector:
        """ Mul vector with scalar """
        return vector[0] * scalar, vector[1] * scalar, vector[2] * scalar

    @staticmethod
    def tovector(vector: Vector) -> Vector:
        """ Return a 3d point """
        try:
            z = float(vector[2])
        except IndexError:
            z = 0.
        return float(vector[0]), float(vector[1]), z

    @staticmethod
    def distance(point1: Vector, point2: Vector) -> float:
        """Calc distance between two 3d points """
        return ((point1[0] - point2[0]) ** 2 +
                (point1[1] - point2[1]) ** 2 +
                (point1[2] - point2[2]) ** 2) ** 0.5
