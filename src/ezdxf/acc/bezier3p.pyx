# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2021-2024 Manfred Moitzi
# License: MIT License
# type: ignore -- pylance sucks at type-checking cython files
from typing import TYPE_CHECKING, Sequence
from .vector cimport Vec3, isclose, v3_dist, v3_lerp, v3_add, Vec2
from .matrix44 cimport Matrix44
import warnings
if TYPE_CHECKING:
    from ezdxf.math import UVec

__all__ = ['Bezier3P']

cdef extern from "constants.h":
    const double ABS_TOL
    const double REL_TOL

cdef double RECURSION_LIMIT = 1000


cdef class Bezier3P:
    cdef ControlPoints curve
    cdef Vec3 offset

    def __cinit__(self, defpoints: Sequence[UVec]):
        if not isinstance(defpoints[0], (Vec2, Vec3)):
            warnings.warn(
                DeprecationWarning, 
                "Bezier3P requires defpoints of type Vec2 or Vec3 in the future",
            )
        if len(defpoints) == 3:
            offset = Vec3(defpoints[0])
            self.offset = offset
            self.curve = ControlPoints(
                Vec3(),
                Vec3(defpoints[1]) - offset,
                Vec3(defpoints[2]) - offset,
            )
        else:
            raise ValueError("Three control points required.")

    @property
    def control_points(self) -> tuple[Vec3, Vec3, Vec3]:
        offset = self.offset
        return offset, v3_add(self.curve.p1, offset), v3_add(self.curve.p2, offset)

    @property
    def start_point(self) -> Vec3:
        return self.offset

    @property
    def end_point(self) -> Vec3:
        return v3_add(self.curve.p2, self.offset)

    def __reduce__(self):
        return Bezier3P, (self.control_points,)

    def point(self, double t) -> Vec3:
        if 0.0 <= t <= 1.0:
            return v3_add(self.curve.point(t), self.offset)
        else:
            raise ValueError("t not in range [0 to 1]")

    def tangent(self, double t) -> Vec3:
        if 0.0 <= t <= 1.0:
            return self.curve.tangent(t)
        else:
            raise ValueError("t not in range [0 to 1]")

    def approximate(self, int segments) -> list[Vec3]:
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

    def flattening(self, double distance, int segments = 4) -> list[Vec3]:
        cdef double dt = 1.0 / segments
        cdef double t0 = 0.0, t1
        cdef _Flattening f = _Flattening(self, distance)
        cdef Vec3 start_point = self.curve.p0
        cdef Vec3 end_point
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

    def reverse(self) -> Bezier3P:
        p0, p1, p2 = self.control_points
        return Bezier3P((p2, p1, p0))

    def transform(self, Matrix44 m) -> Bezier3P:
        p0, p1, p2 = self.control_points
        transform = m.transform
        return Bezier3P((
            transform(p0),
            transform(p1),
            transform(p2),
        ))

cdef class _Flattening:
    cdef ControlPoints curve
    cdef double distance
    cdef list points
    cdef int _recursion_level
    cdef int _recursion_error

    def __cinit__(self, Bezier3P curve, double distance):
        self.curve = curve.curve
        self.distance = distance
        self.points = [self.curve.p0]
        self._recursion_level = 0
        self._recursion_error = 0

    cdef has_recursion_error(self):
        return self._recursion_error

    cdef reset_recursion_check(self):
        self._recursion_level = 0
        self._recursion_error = 0

    cdef flatten(
        self,
        Vec3 start_point,
        Vec3 end_point,
        double start_t,
        double end_t
    ):
        if self._recursion_level > RECURSION_LIMIT:
            self._recursion_error = 1
            return
        self._recursion_level += 1
        cdef double mid_t = (start_t + end_t) * 0.5
        cdef Vec3 mid_point = self.curve.point(mid_t)
        cdef double d = v3_dist(mid_point, v3_lerp(start_point,end_point, 0.5))
        if d < self.distance:
            # Convert CppVec3 to Python type Vec3:
            self.points.append(end_point)
        else:
            self.flatten(start_point, mid_point, start_t, mid_t)
            self.flatten(mid_point, end_point, mid_t, end_t)
        self._recursion_level -= 1

cdef class ControlPoints:
    cdef:
        Vec3 p0
        Vec3 p1
        Vec3 p2

    def __cinit__(self, Vec3 p0, Vec3 p1, Vec3 p2):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2


    cdef Vec3 point(self, double t):
        cdef double _1_minus_t = 1.0 - t
        cdef double a = _1_minus_t * _1_minus_t
        cdef double b = 2.0 * t * _1_minus_t
        cdef double c = t * t
        return self.evaluate(a, b, c)


    cdef Vec3 tangent(self, double t):
        cdef double a = -2.0 * (1.0 - t)
        cdef double b = 2.0 - 4.0 * t
        cdef double c = 2.0 * t
        return self.evaluate(a, b, c)


    cdef Vec3 evaluate(self, double a, double b, double c):
        cdef Vec3 result = Vec3()

        iadd_mul(result, self.p0, a)
        iadd_mul(result, self.p1, b)
        iadd_mul(result, self.p2, c)
        return result


cdef void iadd_mul(Vec3 p, Vec3 cp, double f):
    p.x += cp.x * f
    p.y += cp.y * f
    p.z += cp.z * f
