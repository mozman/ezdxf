# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2021 Manfred Moitzi
# License: MIT License
from typing import List, Tuple, TYPE_CHECKING, Sequence
from .vector cimport Vec3, isclose, v3_dist,   v3_from_cpp_vec3
from .matrix44 cimport Matrix44
from ._cpp_vec3 cimport CppVec3
from ._cpp_quad_bezier cimport CppQuadBezier

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

__all__ = ['Bezier3P']

DEF ABS_TOL = 1e-12
DEF REL_TOL = 1e-9
DEF M_PI = 3.141592653589793
DEF M_TAU = M_PI * 2.0
DEF DEG2RAD = M_PI / 180.0

# noinspection PyUnresolvedReferences
cdef class Bezier3P:
    cdef CppQuadBezier curve

    def __cinit__(self, defpoints: Sequence['Vertex']):
        if len(defpoints) == 3:
            self.curve = CppQuadBezier(
                Vec3(defpoints[0]).to_cpp_vec3(),
                Vec3(defpoints[1]).to_cpp_vec3(),
                Vec3(defpoints[2]).to_cpp_vec3(),
            )
        else:
            raise ValueError("Three control points required.")

    @property
    def control_points(self) -> Tuple[Vec3, Vec3, Vec3]:
        return v3_from_cpp_vec3(self.curve.p0), \
               v3_from_cpp_vec3(self.curve.p1), \
               v3_from_cpp_vec3(self.curve.p2)

    @property
    def start_point(self) -> Vec3:
        return v3_from_cpp_vec3(self.curve.p0)

    @property
    def end_point(self) -> Vec3:
        return v3_from_cpp_vec3(self.curve.p2)

    def __reduce__(self):
        return Bezier3P, (self.control_points,)

    def point(self, double t) -> Vec3:
        if 0.0 <= t <= 1.0:
            return v3_from_cpp_vec3(self.curve.point(t))
        else:
            raise ValueError("t not in range [0 to 1]")

    def tangent(self, double t) -> Vec3:
        if 0.0 <= t <= 1.0:
            return v3_from_cpp_vec3(self.curve.tangent(t))
        else:
            raise ValueError("t not in range [0 to 1]")

    def approximate(self, int segments) -> List[Vec3]:
        # A C++ implementation using std::vector<CppVec3> as return type
        # was significant slower than the current implementation.
        cdef double delta_t
        cdef int segment
        cdef list points = [self.start_point]

        if segments < 1:
            raise ValueError(segments)
        delta_t = 1.0 / segments
        for segment in range(1, segments):
            points.append(v3_from_cpp_vec3(
                self.curve.point(delta_t * segment)
            ))
        points.append(self.end_point)
        return points

    def flattening(self, double distance, int segments = 4) -> List[Vec3]:
        cdef double dt = 1.0 / segments
        cdef double t0 = 0.0, t1
        cdef _Flattening f = _Flattening(self, distance)
        cdef CppVec3 start_point = (<Vec3> self.start_point).to_cpp_vec3()
        cdef CppVec3 end_point

        while t0 < 1.0:
            t1 = t0 + dt
            if isclose(t1, 1.0, REL_TOL, ABS_TOL):
                end_point = (<Vec3> self.end_point).to_cpp_vec3()
                t1 = 1.0
            else:
                end_point = self.curve.point(t1)
            f.flatten(start_point, end_point, t0, t1)
            t0 = t1
            start_point = end_point
        return f.points

    def approximated_length(self, segments: int = 128) -> float:
        cdef double length = 0.0
        cdef bint start_flag = 0
        cdef Vec3 prev_point, point

        for point in self.approximate(segments):
            if start_flag:
                length += v3_dist(prev_point, point)
            else:
                start_flag = 1
            prev_point = point
        return length

    def reverse(self) -> 'Bezier3P':
        p0, p1, p2 = self.control_points
        return Bezier3P((p2, p1, p0))

    def transform(self, Matrix44 m) -> 'Bezier3P':
        p0, p1, p2 = self.control_points
        transform = m.transform
        return Bezier3P((
            transform(<Vec3> p0),
            transform(<Vec3> p1),
            transform(<Vec3> p2),
        ))

cdef class _Flattening:
    cdef CppQuadBezier curve
    cdef double distance
    cdef list points

    def __cinit__(self, Bezier3P curve, double distance):
        self.curve = curve.curve
        self.distance = distance
        self.points = [curve.start_point]

    cdef flatten(self, CppVec3 start_point, CppVec3 end_point,
                 double start_t,
                 double end_t):
        cdef double mid_t = (start_t + end_t) * 0.5
        cdef CppVec3 mid_point = self.curve.point(mid_t)
        cdef double d = mid_point.distance(start_point.lerp(end_point, 0.5))
        # very big numbers (>1e99) can cause calculation errors #574
        # distance from 2.999999999999987e+99 to 2.9999999999999e+99 is
        # very big even it is only a floating point imprecision error in the
        # mantissa!
        if d < self.distance or d > 1e12:  # educated guess
            # keep in sync with CPython implementation: ezdxf/math/_bezier3p.py
            # Convert CppVec3 to Python type Vec3:
            self.points.append(v3_from_cpp_vec3(end_point))
        else:
            self.flatten(start_point, mid_point, start_t, mid_t)
            self.flatten(mid_point, end_point, mid_t, end_t)