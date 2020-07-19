# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
from math import tau
from typing import List

from ezdxf.addons.drawing.type_hints import Radians
from ezdxf.math import Vector


def normalize_angle(theta: Radians) -> Radians:
    # have to mod tau twice to obtain [0, tau), because some angles once normalised become exactly equal to tau
    # e.g. (-1e-16 % tau) == tau
    # so (-1e-16 % tau) % tau == 0.0
    return (theta % tau) % tau


def get_tri_or_quad_points(solid, adjust_order=True) -> List[Vector]:
    d = solid.dxf
    vertices: List[Vector] = [d.vtx0, d.vtx1, d.vtx2]
    if d.vtx3 != d.vtx2:  # when the face is a triangle, vtx2 == vtx3
        vertices.append(d.vtx3)

    # adjust weird vertex order of SOLID and TRACE but not 3DFACE:
    # 0, 1, 2, 3 -> 0, 1, 3, 2
    if adjust_order and len(vertices) > 3:
        vertices[2], vertices[3] = vertices[3], vertices[2]

    if not vertices[0].isclose(vertices[-1]):
        vertices.append(vertices[0])
    return vertices
