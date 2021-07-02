# Copyright (c) 2010-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Union, Sequence, Tuple, Type
import math
from functools import lru_cache

# The pure Python implementation can't import from ._ctypes or ezdxf.math!
from ._vector import Vec3, Vec2
from ._matrix44 import Matrix44
from ._construct import arc_angle_span_deg

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, AnyVec
    from ezdxf.math.ellipse import ConstructionEllipse

__all__ = [
    "Bezier4P",
    "cubic_bezier_arc_parameters",
    "cubic_bezier_from_arc",
    "cubic_bezier_from_ellipse",
]


# Optimization:
# cubic P(t) = (1-t)^3*P0 + 3*(1-t)^2*t*P1 + 3*(1-t)*t^2*P2 + t^3*P3
# cubic P(t) = a*P0 + b*P1 + c*P2 + d*P3
# a, b, c, d = bernstein3(t) ... cached
@lru_cache(maxsize=300)
def bernstein3(t: float) -> Sequence[float]:
    """Bernstein polynom of 3rd degree."""
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
    """First derivative of Bernstein polynom of 3rd degree."""
    t2 = t * t
    a = -3.0 * (1.0 - t) ** 2
    b = 3.0 * (1.0 - 4.0 * t + 3.0 * t2)
    c = 3.0 * t * (2.0 - 3.0 * t)
    d = 3.0 * t2
    return a, b, c, d


class Bezier4P:
    """Implements an optimized cubic `Bézier curve`_ for exact 4 control points.

    A `Bézier curve`_ is a parametric curve, parameter `t` goes from 0 to 1,
    where 0 is the first control point and 1 is the fourth control point.

    Special behavior:

        - 2D control points in, returns 2D results as :class:`~ezdxf.math.Vec2` objects
        - 3D control points in, returns 3D results as :class:`~ezdxf.math.Vec3` objects
        - Object is immutable.

    Args:
        defpoints: iterable of definition points as :class:`Vec2` or
            :class:`Vec3` compatible objects.

    """

    def __init__(self, defpoints: Sequence["Vertex"]):
        if len(defpoints) == 4:
            is3d = any(len(p) > 2 for p in defpoints)
            vector_class: Type["AnyVec"] = Vec3 if is3d else Vec2
            self._control_points: Sequence["AnyVec"] = vector_class.tuple(
                defpoints
            )
        else:
            raise ValueError("Four control points required.")

    @property
    def control_points(self) -> Sequence["AnyVec"]:
        """Control points as tuple of :class:`~ezdxf.math.Vec3` or
        :class:`~ezdxf.math.Vec2` objects.
        """
        return self._control_points

    def tangent(self, t: float) -> "AnyVec":
        """Returns direction vector of tangent for location `t` at the
        Bèzier-curve.

        Args:
            t: curve position in the range ``[0, 1]``

        """
        if not (0 <= t <= 1.0):
            raise ValueError("t not in range [0 to 1]")
        return self._get_curve_tangent(t)

    def point(self, t: float) -> "AnyVec":
        """Returns point for location `t`` at the Bèzier-curve.

        Args:
            t: curve position in the range ``[0, 1]``

        """
        if not (0 <= t <= 1.0):
            raise ValueError("t not in range [0 to 1]")
        return self._get_curve_point(t)

    def approximate(self, segments: int) -> Iterable["AnyVec"]:
        """Approximate `Bézier curve`_ by vertices, yields `segments` + 1
        vertices as ``(x, y[, z])`` tuples.

        Args:
            segments: count of segments for approximation

        """
        if segments < 1:
            raise ValueError(segments)
        delta_t = 1.0 / segments
        yield self._control_points[0]
        for segment in range(1, segments):
            yield self._get_curve_point(delta_t * segment)
        yield self._control_points[3]

    def flattening(
        self, distance: float, segments: int = 4
    ) -> Iterable[Union[Vec3, Vec2]]:
        """Adaptive recursive flattening. The argument `segments` is the
        minimum count of approximation segments, if the distance from the center
        of the approximation segment to the curve is bigger than `distance` the
        segment will be subdivided.

        Args:
            distance: maximum distance from the center of the cubic (C3)
                curve to the center of the linear (C1) curve between two
                approximation points to determine if a segment should be
                subdivided.
            segments: minimum segment count

        .. versionadded:: 0.15

        """

        def subdiv(
            start_point: "AnyVec",
            end_point: "AnyVec",
            start_t: float,
            end_t: float,
        ) -> Iterable["AnyVec"]:
            mid_t: float = (start_t + end_t) * 0.5
            mid_point: "AnyVec" = self._get_curve_point(mid_t)  # type: ignore
            chk_point: "AnyVec" = start_point.lerp(end_point)
            # center point point is faster than projecting mid point onto
            # vector start -> end:
            if chk_point.distance(mid_point) < distance:
                yield end_point
            else:
                yield from subdiv(start_point, mid_point, start_t, mid_t)
                yield from subdiv(mid_point, end_point, mid_t, end_t)

        dt: float = 1.0 / segments
        t0: float = 0.0
        t1: float
        start_point: "AnyVec" = self._control_points[0]
        end_point: "AnyVec"
        yield start_point
        while t0 < 1.0:
            t1 = t0 + dt
            if math.isclose(t1, 1.0):
                end_point = self._control_points[3]
                t1 = 1.0
            else:
                end_point = self._get_curve_point(t1)
            yield from subdiv(start_point, end_point, t0, t1)
            t0 = t1
            start_point = end_point

    def _get_curve_point(self, t: float) -> Union[Vec3, Vec2]:
        b1, b2, b3, b4 = self._control_points
        a, b, c, d = bernstein3(t)
        return b1 * a + b2 * b + b3 * c + b4 * d

    def _get_curve_tangent(self, t: float) -> Union[Vec3, Vec2]:
        b1, b2, b3, b4 = self._control_points
        a, b, c, d = bernstein3_d1(t)
        return b1 * a + b2 * b + b3 * c + b4 * d

    def approximated_length(self, segments: int = 128) -> float:
        """Returns estimated length of Bèzier-curve as approximation by line
        `segments`.
        """
        length = 0.0
        prev_point = None
        for point in self.approximate(segments):
            if prev_point is not None:
                length += prev_point.distance(point)
            prev_point = point
        return length

    def reverse(self) -> "Bezier4P":
        """Returns a new Bèzier-curve with reversed control point order."""
        return Bezier4P(list(reversed(self.control_points)))

    def transform(self, m: Matrix44) -> "Bezier4P":
        """General transformation interface, returns a new :class:`Bezier4p`
        curve and it is always a 3D curve.

        Args:
             m: 4x4 transformation matrix (:class:`ezdxf.math.Matrix44`)

        .. versionadded:: 0.14

        """
        defpoints: Iterable["AnyVec"]
        if len(self._control_points[0]) == 2:
            defpoints = Vec3.generate(self._control_points)
        else:
            defpoints = self._control_points
        return Bezier4P(tuple(m.transform_vertices(defpoints)))


