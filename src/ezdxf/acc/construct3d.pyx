# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Sequence, Tuple
from .vector cimport Vec3, v3_from_cpp_vec3
from ._cpp_vec3 cimport CppVec3

import cython

DEF ABS_TOL = 1e-10

cdef double _determinant(CppVec3 v1, CppVec3 v2, CppVec3 v3):
    return v1.x * v2.y * v3.z + v1.y * v2.z * v3.x + \
           v1.z * v2.x * v3.y - v1.z * v2.y * v3.x - \
           v1.x * v2.z * v3.y - v1.y * v2.x * v3.z

def intersection_ray_ray_3d(ray1: Tuple[Vec3, Vec3],
                            ray2: Tuple[Vec3, Vec3],
                            double abs_tol=ABS_TOL) -> Sequence[Vec3]:
    """
    Calculate intersection of two rays, returns a 0-tuple for parallel rays, a
    1-tuple for intersecting rays and a 2-tuple for not intersecting and not
    parallel rays with points of closest approach on each ray.

    Args:
        ray1: first ray as tuple of two points on the ray as :class:`Vec3` objects
        ray2: second ray as tuple of two points on the ray as :class:`Vec3` objects
        abs_tol: absolute tolerance for comparisons

    """
    # source: http://www.realtimerendering.com/intersections.html#I304
    cdef CppVec3 o2_o1
    cdef double det1, det2
    cdef CppVec3 o1 = Vec3(ray1[0]).to_cpp_vec3()
    cdef CppVec3 p1 = Vec3(ray1[1]).to_cpp_vec3()
    cdef CppVec3 o2 = Vec3(ray2[0]).to_cpp_vec3()
    cdef CppVec3 p2 = Vec3(ray2[1]).to_cpp_vec3()

    cdef CppVec3 d1 = (p1 - o1).normalize(1.0)
    cdef CppVec3 d2 = (p2 - o2).normalize(1.0)
    cdef CppVec3 d1xd2 = d1.cross(d2)
    cdef double denominator = d1xd2.magnitude_sqr()
    if denominator <= abs_tol:
        # ray1 is parallel to ray2
        return tuple()
    else:
        o2_o1 = o2 - o1
        det1 = _determinant(o2_o1, d2, d1xd2)
        det2 = _determinant(o2_o1, d1, d1xd2)
        with cython.cdivision(True):  # denominator check is already done
            p1 = o1 + d1 * (det1 / denominator)
            p2 = o2 + d2 * (det2 / denominator)

        if p1.isclose(p2, abs_tol):
            # ray1 and ray2 have an intersection point
            return v3_from_cpp_vec3(p1),
        else:
            # ray1 and ray2 do not have an intersection point,
            # p1 and p2 are the points of closest approach on each ray
            return v3_from_cpp_vec3(p1), v3_from_cpp_vec3(p2)
