# Copyright (c) 2017 Sam Bolgert
# License: MIT License
# https://github.com/linuxlewis/tripy
from typing import Iterable, Iterator, List, Tuple
import math
import sys
from ezdxf.math import Vec2, Vertex

EPSILON = math.sqrt(sys.float_info.epsilon)


def ear_clipping(
    vertices: Iterable[Vertex],
) -> Iterator[Tuple[Vec2, Vec2, Vec2]]:
    """This function triangulates the given polygon into simple triangles by the
    "ear clipping" algorithm. The function yields n-2 triangles for a polygon
    with n vertices, each triangle is a 3-tuple of :class:`Vec2` objects.

    Implementation Reference:
        - https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf

    """
    ear_vertices: List[Vec2] = []
    polygon: List[Vec2] = Vec2.list(vertices)

    # remove closing vertex -> produces a degenerated last triangle
    # [0] -> [-2] -> [-1], where [0] == [-1]
    if polygon[0].isclose(polygon[-1]):
        polygon.pop()
    if _is_clockwise(polygon):
        polygon.reverse()

    point_count = len(polygon)
    for i in range(point_count):
        prev_index = i - 1
        prev_point = polygon[prev_index]
        point = polygon[i]
        next_index = (i + 1) % point_count
        next_point = polygon[next_index]

        if _is_ear(prev_point, point, next_point, polygon):
            ear_vertices.append(point)

    while ear_vertices and point_count >= 3:
        ear = ear_vertices.pop(0)
        i = polygon.index(ear)
        prev_index = i - 1
        prev_point = polygon[prev_index]
        next_index = (i + 1) % point_count
        next_point = polygon[next_index]

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


def _is_clockwise(polygon: List[Vec2]) -> bool:
    s = 0
    polygon_count = len(polygon)
    for i in range(polygon_count):
        point = polygon[i]
        point2 = polygon[(i + 1) % polygon_count]
        s += (point2.x - point.x) * (point2.y + point.y)
    return s > 0


def _is_convex(prev: Vec2, point: Vec2, next: Vec2):
    return _triangle_sum(prev.x, prev.y, point.x, point.y, next.x, next.y) < 0


def _is_ear(p1: Vec2, p2: Vec2, p3: Vec2, polygon: List[Vec2]) -> bool:
    ear = (
        _contains_no_points(p1, p2, p3, polygon)
        and _is_convex(p1, p2, p3)
        and _triangle_area(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y) > 0
    )
    return ear


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
    area = _triangle_area(a.x, a.y, b.x, b.y, c.x, c.y)
    area1 = _triangle_area(p.x, p.y, b.x, b.y, c.x, c.y)
    area2 = _triangle_area(p.x, p.y, a.x, a.y, c.x, c.y)
    area3 = _triangle_area(p.x, p.y, a.x, a.y, b.x, b.y)
    return abs(area - sum([area1, area2, area3])) < EPSILON


def _triangle_area(x1, y1, x2, y2, x3, y3):
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)


def _triangle_sum(x1, y1, x2, y2, x3, y3):
    return x1 * (y3 - y2) + x2 * (y1 - y3) + x3 * (y2 - y1)
