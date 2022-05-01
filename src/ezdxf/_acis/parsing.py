#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterator, Sequence, Optional, List
from ezdxf.math import Vec3, Matrix44
from ezdxf._acis.const import *
from ezdxf._acis.io import (
    RawEntity,
    NULL_PTR,
)


def parse_transform(transform: RawEntity) -> Matrix44:
    values = transform.parse_values("f;f;f;f;f;f;f;f;f;f;f;f")
    if len(values) != 12:
        raise ParsingError("transform entity has not enough data")
    a, b, c, d, e, f, g, h, i, j, k, l = values
    return Matrix44(
        [
            (a, b, c, 0.0),
            (d, e, f, 0.0),
            (g, h, i, 0.0),
            (j, k, l, 1.0),
        ]
    )


def body_planar_polygon_faces(body: RawEntity) -> Iterator[List[Sequence[Vec3]]]:
    """Yields all planar polygon faces from all lumps in the given `body`_
    entity. Yields a separated list of faces for each linked `lump`_ entity.

    Args:
        body: ACIS raw entity of type `body`_

    Raises:
        TypeError: `body` has invalid ACIS type
        ParsingError: `body` has no linked lump entity

    """

    if body.name != "body":
        raise TypeError(f"expected body, got: {body.name}")

    lump, transform = body.find_entities("lump;transform")
    if lump is NULL_PTR:
        raise ParsingError("lump data not found")

    m: Optional[Matrix44] = None
    if transform is not NULL_PTR:
        m = parse_transform(transform)
    for lump in all_lumps(lump):
        yield list(lump_planar_polygon_faces(lump, m))


def all_lumps(lump: RawEntity) -> List[RawEntity]:
    """Returns a list of all linked lumps. """
    assert lump.name == "lump", "type error, expected lump"
    lumps = []
    while lump is not NULL_PTR:
        lumps.append(lump)
        lump = lump.find_first("lump")
    return lumps


def lump_planar_polygon_faces(
    lump: RawEntity, m: Matrix44 = None
) -> Iterator[Sequence[Vec3]]:
    """Yields all planar polygon faces from the given `lump`_ entity as sequence
    of :class:`~ezdxf.math.Vec3` instances. Applies the transformation
    :class:`~ezdxf.math.Matrix44` `m` to all vertices if not ``None``.

    Args:
        lump: ACIS raw entity of type `lump`_
        m: optional transformation matrix

    Raises:
        TypeError: `lump` has invalid ACIS type

    """
    if lump.name != "lump" or lump is NULL_PTR:
        raise TypeError(f"expected lump, got: {lump.name}")

    face = lump.find_path("shell/face")
    while face is not NULL_PTR:
        vertices: List[Vec3] = []
        face, loop, plane = face.find_entities("face;loop;plane-surface")
        if plane is NULL_PTR or loop is NULL_PTR:
            continue  # not a plane-surface or a polygon face

        first_coedge = loop.find_first("coedge")
        if first_coedge is NULL_PTR:
            continue  # don't know what is going on

        coedge = first_coedge
        is_valid_face = True
        while True:
            # the first coedge field points to the next coedge
            # the edge entity contains the vertices and the curve type
            coedge, edge = coedge.find_entities("coedge;edge")

            # only take the first vertex, the second vertex is the first
            # vertex of the next edge:
            vertex, line = edge.find_entities("vertex;straight-curve")
            if line is NULL_PTR:  # edge is not a straight line
                is_valid_face = False
                break

            # the point entity stores the actual coordinates
            point = vertex.find_first("point")
            vertices.append(parse_point(point))
            if coedge is first_coedge:  # loop is closed
                break

        if is_valid_face:
            if m is not None:
                yield list(m.transform_vertices(vertices))
            else:
                yield vertices


def parse_point(point: RawEntity) -> Vec3:
    """Parses the `point`entity as :class:`ezdxf.math.Vec3` instance.

    Raises:
         ParsingError: no or invalid point entity

    """
    if point is not NULL_PTR or point.name != "point":
        data = point.parse_values("f;f;f")
        if len(data) > 1:
            return Vec3(data[:3])
    raise ParsingError("expected a point entity")
