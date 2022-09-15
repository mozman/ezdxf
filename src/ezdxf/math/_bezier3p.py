# Copyright (c) 2021-2022 Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Iterable, Sequence, Type, Optional, TYPE_CHECKING
import math

# The pure Python implementation can't import from ._ctypes or ezdxf.math!
from ._vector import Vec3, Vec2
from ._matrix44 import Matrix44

if TYPE_CHECKING:
    from ._vector import UVec, AnyVec

__all__ = ["Bezier3P"]


def check_if_in_valid_range(t: float) -> None:
    if not (0 <= t <= 1.0):
        raise ValueError("t not in range [0 to 1]")


class Bezier3P:
    """Implements an optimized quadratic `Bézier curve`_ for exact 3 control
    points.

    Special behavior:

        - 2D control points in, returns 2D results as :class:`~ezdxf.math.Vec2` objects
        - 3D control points in, returns 3D results as :class:`~ezdxf.math.Vec3` objects
        - Object is immutable.

    Args:
        defpoints: iterable of definition points as :class:`Vec2` or
            :class:`Vec3` compatible objects.

    """
    __slots__ = ("_control_points", "_offset")

    def __init__(self, defpoints: Sequence[UVec]):
        if len(defpoints) == 3:
            is3d = any(len(p) > 2 for p in defpoints)
            vector_class: Type["AnyVec"] = Vec3 if is3d else Vec2
            # The start point is the curve offset
            offset: "AnyVec" = vector_class(defpoints[0])
            self._offset: "AnyVec" = offset
            # moving the curve to the origin reduces floating point errors:
            self._control_points: Sequence["AnyVec"] = tuple(
                vector_class(p) - offset for p in defpoints
            )
        else:
            raise ValueError("Three control points required.")

    @property
    def control_points(self) -> Sequence["AnyVec"]:
        """Control points as tuple of :class:`~ezdxf.math.Vec3` or
        :class:`~ezdxf.math.Vec2` objects.
        """
        # ezdxf optimization: p0 is always (0, 0, 0)
        p0, p1, p2 = self._control_points
        offset = self._offset
        return offset, p1 + offset, p2 + offset

    def tangent(self, t: float) -> "AnyVec":
        """Returns direction vector of tangent for location `t` at the
        Bèzier-curve.

        Args:
            t: curve position in the range ``[0, 1]``

        """
        check_if_in_valid_range(t)
        return self._get_curve_tangent(t)

    def point(self, t: float) -> "AnyVec":
        """Returns point for location `t`` at the Bèzier-curve.

        Args:
            t: curve position in the range ``[0, 1]``

        """
        check_if_in_valid_range(t)
        return self._get_curve_point(t)

    def approximate(self, segments: int) -> Iterable["AnyVec"]:
        """Approximate `Bézier curve`_ by vertices, yields `segments` + 1
        vertices as ``(x, y[, z])`` tuples.

        Args:
            segments: count of segments for approximation

        """
        if segments < 1:
            raise ValueError(segments)
        delta_t: float = 1.0 / segments
        cp = self.control_points
        yield cp[0]
        for segment in range(1, segments):
            yield self._get_curve_point(delta_t * segment)
        yield cp[2]

    def approximated_length(self, segments: int = 128) -> float:
        """Returns estimated length of Bèzier-curve as approximation by line
        `segments`.
        """
        length: float = 0.0
        prev_point: Optional["AnyVec"] = None
        for point in self.approximate(segments):
            if prev_point is not None:
                length += prev_point.distance(point)
            prev_point = point
        return length

    def flattening(
        self, distance: float, segments: int = 4
    ) -> Iterable["AnyVec"]:
        """Adaptive recursive flattening. The argument `segments` is the
        minimum count of approximation segments, if the distance from the center
        of the approximation segment to the curve is bigger than `distance` the
        segment will be subdivided.

        Args:
            distance: maximum distance from the center of the quadratic (C2)
                curve to the center of the linear (C1) curve between two
                approximation points to determine if a segment should be
                subdivided.
            segments: minimum segment count

        """
        def subdiv(
            start_point: "AnyVec",
            end_point: "AnyVec",
            start_t: float,
            end_t: float,
        ) -> Iterable["AnyVec"]:
            mid_t: float = (start_t + end_t) * 0.5
            mid_point: "AnyVec" = self._get_curve_point(mid_t)
            chk_point: "AnyVec" = start_point.lerp(end_point)
            # center point point is faster than projecting mid point onto
            # vector start -> end:
            d = chk_point.distance(mid_point)
            if d < distance:
                yield end_point
            else:
                yield from subdiv(start_point, mid_point, start_t, mid_t)
                yield from subdiv(mid_point, end_point, mid_t, end_t)

        dt: float = 1.0 / segments
        t0: float = 0.0
        t1: float
        cp = self.control_points
        start_point: "AnyVec" = cp[0]
        end_point: "AnyVec"
        yield start_point
        while t0 < 1.0:
            t1 = t0 + dt
            if math.isclose(t1, 1.0):
                end_point = cp[2]
                t1 = 1.0
            else:
                end_point = self._get_curve_point(t1)
            yield from subdiv(start_point, end_point, t0, t1)
            t0 = t1
            start_point = end_point

    def _get_curve_point(self, t: float) -> "AnyVec":
        # 1st control point (p0) is always (0, 0, 0)
        # => p0 * a is always (0, 0, 0)
        p0, p1, p2 = self._control_points
        _1_minus_t = 1.0 - t
        # a = _1_minus_t * _1_minus_t
        b = 2.0 * t * _1_minus_t
        c = t * t
        # add offset at last - it is maybe very large
        return p1 * b + p2 * c + self._offset

    def _get_curve_tangent(self, t: float) -> "AnyVec":
        # tangent vector is independent from offset location!
        # 1st control point (p0) is always (0, 0, 0)
        # => p0 * a is always (0, 0, 0)
        p0, p1, p2 = self._control_points
        # a = -2.0 * (1.0 - t)
        b = 2.0 - 4.0 * t
        c = 2.0 * t
        return p1 * b + p2 * c

    def reverse(self) -> "Bezier3P":
        """Returns a new Bèzier-curve with reversed control point order."""
        return Bezier3P(list(reversed(self.control_points)))

    def transform(self, m: Matrix44) -> "Bezier3P":
        """General transformation interface, returns a new :class:`Bezier3P`
        curve and it is always a 3D curve.

        Args:
             m: 4x4 transformation matrix (:class:`ezdxf.math.Matrix44`)

        """
        defpoints: Iterable["AnyVec"]
        if len(self._offset) == 2:
            defpoints = Vec3.generate(self.control_points)
        else:
            defpoints = self.control_points
        return Bezier3P(tuple(m.transform_vertices(defpoints)))
