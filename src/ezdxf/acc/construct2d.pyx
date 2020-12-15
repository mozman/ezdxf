# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable, TYPE_CHECKING, Sequence, Optional
from .vector cimport Vec2, v2_isclose
from libc.math cimport fabs
import cython

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

DEF ABS_TOL = 1e-12
TOLERANCE = 1e-10

def has_clockwise_orientation(vertices: Iterable['Vertex']) -> bool:
    """ Returns True if 2D `vertices` have clockwise orientation. Ignores
    z-axis of all vertices.

    Args:
        vertices: iterable of :class:`Vec2` compatible objects

    Raises:
        ValueError: less than 3 vertices

    """
    cdef list _vertices = [Vec2(v) for v in vertices]
    if len(_vertices) < 3:
        raise ValueError('At least 3 vertices required.')

    cdef Vec2 p1 = <Vec2> _vertices[0]
    cdef Vec2 p2 = <Vec2> _vertices[-1]
    cdef double s = 0.0
    cdef Py_ssize_t index

    if not v2_isclose(p1, p2, ABS_TOL):
        _vertices.append(p1)

    for index in range(1, len(_vertices)):
        p2 = <Vec2> _vertices[index]
        s += (p2.x - p1.x) * (p2.y + p1.y)
        p1 = p2
    return s > 0.0

def intersection_line_line_2d(
        line1: Sequence[Vec2],
        line2: Sequence[Vec2],
        bint virtual=True,
        double abs_tol=TOLERANCE) -> Optional[Vec2]:
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
    cdef Vec2 a, b, c, d, res = Vec2()
    cdef double x1, y1, x2, y2, x3, y3, x4, y4, det
    cdef double x1_x2, y3_y4, y1_y2, x3_x4, e, f
    cdef bint in_range

    a = line1[0]
    b = line1[1]
    c = line2[0]
    d = line2[1]

    x1 = a.x
    y1 = a.y
    x2 = b.x
    y2 = b.y
    x3 = c.x
    y3 = c.y
    x4 = d.x
    y4 = d.y

    x1_x2 = x1 - x2
    y3_y4 = y3 - y4
    y1_y2 = y1 - y2
    x3_x4 = x3 - x4

    det = x1_x2 * y3_y4 - y1_y2 * x3_x4

    if fabs(det) <= abs_tol:
        return None

    e = x1 * y2 - y1 * x2
    f = x3 * y4 - y3 * x4
    # det near zero is checked by if-statement above:
    with cython.cdivision(True):
        x = (e * x3_x4 - x1_x2 * f) / det
        y = (e * y3_y4 - y1_y2 * f) / det

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

    res.x = x
    res.y = y
    return res
