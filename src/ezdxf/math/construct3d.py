# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Sequence, List, Iterable, Union
from ezdxf.math.vector import Vector, Vec2


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


def subdivide_face(face: Sequence[Union[Vector, Vec2]], quads=True) -> Iterable[List[Vector]]:
    """ Yields new subdivided faces. Creates new faces from subdivided edges and the face midpoint by linear
    interpolation.

    Args:
        face: a sequence of vertices, :class:`Vec2` and :class:`Vector` objects supported.
        quads: create quad faces if ``True`` else create triangles

    """
    if len(face) < 3:
        raise ValueError('3 or more vertices required.')
    mid_pos = sum(face) / len(face)
    subdiv_pos = [v1.lerp(v2) for v1, v2 in zip(face[:-1], face[1:])]
    subdiv_pos.append(face[-1].lerp(face[0]))
    for index, vertex in enumerate(face):
        if quads:
            yield vertex, subdiv_pos[index], mid_pos, subdiv_pos[index - 1]
        else:
            yield subdiv_pos[index - 1], vertex, mid_pos
            yield vertex, subdiv_pos[index], mid_pos
