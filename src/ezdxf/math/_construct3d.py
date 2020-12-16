# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Sequence, Tuple
# A pure Python implementation of a base type can't import from ._types or ezdxf.math!
from ezdxf.math._vector import Vec3


def _determinant(v1, v2, v3) -> float:
    """ Returns determinant. """
    e11, e12, e13 = v1
    e21, e22, e23 = v2
    e31, e32, e33 = v3

    return e11 * e22 * e33 + e12 * e23 * e31 + \
           e13 * e21 * e32 - e13 * e22 * e31 - \
           e11 * e23 * e32 - e12 * e21 * e33


def intersection_ray_ray_3d(ray1: Tuple[Vec3, Vec3],
                            ray2: Tuple[Vec3, Vec3],
                            abs_tol=1e-10) -> Sequence[Vec3]:
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
    o1, p1 = ray1
    d1 = (p1 - o1).normalize()
    o2, p2 = ray2
    d2 = (p2 - o2).normalize()
    d1xd2 = d1.cross(d2)
    denominator = d1xd2.magnitude_square
    if denominator <= abs_tol:
        # ray1 is parallel to ray2
        return tuple()
    else:
        o2_o1 = o2 - o1
        det1 = _determinant(o2_o1, d2, d1xd2)
        det2 = _determinant(o2_o1, d1, d1xd2)
        p1 = o1 + d1 * (det1 / denominator)
        p2 = o2 + d2 * (det2 / denominator)
        if p1.isclose(p2, abs_tol=abs_tol):
            # ray1 and ray2 have an intersection point
            return p1,
        else:
            # ray1 and ray2 do not have an intersection point,
            # p1 and p2 are the points of closest approach on each ray
            return p1, p2
