# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020-2023, Manfred Moitzi
# License: MIT License
# type: ignore -- pylance sucks at type-checking cython files
from typing import Iterable, TYPE_CHECKING, Sequence, Optional, Tuple
from libc.math cimport fabs
from .vector cimport Vec2, v2_isclose, Vec3, v3_from_cpp_vec3, isclose
from ._cpp_vec3 cimport CppVec3

import cython

if TYPE_CHECKING:
    from ezdxf.math import UVec

cdef extern from "constants.h":
    const double ABS_TOL
    const double REL_TOL
    const double M_TAU

cdef double RAD_ABS_TOL = 1e-15
cdef double DEG_ABS_TOL = 1e-13
cdef double TOLERANCE = 1e-10

def has_clockwise_orientation(vertices: Iterable[UVec]) -> bool:
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

    # Using the same tolerance as the Python implementation:
    if not v2_isclose(p1, p2, REL_TOL, ABS_TOL):
        _vertices.append(p1)

    for index in range(1, len(_vertices)):
        p2 = <Vec2> _vertices[index]
        s += (p2.x - p1.x) * (p2.y + p1.y)
        p1 = p2
    return s > 0.0

def intersection_line_line_2d(
        line1: Sequence[Vec2],
        line2: Sequence[Vec2],
        bint virtual=True,
        double abs_tol=TOLERANCE) -> Optional[Vec2]:
    """
    Compute the intersection of two lines in the xy-plane.

    Args:
        line1: start- and end point of first line to test
            e.g. ((x1, y1), (x2, y2)).
        line2: start- and end point of second line to test
            e.g. ((x3, y3), (x4, y4)).
        virtual: ``True`` returns any intersection point, ``False`` returns
            only real intersection points.
        abs_tol: tolerance for intersection test.

    Returns:
        ``None`` if there is no intersection point (parallel lines) or
        intersection point as :class:`Vec2`

    """
    # Algorithm based on: http://paulbourke.net/geometry/pointlineplane/
    # chapter: Intersection point of two line segments in 2 dimensions
    cdef Vec2 s1, s2, c1, c2, res
    cdef double s1x, s1y, s2x, s2y, c1x, c1y, c2x, c2y, den, us, uc
    cdef double lwr = 0.0, upr = 1.0

    s1 = line1[0]
    s2 = line1[1]
    c1 = line2[0]
    c2 = line2[1]

    s1x = s1.x
    s1y = s1.y
    s2x = s2.x
    s2y = s2.y
    c1x = c1.x
    c1y = c1.y
    c2x = c2.x
    c2y = c2.y

    den = (c2y - c1y) * (s2x - s1x) - (c2x - c1x) * (s2y - s1y)

    if fabs(den) <= abs_tol:
        return None


    # den near zero is checked by if-statement above:
    with cython.cdivision(True):
        us = ((c2x - c1x) * (s1y - c1y) - (c2y - c1y) * (s1x - c1x)) / den

    res = Vec2(s1x + us * (s2x - s1x), s1y + us * (s2y - s1y))
    if virtual:
        return res

    # 0 = intersection point is the start point of the line
    # 1 = intersection point is the end point of the line
    # otherwise: linear interpolation
    if lwr <= us <= upr:  # intersection point is on the subject line
        with cython.cdivision(True):
            uc = ((s2x - s1x) * (s1y - c1y) - (s2y - s1y) * (s1x - c1x)) / den
        if lwr <= uc <= upr:  # intersection point is on the clipping line
            return res
    return None

cdef double _determinant(CppVec3 v1, CppVec3 v2, CppVec3 v3):
    return v1.x * v2.y * v3.z + v1.y * v2.z * v3.x + \
           v1.z * v2.x * v3.y - v1.z * v2.y * v3.x - \
           v1.x * v2.z * v3.y - v1.y * v2.x * v3.z

def intersection_ray_ray_3d(ray1: Tuple[Vec3, Vec3],
                            ray2: Tuple[Vec3, Vec3],
                            double abs_tol=TOLERANCE) -> Sequence[Vec3]:
    """
    Calculate intersection of two 3D rays, returns a 0-tuple for parallel rays,
    a 1-tuple for intersecting rays and a 2-tuple for not intersecting and not
    parallel rays with points of closest approach on each ray.

    Args:
        ray1: first ray as tuple of two points as Vec3() objects
        ray2: second ray as tuple of two points as Vec3() objects
        abs_tol: absolute tolerance for comparisons

    """
    # source: http://www.realtimerendering.com/intersections.html#I304
    cdef CppVec3 o2_o1
    cdef double det1, det2
    # Vec3() objects as input are not guaranteed, a hard <Vec3> cast could
    # crash the interpreter for an invalid input!
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

def arc_angle_span_deg(double start, double end) -> float:
    if isclose(start, end, REL_TOL, DEG_ABS_TOL):
        return 0.0

    start %= 360.0
    if isclose(start, end % 360.0, REL_TOL, DEG_ABS_TOL):
        return 360.0

    if not isclose(end, 360.0, REL_TOL, DEG_ABS_TOL):
        end %= 360.0

    if end < start:
        end += 360.0
    return end - start

def arc_angle_span_rad(double start, double end) -> float:
    if isclose(start, end, REL_TOL, RAD_ABS_TOL):
        return 0.0

    start %= M_TAU
    if isclose(start, end % M_TAU, REL_TOL, RAD_ABS_TOL):
        return M_TAU

    if not isclose(end, M_TAU, REL_TOL, RAD_ABS_TOL):
        end %= M_TAU

    if end < start:
        end += M_TAU
    return end - start
