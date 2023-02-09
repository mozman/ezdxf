# Copyright (c) 2017 Sam Bolgert
# License: MIT License
# https://github.com/linuxlewis/tripy

from __future__ import annotations
from typing import Iterable, Iterator, List, Tuple
import sys
import math
from ezdxf.math import Vec2, UVec, has_clockwise_orientation

EPSILON = math.sqrt(sys.float_info.epsilon)

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
    ear_vertices: List[Vec2] = []
    polygon: List[Vec2] = Vec2.list(vertices)
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
        prev_point = polygon[i - 1]
        next_point = polygon[(i + 1) % point_count]
        if _is_ear(prev_point, point, next_point, polygon):
            ear_vertices.append(point)

    while ear_vertices and point_count >= 3:
        ear = ear_vertices.pop(0)
        i = polygon.index(ear)
        prev_index = i - 1
        prev_point = polygon[prev_index]
        next_point = polygon[(i + 1) % point_count]

        polygon.remove(ear)
        point_count -= 1
        yield prev_point, ear, next_point

        if point_count > 3:
            prev_prev_point = polygon[prev_index - 1]
            next_next_index = (i + 1) % point_count
            next_next_point = polygon[next_next_index]

            groups = [
                (prev_prev_point, prev_point, next_point, polygon),
                (prev_point, next_point, next_next_point, polygon),
            ]
            for group in groups:
                p = group[1]
                if _is_ear(*group):
                    if p not in ear_vertices:
                        ear_vertices.append(p)
                elif p in ear_vertices:
                    ear_vertices.remove(p)


def _is_convex(a: Vec2, b: Vec2, c: Vec2) -> bool:
    return a.x * (c.y - b.y) + b.x * (a.y - c.y) + c.x * (b.y - a.y) < 0.0


def _is_ear(p1: Vec2, p2: Vec2, p3: Vec2, polygon: List[Vec2]) -> bool:
    return (
        _is_convex(p1, p2, p3)
        and _triangle_area(p1, p2, p3) > 0.0
        and _contains_no_points(p1, p2, p3, polygon)
    )


def _contains_no_points(
    p1: Vec2, p2: Vec2, p3: Vec2, polygon: List[Vec2]
) -> bool:
    p123 = p1, p2, p3
    for pn in polygon:
        if pn in p123:
            continue
        elif _is_point_inside(pn, p1, p2, p3):
            return False
    return True


def _is_point_inside(p: Vec2, a: Vec2, b: Vec2, c: Vec2) -> bool:
    area = _triangle_area(a, b, c)
    area1 = _triangle_area(p, b, c)
    area2 = _triangle_area(p, a, c)
    area3 = _triangle_area(p, a, b)
    return abs(area - area1 - area2 - area3) < EPSILON


def _triangle_area(a: Vec2, b: Vec2, c: Vec2) -> float:
    return abs(
        (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2.0
    )
