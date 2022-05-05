#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterator, Sequence, Optional, List
from ezdxf.math import Vec3, Matrix44
from ezdxf._acis.const import *
from ezdxf._acis.abstract import AbstractEntity
from ezdxf._acis import sat
from ezdxf._acis import sab


def parse_transform(transform: AbstractEntity) -> Matrix44:
    if isinstance(transform, sat.SatEntity):
        return parse_sat_transform(transform)
    elif isinstance(transform, sab.SabEntity):
        return parse_sab_transform(transform)
    else:
        raise TypeError("invalid entity type")


def parse_sat_transform(transform: sat.SatEntity) -> Matrix44:
    values = transform.parse_values("f;f;f;f;f;f;f;f;f;f;f;f")
    if len(values) != 12:
        raise ParsingError("transform entity has not enough data")
    a, b, c, d, e, f, g, h, i, j, k, l = values
    return Matrix44((a, b, c, 0, d, e, f, 0, g, h, i, 0, j, k, l, 1))


def parse_sab_transform(transform: sab.SabEntity) -> Matrix44:
    # Weired special case, transformation matrix is stored as long string:
    # Token(tag=18, value='1 0 0 0 1 0 0 0 1 123 85 8.4999999999999947 1 no_rotate no_reflect no_shear ')
    strings = transform.parse_values("@")
    if strings:
        e = sat.new_entity("transform", data=strings[0].split())
        return parse_sat_transform(e)
    return Matrix44()


def body_planar_polygon_faces(
    body: AbstractEntity,
) -> Iterator[List[Sequence[Vec3]]]:
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
    if lump.is_null_ptr:
        raise ParsingError("lump data not found")
    m: Optional[Matrix44] = None
    if not transform.is_null_ptr:
        m = parse_transform(transform)
    for lump in all_lumps(lump):
        yield list(lump_planar_polygon_faces(lump, m))


def all_lumps(lump: AbstractEntity) -> List[AbstractEntity]:
    """Returns a list of all linked lumps."""
    assert lump.name == "lump", "type error, expected lump"
    lumps = []
    while not lump.is_null_ptr:
        lumps.append(lump)
        lump = lump.find_first("lump")
    return lumps


def lump_planar_polygon_faces(
    lump: AbstractEntity, m: Matrix44 = None
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
    if lump.name != "lump" or lump.name == "null-ptr":
        raise TypeError(f"expected lump, got: {lump.name}")

    face = lump.find_path("shell/face")
    while not face.is_null_ptr:
        vertices: List[Vec3] = []
        face, loop, plane = face.find_entities("face;loop;plane-surface")
        if plane.is_null_ptr or loop.is_null_ptr:
            continue  # not a plane-surface or a polygon face

        first_coedge = loop.find_first("coedge")
        if first_coedge.is_null_ptr:
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
            if line.is_null_ptr:  # edge is not a straight line
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


def parse_point(point: AbstractEntity) -> Vec3:
    """Parses the `point`entity as :class:`ezdxf.math.Vec3` instance.

    Raises:
         ParsingError: no or invalid point entity

    """
    if not point.is_null_ptr or point.name != "point":
        try:
            return Vec3(point.parse_values("v")[0])
        except (IndexError, TypeError):
            pass
    raise ParsingError(f"expected a point entity, got {point.name}")
