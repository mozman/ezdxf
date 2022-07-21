# Copyright (c) 2022, Manfred Moitzi
# License: MIT License

from __future__ import annotations
from typing import Iterable, Iterator, List, Tuple, Sequence, Callable
from ezdxf.math import Vec2, UVec, Vec3


__all__ = ["ear_clipping_2d", "ear_clipping_3d", "mapbox_earcut_2d"]


def ear_clipping_2d(
    vertices: Iterable[UVec],
) -> Iterator[Tuple[Vec2, Vec2, Vec2]]:
    """This function triangulates the given 2d polygon into simple triangles by
    the "ear clipping" algorithm. The function yields n-2 triangles for a polygon
    with n vertices, each triangle is a 3-tuple of :class:`Vec2` objects.

    The `fast` mode uses a shortcut for 4 and 5 vertices which may not work for
    concave polygons!

    .. versionadded:: 0.18

    Implementation Reference:
        - https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf

    """
    from ._tripy import earclip
    return earclip(vertices)


def ear_clipping_3d(
    vertices: Iterable[Vec3],
) -> Iterator[Tuple[Vec3, Vec3, Vec3]]:
    """Implements the "ear clipping" algorithm for planar 3d polygons.

    The `fast` mode uses a shortcut for 4 and 5 vertices which may not work for
    concave polygons!

    Raise:
        TypeError: invalid input data type
        ZeroDivisionError: normal vector calculation failed

    .. versionadded:: 0.18

    """
    from ._tripy import earclip
    return triangulate_3d(vertices, earclip)


def triangulate_3d(
    vertices: Iterable[Vec3],
    triangulate_2d: Callable[
        [Iterable[Vec2]], Iterator[Tuple[Vec2, Vec2, Vec2]]
    ],
) -> Iterator[Tuple[Vec3, Vec3, Vec3]]:
    """Applies a 2D triangulation function to a planar 3D polygon.

    Raise:
        TypeError: invalid input data type
        ZeroDivisionError: normal vector calculation failed

    .. versionadded:: 0.18

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
    ocs = OCS(safe_normal_vector(polygon))
    elevation = ocs.from_wcs(polygon[0]).z  # type: ignore
    for triangle in triangulate_2d(ocs.points_from_wcs(polygon)):
        yield tuple(  # type: ignore
            ocs.points_to_wcs(Vec3(v.x, v.y, elevation) for v in triangle)
        )


def simple_polygon_triangulation(
    face: Iterable[Vec3],
) -> List[Sequence[Vec3]]:
    """Simple triangulation of convex polygons.

    This function creates regular triangles by adding a center-vertex in the
    middle of the polygon, but works only for convex shapes.

    .. versionadded:: 0.18

    """
    face_: List[Vec3] = list(face)
    assert len(face_) > 2
    if not face_[0].isclose(face_[-1]):
        face_.append(face_[0])
    center = Vec3.sum(face_[:-1]) / (len(face_) - 1)
    return [(v1, v2, center) for v1, v2 in zip(face_, face_[1:])]


def mapbox_earcut_2d(
    exterior: Iterable[UVec], holes: Iterable[Iterable[UVec]] = None
) -> Iterator[Tuple[Vec2, Vec2, Vec2]]:
    """Mapbox triangulation algorithm with hole support.

    Args:
        exterior: exterior polygon as iterable of :class:`Vec2` objects
        holes: iterable of holes as iterable of :class:`Vec2` objects, a single
            vertex represents a Steiner point.

    Returns:
        yields the result as 3-tuples of :class:`Vec2` objects

    """
    from ._mapbox_earcut import earcut

    data: list[Vec2] = Vec2.list(exterior)
    hole_indices: List[int] = []

    if len(data) == 0:
        return

    if holes is not None:
        for hole in holes:
            vertices = tuple(hole)
            if len(vertices):
                index = len(data)
                hole_indices.append(index)
                data.extend(Vec2.generate(vertices))

    triangles = earcut(data, hole_indices)

    triangle: List[Vec2] = []
    for vec2 in triangles:
        triangle.append(vec2)
        if len(triangle) == 3:
            yield tuple(triangle)  # type: ignore
            triangle.clear()
