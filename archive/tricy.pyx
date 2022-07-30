# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2017 Sam Bolgert
# License: MIT License
# https://github.com/linuxlewis/tripy
from typing import Iterable, Iterator, List, Tuple
from ezdxf.math import UVec, has_clockwise_orientation
from ezdxf.acc.vector cimport Vec2
from libc.math cimport fabs

cdef double EPSILON = 1e-16

# This module was replaced by the faster ezdxf.math._mapbox_earcut.py module!
# This file just preserves the invested time and effort for the ezdxf
# integration ;)


def earclip(vertices: Iterable[UVec]) -> Iterator[Tuple[Vec2, Vec2, Vec2]]:
    """This function triangulates the given 2d polygon into simple triangles by
    the "ear clipping" algorithm. The function yields n-2 triangles for a polygon
    with n vertices, each triangle is a 3-tuple of :class:`Vec2` objects.

    Implementation Reference:
        - https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf

    """
    cdef list ear_vertices = []
    cdef list polygon = Vec2.list(vertices)
    cdef list groups
    cdef int point_count, prev_index, next_next_index, i, j
    cdef Vec2 ear, prev_point, next_point, point, prev_prev_point, next_next_point

    if len(polygon) == 0:
        return

    # remove closing vertex -> produces a degenerated last triangle
    # [0] -> [-2] -> [-1], where [0] == [-1]
    if polygon[0].isclose(polygon[-1]):
        polygon.pop()

    point_count = len(polygon)
    if point_count < 3:
        return

    if has_clockwise_orientation(polygon):
        polygon.reverse()

    # "simple" polygons are a requirement, see algorithm description:
    # https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf
    if point_count == 3:
        yield polygon[0], polygon[1], polygon[2]
        return

    for i, point in enumerate(polygon):
        prev_point = <Vec2> polygon[i - 1]
        next_point = <Vec2> polygon[(i + 1) % point_count]
        if _is_ear(prev_point, point, next_point, polygon):
            ear_vertices.append(point)

    while ear_vertices and point_count >= 3:
        ear = <Vec2> ear_vertices.pop(0)
        i = polygon.index(ear)
        prev_index = i - 1
        prev_point = <Vec2> polygon[prev_index]
        next_point = <Vec2> polygon[(i + 1) % point_count]

        polygon.remove(ear)
        point_count -= 1
        yield prev_point, ear, next_point

        if point_count > 3:
            prev_prev_point = <Vec2> polygon[prev_index - 1]
            next_next_index = (i + 1) % point_count
            next_next_point = <Vec2> polygon[next_next_index]

            groups = [
                (prev_prev_point, prev_point, next_point, polygon),
                (prev_point, next_point, next_next_point, polygon),
            ]
            for j in range(len(groups)):
                group = groups[j]
                p = group[1]
                if _is_ear(<Vec2> group[0], <Vec2> p, <Vec2> group[2], <list> group[3]):
                    if p not in ear_vertices:
                        ear_vertices.append(p)
                elif p in ear_vertices:
                    ear_vertices.remove(p)


cdef bint _is_convex(Vec2 a, Vec2 b, Vec2 c):
    return a.x * (c.y - b.y) + b.x * (a.y - c.y) + c.x * (b.y - a.y) < 0.0


cdef bint _is_ear(Vec2 p1, Vec2 p2, Vec2 p3, list polygon):
    return (
        _is_convex(p1, p2, p3)
        and _triangle_area(p1, p2, p3) > 0.0
        and _contains_no_points(p1, p2, p3, polygon)
    )


cdef bint _contains_no_points(
    Vec2 p1, Vec2 p2, Vec2 p3, list polygon
):
    cdef Vec2 pn
    cdef int i

    for i in range(len(polygon)):
        pn = <Vec2> polygon[i]
        if pn is p1 or pn is p2 or pn is p3:
            continue
        elif _is_point_inside(pn, p1, p2, p3):
            return False
    return True


cdef bint _is_point_inside(Vec2 p, Vec2 a, Vec2 b, Vec2 c):
    cdef double area = _triangle_area(a, b, c)
    cdef double area1 = _triangle_area(p, b, c)
    cdef double area2 = _triangle_area(p, a, c)
    cdef double area3 = _triangle_area(p, a, b)
    return fabs(area - area1 - area2 - area3) < EPSILON


cdef double _triangle_area(Vec2 a, Vec2 b, Vec2 c):
    return fabs(
        (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2.0
    )
