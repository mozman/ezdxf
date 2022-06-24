# Copyright (c) 2022, Manfred Moitzi
# License: MIT License

from __future__ import annotations
from typing import Iterable, Iterator, List, Tuple, Sequence
import math
import sys
from ezdxf.math import Vec2, UVec, Vec3


EPSILON = math.sqrt(sys.float_info.epsilon)

__all__ = ["ear_clipping_2d", "ear_clipping_3d"]


# Candidate for a faster Cython implementation:
def ear_clipping_2d(
    vertices: Iterable[UVec],
    fast=False,
) -> Iterator[Tuple[Vec2, Vec2, Vec2]]:
    """This function triangulates the given 2d polygon into simple triangles by
    the "ear clipping" algorithm. The function yields n-2 triangles for a polygon
    with n vertices, each triangle is a 3-tuple of :class:`Vec2` objects.

    The `fast` mode uses a shortcut for 4 and 5 vertices which may not work for
    concave polygons!

    Implementation Reference:
        - https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf

    """
    # Copyright (c) 2017 Sam Bolgert
    # License: MIT License
    # https://github.com/linuxlewis/tripy
    ear_vertices: List[Vec2] = []
    polygon: List[Vec2] = Vec2.list(vertices)
    if len(polygon) == 0:
        return

    # remove closing vertex -> produces a degenerated last triangle
    # [0] -> [-2] -> [-1], where [0] == [-1]
    if polygon[0].isclose(polygon[-1]):
        polygon.pop()
    if _is_clockwise(polygon):
        polygon.reverse()

    point_count = len(polygon)
    if len(polygon) < 3:
        return
    # "simple" polygons are a requirement, see algorithm description:
    # https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf
    if point_count == 3:
        yield polygon[0], polygon[1], polygon[2]
        return
    if fast and point_count < 6:  # fast simple cases 4..5 vertices
        if point_count == 4:
            yield polygon[0], polygon[1], polygon[2]
            yield polygon[0], polygon[2], polygon[3]
        elif point_count == 5:
            yield polygon[0], polygon[3], polygon[4]
            yield polygon[0], polygon[1], polygon[3]
            yield polygon[1], polygon[2], polygon[3]
        return

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
    s = 0.0
    polygon_count = len(polygon)
    for i in range(polygon_count):
        point = polygon[i]
        point2 = polygon[(i + 1) % polygon_count]
        s += (point2.x - point.x) * (point2.y + point.y)
    return s > 0


def _is_convex(a: Vec2, b: Vec2, c: Vec2) -> bool:
    return a.x * (c.y - b.y) + b.x * (a.y - c.y) + c.x * (b.y - a.y) < 0


def _is_ear(p1: Vec2, p2: Vec2, p3: Vec2, polygon: List[Vec2]) -> bool:
    ear = (
        _contains_no_points(p1, p2, p3, polygon)
        and _is_convex(p1, p2, p3)
        and _triangle_area(p1, p2, p3) > 0
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
    area = _triangle_area(a, b, c)
    area1 = _triangle_area(p, b, c)
    area2 = _triangle_area(p, a, c)
    area3 = _triangle_area(p, a, b)
    return abs(area - sum([area1, area2, area3])) < EPSILON


def _triangle_area(a: Vec2, b: Vec2, c: Vec2) -> float:
    return abs(
        (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2.0
    )


def ear_clipping_3d(
    vertices: Iterable[Vec3],
    fast=False,
) -> Iterator[Tuple[Vec3, Vec3, Vec3]]:
    """Implements the "ear clipping" algorithm for planar 3d polygons.

    The `fast` mode uses a shortcut for 4 and 5 vertices which may not work for
    concave polygons!

    Raise:
        TypeError: invalid input data type
        ZeroDivisionError: normal vector calculation failed

    """
    from ezdxf.math import safe_normal_vector, OCS

    polygon = list(vertices)
    if len(polygon) == 0:
        return

    if not isinstance(polygon[0], Vec3):
        raise TypeError("Vec3() as input type required")
    if polygon[0].isclose(polygon[-1]):
        polygon.pop()
    count = len(polygon)
    if count < 3:
        return
    if count == 3:
        yield polygon[0], polygon[1], polygon[2]
        return
    if fast and count < 6:
        if count == 4:
            yield polygon[0], polygon[1], polygon[2]
            yield polygon[0], polygon[2], polygon[3]
        elif count == 5:
            yield polygon[0], polygon[3], polygon[4]
            yield polygon[0], polygon[1], polygon[3]
            yield polygon[1], polygon[2], polygon[3]
        return
    ocs = OCS(safe_normal_vector(polygon))
    elevation = ocs.from_wcs(polygon[0]).z  # type: ignore
    for triangle in ear_clipping_2d(ocs.points_from_wcs(polygon), fast=False):
        yield tuple(  # type: ignore
            ocs.points_to_wcs(Vec3(v.x, v.y, elevation) for v in triangle)
        )


def simple_polygon_triangulation(
    face: Iterable[Vec3],
) -> List[Sequence[Vec3]]:
    """Simple triangulation of convex polygons.

    This function creates regular triangles by adding a center-vertex in the
    middle of the polygon, but works only for convex shapes.
    """
    face_: List[Vec3] = list(face)
    assert len(face_) > 2
    if not face_[0].isclose(face_[-1]):
        face_.append(face_[0])
    center = Vec3.sum(face_[:-1]) / (len(face_) - 1)
    return [(v1, v2, center) for v1, v2 in zip(face_, face_[1:])]
