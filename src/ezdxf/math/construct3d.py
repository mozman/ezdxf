# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Sequence
from ezdxf.math.vector import Vector


def is_planar_face(face: Sequence[Vector], abs_tol=1e-12) -> bool:
    """ Returns ``True`` if sequence of vectors is a planar face.

    Args:
         face: sequence of :class:`~ezdxf.math.Vector` objects
         abs_tol: tolerance for normals check

    """
    if len(face) < 3:
        return False
    if len(face) == 3:
        return True
    first_normal = None
    for index in range(len(face) - 2):
        a, b, c = face[index:index + 3]
        normal = (b - a).cross(c - b).normalize()
        if first_normal is None:
            first_normal = normal
        elif not first_normal.isclose(normal, abs_tol):
            return False
    return True
