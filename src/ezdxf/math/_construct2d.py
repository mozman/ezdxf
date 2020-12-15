# Copyright (c) 2010-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Sequence, Optional
import math
# A pure Python implementation of a base type can't import from ._types or ezdxf.math!
from ._vector import Vec2

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex
TOLERANCE = 1e-10


def has_clockwise_orientation(vertices: Iterable['Vertex']) -> bool:
    """ Returns True if 2D `vertices` have clockwise orientation. Ignores
    z-axis of all vertices.

    Args:
        vertices: iterable of :class:`Vec2` compatible objects

    Raises:
        ValueError: less than 3 vertices

    """
    vertices = Vec2.list(vertices)
    if len(vertices) < 3:
        raise ValueError('At least 3 vertices required.')

    # Close polygon:
    if not vertices[0].isclose(vertices[-1]):
        vertices.append(vertices[0])

    return sum(
        (p2.x - p1.x) * (p2.y + p1.y)
        for p1, p2 in zip(vertices, vertices[1:])
    ) > 0


def intersection_line_line_2d(
        line1: Sequence[Vec2],
        line2: Sequence[Vec2],
        virtual=True,
        abs_tol=TOLERANCE) -> Optional[Vec2]:
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
