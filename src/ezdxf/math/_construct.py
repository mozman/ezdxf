# Copyright (c) 2010-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Sequence, Optional, Tuple
import math

# The pure Python implementation can't import from ._ctypes or ezdxf.math!
from ._vector import Vec2, Vec3

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex
TOLERANCE = 1e-10


def has_clockwise_orientation(vertices: Iterable["Vertex"]) -> bool:
    """Returns True if 2D `vertices` have clockwise orientation. Ignores
    z-axis of all vertices.

    Args:
        vertices: iterable of :class:`Vec2` compatible objects

    Raises:
        ValueError: less than 3 vertices

    """
    vertices = Vec2.list(vertices)
    if len(vertices) < 3:
        raise ValueError("At least 3 vertices required.")

    # Close polygon:
    if not vertices[0].isclose(vertices[-1]):
        vertices.append(vertices[0])

    return (
        sum(
            (p2.x - p1.x) * (p2.y + p1.y)
            for p1, p2 in zip(vertices, vertices[1:])
        )
        > 0
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
    # Sources:
    # compas: https://github.com/compas-dev/compas/blob/master/src/compas/geometry/_core/intersections.py (MIT)
    # wikipedia: https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection

    a, b = line1
    c, d = line2

    x1, y1 = a.x, a.y
    x2, y2 = b.x, b.y
    x3, y3 = c.x, c.y
    x4, y4 = d.x, d.y

    x1_x2 = x1 - x2
    y3_y4 = y3 - y4
    y1_y2 = y1 - y2
    x3_x4 = x3 - x4

    d = x1_x2 * y3_y4 - y1_y2 * x3_x4

    if math.fabs(d) <= abs_tol:
        return None

    a = x1 * y2 - y1 * x2
    b = x3 * y4 - y3 * x4
    x = (a * x3_x4 - x1_x2 * b) / d
    y = (a * y3_y4 - y1_y2 * b) / d

    if not virtual:
        if x1 > x2:
            in_range = (x2 - abs_tol) <= x <= (x1 + abs_tol)
        else:
            in_range = (x1 - abs_tol) <= x <= (x2 + abs_tol)

        if not in_range:
            return None

        if x3 > x4:
            in_range = (x4 - abs_tol) <= x <= (x3 + abs_tol)
        else:
            in_range = (x3 - abs_tol) <= x <= (x4 + abs_tol)

        if not in_range:
            return None

        if y1 > y2:
            in_range = (y2 - abs_tol) <= y <= (y1 + abs_tol)
        else:
            in_range = (y1 - abs_tol) <= y <= (y2 + abs_tol)

        if not in_range:
            return None

        if y3 > y4:
            in_range = (y4 - abs_tol) <= y <= (y3 + abs_tol)
        else:
            in_range = (y3 - abs_tol) <= y <= (y4 + abs_tol)

        if not in_range:
            return None

    return Vec2(x, y)


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
    ray1: Tuple[Vec3, Vec3], ray2: Tuple[Vec3, Vec3], abs_tol=TOLERANCE
) -> Sequence[Vec3]:
    """
    Calculate intersection of two 3D rays, returns a 0-tuple for parallel rays,
    a 1-tuple for intersecting rays and a 2-tuple for not intersecting and not
    parallel rays with points of closest approach on each ray.

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
            return p1,
        else:
            # ray1 and ray2 do not have an intersection point,
            # p1 and p2 are the points of closest approach on each ray
            return p1, p2


def arc_angle_span_deg(start: float, end: float) -> float:
    """Returns the counter clockwise angle span from `start` to `end` in degrees.

    Returns the angle span in the range of [0, 360], 360 is a full circle.
    Full circle handling is a special case, because normalization of angles
    which describe a full circle would return 0 if treated as regular angles.
    e.g. (0, 360) → 360, (0, -360) → 360, (180, -180) → 360.
    Input angles with the same value always return 0 by definition: (0, 0) → 0,
    (-180, -180) → 0, (360, 360) → 0.

    """
    # Input values are equal, returns 0 by definition:
    if math.isclose(start, end):
        return 0.0

    # Normalized start- and end angles are equal, but input values are
    # different, returns 360 by definition:
    start %= 360.0
    if math.isclose(start, end % 360.0):
        return 360.0

    # Special treatment for end angle == 360 deg:
    if not math.isclose(end, 360.0):
        end %= 360.0

    if end < start:
        end += 360.0
    return end - start
