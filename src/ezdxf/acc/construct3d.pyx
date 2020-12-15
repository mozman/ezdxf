# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Sequence, Tuple
from libc.math cimport fabs
from .vector cimport (
Vec3, v3_isclose, v3_sub, v3_cross, v3_normalize, v3_magnitude_sqr,
v3_add, v3_mul,
)
import cython

DEF ABS_TOL = 1e-10

cdef double _determinant(Vec3 v1, Vec3 v2, Vec3 v3):
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
    cdef Vec3 o1, p1, o2, p2, d1, d2, d1xd2, o2_o1
    cdef double det1, det2, denominator
    o1 = ray1[0]
    p1 = ray1[1]
    o2 = ray2[0]
    p2 = ray2[1]
    d1 = v3_normalize(v3_sub(p1, o1), 1.0)
    d2 = v3_normalize(v3_sub(p2, o2), 1.0)
    d1xd2 = v3_cross(d1, d2)
    denominator = v3_magnitude_sqr(d1xd2)
    if fabs(denominator) <= abs_tol:
        # ray1 is parallel to ray2
        return tuple()
    else:
        o2_o1 = v3_sub(o2, o1)
        det1 = _determinant(o2_o1, d2, d1xd2)
        det2 = _determinant(o2_o1, d1, d1xd2)
        with cython.cdivision(True):  # denominator check is already done
            p1 = v3_add(o1, v3_mul(d1, det1 / denominator))
            p2 = v3_add(o2, v3_mul(d2, det2 / denominator))

        if v3_isclose(p1, p2, abs_tol):
            # ray1 and ray2 have an intersection point
            return p1,
        else:
            # ray1 and ray2 do not have an intersection point,
            # p1 and p2 are the points of closest approach on each ray
            return p1, p2
