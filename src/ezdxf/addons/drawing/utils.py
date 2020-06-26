# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import enum
import math
from math import tau
from typing import Union, Tuple, Optional, List

from ezdxf.addons.drawing.type_hints import Radians
from ezdxf.entities import Face3d, Solid, Trace
from ezdxf.entities.mtext import plain_mtext
from ezdxf.math import Vector


def normalize_angle(theta: Radians) -> Radians:
    # have to mod tau twice to obtain [0, tau), because some angles once normalised become exactly equal to tau
    # e.g. (-1e-16 % tau) == tau
    # so (-1e-16 % tau) % tau == 0.0
    return (theta % tau) % tau


@enum.unique
class Direction(enum.Enum):
    CLOCKWISE = 0
    ANTI_CLOCKWISE = 1


def get_rotation_direction_from_extrusion_vector(extrusion_vector: Union[Vector, Tuple[float, float, float]]) -> Direction:
    """ when rotating about the extrusion vector:
    anticlockwise rotation about (0, 0, 1) corresponds to positive => anti clockwise
    anticlockwise rotation about (0, 0, -1) corresponds to positive => clockwise
    """
    # may be passed a tuple if the default extrusion vector is used
    if isinstance(extrusion_vector, tuple):
        extrusion_vector = Vector(*extrusion_vector)

    mag = extrusion_vector.magnitude
    if math.isclose(mag, 0.0):
        return Direction.ANTI_CLOCKWISE
    extrusion_vector /= mag

    clockwise_similarity = extrusion_vector.dot(Vector(0, 0, -1))
    anticlockwise_similarity = extrusion_vector.dot(Vector(0, 0, 1))
    if math.isclose(clockwise_similarity, 1.0):
        return Direction.CLOCKWISE
    elif math.isclose(anticlockwise_similarity, 1.0):
        return Direction.ANTI_CLOCKWISE
    else:
        if anticlockwise_similarity >= clockwise_similarity:
            return Direction.ANTI_CLOCKWISE
        else:
            return Direction.CLOCKWISE


def get_draw_angles(direction: Direction, start_angle: Radians, end_angle: Radians) -> Optional[Tuple[Radians, Radians]]:
    if direction == Direction.CLOCKWISE:
        # arc always drawn anticlockwise
        start_angle, end_angle = normalize_angle(-end_angle), normalize_angle(-start_angle)
    elif direction == Direction.ANTI_CLOCKWISE:
        start_angle, end_angle = normalize_angle(start_angle), normalize_angle(end_angle)
    else:
        raise ValueError(direction)

    # if the end angle lies just behind the start angle
    eps = 1e-4
    offset_start = start_angle + eps
    offset_end = (end_angle + eps) % tau
    if offset_start > tau:
        if (start_angle <= offset_end < tau) or (0 <= offset_end <= offset_start % tau):
            return None
    else:
        if start_angle <= offset_end <= offset_start:
            return None

    return start_angle, end_angle


def get_tri_or_quad_points(shape: Union[Face3d, Solid, Trace]) -> List[Vector]:
    d = shape.dxf
    vertices: List[Vector] = [d.vtx0, d.vtx1, d.vtx2]
    if d.vtx3 != d.vtx2:  # when the face is a triangle, vtx2 == vtx3
        vertices.append(d.vtx3)

    if not vertices[0].isclose(vertices[-1]):
        vertices.append(vertices[0])
    return vertices
