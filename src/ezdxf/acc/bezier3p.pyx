# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2021-2022 Manfred Moitzi
# License: MIT License
from typing import List, Tuple, TYPE_CHECKING, Sequence
from .vector cimport Vec3, isclose, v3_dist, v3_from_cpp_vec3, v3_add
from .matrix44 cimport Matrix44
from ._cpp_vec3 cimport CppVec3
from ._cpp_quad_bezier cimport CppQuadBezier

if TYPE_CHECKING:
    from ezdxf.math import UVec

__all__ = ['Bezier3P']

cdef double ABS_TOL = 1e-12
cdef double REL_TOL = 1e-9
cdef double M_PI = 3.141592653589793
cdef double M_TAU = M_PI * 2.0
cdef double DEG2RAD = M_PI / 180.0
cdef double RECURSION_LIMIT = 1000

# noinspection PyUnresolvedReferences
cdef class Bezier3P:
    cdef CppQuadBezier curve
    cdef Vec3 offset

    def __cinit__(self, defpoints: Sequence[UVec]):
        cdef CppVec3 cpp_offset
        if len(defpoints) == 3:
            self.offset = Vec3(defpoints[0])
            cpp_offset = self.offset.to_cpp_vec3()
            self.curve = CppQuadBezier(
                CppVec3(),
                Vec3(defpoints[1]).to_cpp_vec3() - cpp_offset,
                Vec3(defpoints[2]).to_cpp_vec3() - cpp_offset,
            )
        else:
            raise ValueError("Three control points required.")

    @property
    def control_points(self) -> Tuple[Vec3, Vec3, Vec3]:
        cdef CppVec3 cpp_offset = self.offset.to_cpp_vec3()
        return self.offset, \
               v3_from_cpp_vec3(self.curve.p1 + cpp_offset), \
               v3_from_cpp_vec3(self.curve.p2 + cpp_offset)

    @property
    def start_point(self) -> Vec3:
        return self.offset

    @property
    def end_point(self) -> Vec3:
        return v3_add(v3_from_cpp_vec3(self.curve.p2), self.offset)

    def __reduce__(self):
        return Bezier3P, (self.control_points,)

    def point(self, double t) -> Vec3:
        if 0.0 <= t <= 1.0:
            return v3_add(v3_from_cpp_vec3(self.curve.point(t)), self.offset)
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
            points.append(self.point(delta_t * segment))
        points.append(self.end_point)
        return points

    def flattening(self, double distance, int segments = 4) -> List[Vec3]:
        cdef double dt = 1.0 / segments
        cdef double t0 = 0.0, t1
        cdef _Flattening f = _Flattening(self, distance)
        cdef CppVec3 start_point = self.curve.p0
        cdef CppVec3 end_point
        cdef Vec3 offset = self.offset
        # Flattening of the translated curve!
        while t0 < 1.0:
            t1 = t0 + dt
            if isclose(t1, 1.0, REL_TOL, ABS_TOL):
                end_point = self.curve.p2
                t1 = 1.0
            else:
                end_point = self.curve.point(t1)
            f.reset_recursion_check()
            f.flatten(start_point, end_point, t0, t1)
            if f.has_recursion_error():
                raise RecursionError(
                    "Bezier3P flattening error, check for very large coordinates"
                )
            t0 = t1
            start_point = end_point
        # translate vertices to original location:
        return [v3_add(p, offset) for p in f.points]

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
    cdef int _recursion_level
    cdef int _recursion_error

    def __cinit__(self, Bezier3P curve, double distance):
        self.curve = curve.curve
        self.distance = distance
        self.points = [v3_from_cpp_vec3(self.curve.p0)]
        self._recursion_level = 0
        self._recursion_error = 0

    cdef has_recursion_error(self):
        return self._recursion_error

    cdef reset_recursion_check(self):
        self._recursion_level = 0
        self._recursion_error = 0

    cdef flatten(
        self,
        CppVec3 start_point,
        CppVec3 end_point,
        double start_t,
        double end_t
    ):
        if self._recursion_level > RECURSION_LIMIT:
            self._recursion_error = 1
            return
        self._recursion_level += 1
        cdef double mid_t = (start_t + end_t) * 0.5
        cdef CppVec3 mid_point = self.curve.point(mid_t)
        cdef double d = mid_point.distance(start_point.lerp(end_point, 0.5))
        if d < self.distance:
            # Convert CppVec3 to Python type Vec3:
            self.points.append(v3_from_cpp_vec3(end_point))
        else:
            self.flatten(start_point, mid_point, start_t, mid_t)
            self.flatten(mid_point, end_point, mid_t, end_t)
        self._recursion_level -= 1