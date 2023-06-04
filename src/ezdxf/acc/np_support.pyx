# cython: language_level=3
# distutils: language = c++
#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import numpy as np
import cython
from .vector cimport isclose

DEF ABS_TOL = 1e-12
DEF REL_TOL = 1e-9

def has_clockwise_orientation(vertices: np.ndarray) -> bool:
    """ Returns True if 2D `vertices` have clockwise orientation. Ignores
    z-axis of all vertices.

    Args:
        vertices: numpy array

    Raises:
        ValueError: less than 3 vertices

    """
    if len(vertices) < 3:
        raise ValueError('At least 3 vertices required.')

    return _has_clockwise_orientation(vertices, vertices.shape[0])

@cython.boundscheck(False)
@cython.wraparound(False)
cdef bint _has_clockwise_orientation(double [:, ::1] vertices, Py_ssize_t size):
    cdef Py_ssize_t index
    cdef Py_ssize_t start
    cdef Py_ssize_t last = size - 1
    cdef double s = 0.0
    cdef double p1x = vertices[0][0]
    cdef double p1y = vertices[0][1]
    cdef double p2x = vertices[last][0]
    cdef double p2y = vertices[last][1]

    # Using the same tolerance as the Python implementation:
    cdef bint x_is_close = isclose(p1x, p2x, REL_TOL, ABS_TOL)
    cdef bint y_is_close = isclose(p1y, p2y, REL_TOL, ABS_TOL)

    if x_is_close and y_is_close:
        p1x = vertices[0][0]
        p1y = vertices[0][1]
        start = 1
    else:
        p1x = vertices[last][0]
        p1y = vertices[last][1]
        start = 0

    for index in range(start, size):
        p2x = vertices[index][0]
        p2y = vertices[index][1]
        s += (p2x - p1x) * (p2y + p1y)
        p1x = p2x
        p1y = p2y
    return s > 0.0
