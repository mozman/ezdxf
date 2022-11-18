# Copyright (c) 2011-2022, Manfred Moitzi
# License: MIT License
# These are the pure Python implementations of the Cython accelerated
# construction tools: ezdxf/acc/construct.pyx
from __future__ import annotations
from typing import Iterable, Sequence, Optional, TYPE_CHECKING
import math

# The pure Python implementation can't import from ._ctypes or ezdxf.math!
from ._vector import Vec2, Vec3

if TYPE_CHECKING:
    from ezdxf.math import UVec

TOLERANCE = 1e-10
RAD_ABS_TOL = 1e-15
DEG_ABS_TOL = 1e-13


def has_clockwise_orientation(vertices: Iterable[UVec]) -> bool:
    """Returns ``True`` if the given 2D `vertices` have clockwise orientation.
    Ignores the z-axis of all vertices.

    Args:
        vertices: iterable of :class:`Vec2` compatible objects

    Raises:
        ValueError: less than 3 vertices

    """
    vertices = Vec2.list(vertices)
    if len(vertices) < 3:
        raise ValueError("At least 3 vertices required.")

    # close polygon:
    if not vertices[0].isclose(vertices[-1]):
        vertices.append(vertices[0])

    return (
        sum(
            (p2.x - p1.x) * (p2.y + p1.y)
            for p1, p2 in zip(vertices, vertices[1:])
        )
        > 0.0
    )


def intersection_line_line_2d(
    line1: Sequence[Vec2],
    line2: Sequence[Vec2],
    virtual=True,
    abs_tol=TOLERANCE,
) -> Optional[Vec2]:
    """
    Compute the intersection of two lines in the xy-plane.

    Args:
        line1: start- and end point of first line to test
            e.g. ((x1, y1), (x2, y2)).
        line2: start- and end point of second line to test
            e.g. ((x3, y3), (x4, y4)).
        virtual: ``True`` returns any intersection point, ``False`` returns
            only real intersection points.
        abs_tol: tolerance for intersection test.

    Returns:
        ``None`` if there is no intersection point (parallel lines) or
        intersection point as :class:`Vec2`

    """
    # Algorithm based on: http://paulbourke.net/geometry/pointlineplane/
    # chapter: Intersection point of two line segments in 2 dimensions
    s1, s2 = line1  # the subject line
    c1, c2 = line2  # the clipping line
    s1x = s1.x
    s1y = s1.y
    s2x = s2.x
    s2y = s2.y
    c1x = c1.x
    c1y = c1.y
    c2x = c2.x
    c2y = c2.y

    den = (c2y - c1y) * (s2x - s1x) - (c2x - c1x) * (s2y - s1y)
    if math.fabs(den) <= abs_tol:
        return None

    us = ((c2x - c1x) * (s1y - c1y) - (c2y - c1y) * (s1x - c1x)) / den
    intersection_point = Vec2(s1x + us * (s2x - s1x), s1y + us * (s2y - s1y))
    if virtual:
        return intersection_point

    # 0 = intersection point is the start point of the line
    # 1 = intersection point is the end point of the line
    # otherwise: linear interpolation
    lwr = 0.0  # tolerances required?
    upr = 1.0  # tolerances required?
    if lwr <= us <= upr:  # intersection point is on the subject line
        uc = ((s2x - s1x) * (s1y - c1y) - (s2y - s1y) * (s1x - c1x)) / den
        if lwr <= uc <= upr:  # intersection point is on the clipping line
            return intersection_point
    return None


def _determinant(v1, v2, v3) -> float:
    """Returns determinant."""
    e11, e12, e13 = v1
    e21, e22, e23 = v2
    e31, e32, e33 = v3

    return (
        e11 * e22 * e33
        + e12 * e23 * e31
        + e13 * e21 * e32
        - e13 * e22 * e31
        - e11 * e23 * e32
        - e12 * e21 * e33
    )


def intersection_ray_ray_3d(
    ray1: Sequence[Vec3], ray2: Sequence[Vec3], abs_tol=TOLERANCE
) -> Sequence[Vec3]:
    """
    Calculate intersection of two 3D rays, returns a 0-tuple for parallel rays,
    a 1-tuple for intersecting rays and a 2-tuple for not intersecting and not
    parallel rays with points of the closest approach on each ray.

    Args:
        ray1: first ray as tuple of two points as :class:`Vec3` objects
        ray2: second ray as tuple of two points as :class:`Vec3` objects
        abs_tol: absolute tolerance for comparisons

    """
    # source: http://www.realtimerendering.com/intersections.html#I304
    o1, p1 = ray1
    d1 = (p1 - o1).normalize()
    o2, p2 = ray2
    d2 = (p2 - o2).normalize()
    d1xd2 = d1.cross(d2)
    denominator = d1xd2.magnitude_square
    if denominator <= abs_tol:
        # ray1 is parallel to ray2
        return tuple()
    else:
        o2_o1 = o2 - o1
        det1 = _determinant(o2_o1, d2, d1xd2)
        det2 = _determinant(o2_o1, d1, d1xd2)
        p1 = o1 + d1 * (det1 / denominator)
        p2 = o2 + d2 * (det2 / denominator)
        if p1.isclose(p2, abs_tol=abs_tol):
            # ray1 and ray2 have an intersection point
            return (p1,)
        else:
            # ray1 and ray2 do not have an intersection point,
            # p1 and p2 are the points of closest approach on each ray
            return p1, p2


def arc_angle_span_deg(start: float, end: float) -> float:
    """Returns the counter-clockwise angle span from `start` to `end` in degrees.

    Returns the angle span in the range of [0, 360], 360 is a full circle.
    Full circle handling is a special case, because normalization of angles
    which describe a full circle would return 0 if treated as regular angles.
    e.g. (0, 360) → 360, (0, -360) → 360, (180, -180) → 360.
    Input angles with the same value always return 0 by definition: (0, 0) → 0,
    (-180, -180) → 0, (360, 360) → 0.

    """
    # Input values are equal, returns 0 by definition:
    if math.isclose(start, end, abs_tol=DEG_ABS_TOL):
        return 0.0

    # Normalized start- and end angles are equal, but input values are
    # different, returns 360 by definition:
    start %= 360.0
    if math.isclose(start, end % 360.0, abs_tol=DEG_ABS_TOL):
        return 360.0

    # Special treatment for end angle == 360 deg:
    if not math.isclose(end, 360.0, abs_tol=DEG_ABS_TOL):
        end %= 360.0

    if end < start:
        end += 360.0
    return end - start


def arc_angle_span_rad(start: float, end: float) -> float:
    """Returns the counter-clockwise angle span from `start` to `end` in radians.

    Returns the angle span in the range of [0, 2π], 2π is a full circle.
    Full circle handling is a special case, because normalization of angles
    which describe a full circle would return 0 if treated as regular angles.
    e.g. (0, 2π) → 2π, (0, -2π) → 2π, (π, -π) → 2π.
    Input angles with the same value always return 0 by definition: (0, 0) → 0,
    (-π, -π) → 0, (2π, 2π) → 0.

    """
    tau = math.tau
    # Input values are equal, returns 0 by definition:
    if math.isclose(start, end, abs_tol=RAD_ABS_TOL):
        return 0.0

    # Normalized start- and end angles are equal, but input values are
    # different, returns 360 by definition:
    start %= tau
    if math.isclose(start, end % tau, abs_tol=RAD_ABS_TOL):
        return tau

    # Special treatment for end angle == 2π:
    if not math.isclose(end, tau, abs_tol=RAD_ABS_TOL):
        end %= tau

    if end < start:
        end += tau
    return end - start
