# cython: language_level=3
# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
from typing import List, Tuple, TYPE_CHECKING, Sequence

from .vector cimport Vec3, isclose, v3_lerp, v3_dist
from .matrix44 cimport Matrix44

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

__all__ = ['Bezier4P']

# noinspection PyUnresolvedReferences
cdef class Bezier4P:
    cdef Vec3 p0
    cdef Vec3 p1
    cdef Vec3 p2
    cdef Vec3 p3

    def __cinit__(self, defpoints: Sequence['Vertex']):
        if len(defpoints) == 4:
            self.p0 = Vec3(defpoints[0])
            self.p1 = Vec3(defpoints[1])
            self.p2 = Vec3(defpoints[2])
            self.p3 = Vec3(defpoints[3])
        else:
            raise ValueError("Four control points required.")

    @property
    def control_points(self) -> Tuple[Vec3, Vec3, Vec3, Vec3]:
        return self.p0, self.p1, self.p2, self.p3

    def point(self, double t) -> Vec3:
        cdef double weights[4]
        if 0.0 <= t <= 1.0:
            bernstein3(t, weights)
            return bezier_point(self, weights)
        else:
            raise ValueError("t not in range [0 to 1]")

    def tangent(self, double t) -> Vec3:
        cdef double weights[4]
        if 0.0 <= t <= 1.0:
            bernstein3_d1(t, weights)
            return bezier_point(self, weights)
        else:
            raise ValueError("t not in range [0 to 1]")

    def approximate(self, int segments) -> List[Vec3]:
        cdef double weights[4]
        cdef double delta_t, t
        cdef int segment
        cdef list points = [self.p0]

        if segments < 1:
            raise ValueError(segments)
        delta_t = 1.0 / segments

        for segment in range(1, segments):
            t = delta_t * segment
            bernstein3(t, weights)
            points.append(bezier_point(self, weights))
        points.append(self.p3)
        return points

    def flattening(self, double distance, int segments = 4) -> List[Vec3]:
        cdef double weights[4]
        cdef double dt = 1.0 / segments
        cdef double t0 = 0.0, t1
        cdef Vec3 start_point = self.p0
        cdef Vec3 end_point
        cdef SubDiv s = SubDiv(self, distance, start_point)

        while t0 < 1.0:
            t1 = t0 + dt
            if isclose(t1, 1.0):
                end_point = self.p3
                t1 = 1.0
            else:
                bernstein3(t1, weights)
                end_point = bezier_point(self, weights)
            s.subdiv(start_point, end_point, t0, t1)
            t0 = t1
            start_point = end_point
        return s.points

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

    def reverse(self) -> 'Bezier4P':
        return Bezier4P((self.p3, self.p2, self.p1, self.p0))

    def transform(self, Matrix44 m) -> 'Bezier4P':
        transform = m.transform
        return Bezier4P((
            transform(self.p0),
            transform(self.p1),
            transform(self.p2),
            transform(self.p3),
        ))

cdef void bernstein3(double t, double *weights):
    cdef double t2 = t * t
    cdef double _1_minus_t = 1.0 - t
    cdef double _1_minus_t_square = _1_minus_t * _1_minus_t
    weights[0] = _1_minus_t_square * _1_minus_t
    weights[1] = 3.0 * _1_minus_t_square * t
    weights[2] = 3.0 * _1_minus_t * t2
    weights[3] = t2 * t

cdef void bernstein3_d1(double t, double *weights):
    cdef double t2 = t * t
    weights[0] = -3.0 * (1.0 - t) * (1.0 - t)
    weights[1] = 3.0 * (1.0 - 4.0 * t + 3.0 * t2)
    weights[2] = 3.0 * t * (2.0 - 3.0 * t)
    weights[3] = 3.0 * t2

cdef Vec3 bezier_point(Bezier4P curve, double *weights):
    cdef Vec3 p0 = curve.p0
    cdef Vec3 p1 = curve.p1
    cdef Vec3 p2 = curve.p2
    cdef Vec3 p3 = curve.p3
    cdef Vec3 res = Vec3()
    cdef double a = weights[0], b = weights[1], c = weights[2], d = weights[3]
    res.x = p0.x * a + p1.x * b + p2.x * c + p3.x * d
    res.y = p0.y * a + p1.y * b + p2.y * c + p3.y * d
    res.z = p0.z * a + p1.z * b + p2.z * c + p3.z * d
    return res

cdef class SubDiv:
    cdef Bezier4P curve
    cdef double distance
    cdef list points

    def __cinit__(self, Bezier4P curve, double distance, Vec3 point):
        self.curve = curve
        self.distance = distance
        self.points = [point]

    cdef subdiv(self, Vec3 start_point, Vec3 end_point, double start_t,
                double end_t):
        cdef double weights[4]
        cdef double mid_t = (start_t + end_t) * 0.5

        bernstein3(mid_t, weights)
        cdef Vec3 mid_point = bezier_point(self.curve, weights)
        cdef double d = v3_dist(
            v3_lerp(start_point, end_point, 0.5), mid_point)
        if d < self.distance:
            self.points.append(end_point)
        else:
            self.subdiv(start_point, mid_point, start_t, mid_t)
            self.subdiv(mid_point, end_point, mid_t, end_t)
