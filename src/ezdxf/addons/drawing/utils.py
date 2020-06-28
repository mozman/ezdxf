# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import enum
import math
from math import tau
from typing import Union, List

from ezdxf.addons.drawing.type_hints import Radians
from ezdxf.entities import Face3d, Solid, Trace
from ezdxf.math import Vector, Z_AXIS, OCS


def normalize_angle(theta: Radians) -> Radians:
    # have to mod tau twice to obtain [0, tau), because some angles once normalised become exactly equal to tau
    # e.g. (-1e-16 % tau) == tau
    # so (-1e-16 % tau) % tau == 0.0
    return (theta % tau) % tau


def get_draw_angles(start: float, end: float, extrusion: Vector):
    if extrusion.isclose(Z_AXIS):
        return start, end
    else:
        ocs = OCS(extrusion)
        s = ocs.to_wcs(Vector.from_angle(start))
        e = ocs.to_wcs(Vector.from_angle(end))
        return e.angle % math.tau, s.angle % math.tau


def get_tri_or_quad_points(shape: Union[Face3d, Solid, Trace]) -> List[Vector]:
    d = shape.dxf
    vertices: List[Vector] = [d.vtx0, d.vtx1, d.vtx2]
    if d.vtx3 != d.vtx2:  # when the face is a triangle, vtx2 == vtx3
        vertices.append(d.vtx3)

    if not vertices[0].isclose(vertices[-1]):
        vertices.append(vertices[0])
    return vertices