def cubic_bezier_from_arc(
    center: "Vertex" = (0, 0, 0),
    radius: float = 1,
    start_angle: float = 0,
    end_angle: float = 360,
    segments: int = 1,
) -> Iterable[Bezier4P]:
    """Returns an approximation for a circular 2D arc by multiple cubic
    Bézier-curves.

    Args:
        center: circle center as :class:`Vec3` compatible object
        radius: circle radius
        start_angle: start angle in degrees
        end_angle: end angle in degrees
        segments: count of Bèzier-curve segments, at least one segment for each
            quarter (90 deg), 1 for as few as possible.

    """
    center_: Vec3 = Vec3(center)
    radius = float(radius)
    angle_span: float = arc_angle_span_deg(start_angle, end_angle)
    if abs(angle_span) < 1e-9:
        return

    s: float = start_angle
    start_angle = math.radians(s) % math.tau
    end_angle = math.radians(s + angle_span)
    while start_angle > end_angle:
        end_angle += math.tau

    for control_points in cubic_bezier_arc_parameters(
        start_angle, end_angle, segments
    ):
        defpoints = [center_ + (p * radius) for p in control_points]
        yield Bezier4P(defpoints)


PI_2: float = math.pi / 2.0


def cubic_bezier_from_ellipse(
    ellipse: "ConstructionEllipse", segments: int = 1
) -> Iterable[Bezier4P]:
    """Returns an approximation for an elliptic arc by multiple cubic
    Bézier-curves.

    Args:
        ellipse: ellipse parameters as :class:`~ezdxf.math.ConstructionEllipse`
            object
        segments: count of Bèzier-curve segments, at least one segment for each
            quarter (π/2), 1 for as few as possible.

    """
    param_span: float = ellipse.param_span
    if abs(param_span) < 1e-9:
        return
    start_angle: float = ellipse.start_param % math.tau
    end_angle: float = start_angle + param_span
    while start_angle > end_angle:
        end_angle += math.tau

    def transform(points: Iterable[Vec3]) -> Iterable[Vec3]:
        center = Vec3(ellipse.center)
        x_axis: Vec3 = ellipse.major_axis
        y_axis: Vec3 = ellipse.minor_axis
        for p in points:
            yield center + x_axis * p.x + y_axis * p.y

    for defpoints in cubic_bezier_arc_parameters(
        start_angle, end_angle, segments
    ):
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
    start_angle: float, end_angle: float, segments: int = 1
) -> Iterable[Tuple[Vec3, Vec3, Vec3, Vec3]]:
    """Yields cubic Bézier-curve parameters for a circular 2D arc with center
    at (0, 0) and a radius of 1 in the form of [start point, 1. control point,
    2. control point, end point].

    Args:
        start_angle: start angle in radians
        end_angle: end angle in radians (end_angle > start_angle!)
        segments: count of Bèzier-curve segments, at least one segment for each
            quarter (π/2)

    """
    if segments < 1:
        raise ValueError("Invalid argument segments (>= 1).")
    delta_angle: float = end_angle - start_angle
    if delta_angle > 0:
        arc_count = max(math.ceil(delta_angle / math.pi * 2.0), segments)
    else:
        raise ValueError("Delta angle from start- to end angle has to be > 0.")

    segment_angle: float = delta_angle / arc_count
    tangent_length: float = TANGENT_FACTOR * math.tan(segment_angle / 4.0)

    angle: float = start_angle
    end_point: Vec3 = Vec3.from_angle(angle)
    for _ in range(arc_count):
        start_point = end_point
        angle += segment_angle
        end_point = Vec3.from_angle(angle)
        control_point_1 = start_point + (
            -start_point.y * tangent_length,
            start_point.x * tangent_length,
        )
        control_point_2 = end_point + (
            end_point.y * tangent_length,
            -end_point.x * tangent_length,
        )
        yield start_point, control_point_1, control_point_2, end_point
