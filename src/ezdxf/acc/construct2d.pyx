# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable, TYPE_CHECKING
from .vector cimport Vec2, v2_isclose

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

DEF ABS_TOL = 1e-12

def has_clockwise_orientation(vertices: Iterable['Vertex']) -> bool:
    """ Returns True if 2D `vertices` have clockwise orientation. Ignores
    z-axis of all vertices.

    Args:
        vertices: iterable of :class:`Vec2` compatible objects

    Raises:
        ValueError: less than 3 vertices

    """
    cdef list _vertices = [Vec2(v) for v in vertices]
    if len(_vertices) < 3:
        raise ValueError('At least 3 vertices required.')

    cdef Vec2 p1 = <Vec2> _vertices[0]
    cdef Vec2 p2 = <Vec2> _vertices[-1]
    cdef double s = 0.0
    cdef Py_ssize_t index

    if not v2_isclose(p1, p2, ABS_TOL):
        _vertices.append(p1)

    for index in range(1, len(_vertices)):
        p2 = <Vec2> _vertices[index]
        s += (p2.x - p1.x) * (p2.y + p1.y)
        p1 = p2
    return s > 0.0
