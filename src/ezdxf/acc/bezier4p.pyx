# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
from typing import List, Tuple, TYPE_CHECKING, Sequence, Iterable
import cython
from .vector cimport (
Vec3, isclose, v3_lerp, v3_dist, v3_from_angle, normalize_rad_angle,
normalize_deg_angle, v3_from_cpp_vec3,
)
from .matrix44 cimport Matrix44
from libc.math cimport ceil, M_PI, tan

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex
    from ezdxf.math.ellipse import ConstructionEllipse

__all__ = [
    'Bezier4P', 'cubic_bezier_arc_parameters',
    'cubic_bezier_from_arc', 'cubic_bezier_from_ellipse',
]

DEF ABS_TOL = 1e-12
cdef double M_TAU = M_PI * 2.0
cdef double DEG2RAD = M_PI / 180.0

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
            if isclose(t1, 1.0, ABS_TOL):
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

cdef double DEFAULT_TANGENT_FACTOR = 4.0 / 3.0  # 1.333333333333333333
cdef double OPTIMIZED_TANGENT_FACTOR = 1.3324407374108935
cdef double TANGENT_FACTOR = DEFAULT_TANGENT_FACTOR

@cython.cdivision(True)
def cubic_bezier_arc_parameters(
        double start_angle, double end_angle,
        int segments = 1) -> Iterable[Tuple[Vec3, Vec3, Vec3, Vec3]]:
    if segments < 1:
        raise ValueError('Invalid argument segments (>= 1).')
    cdef double delta_angle = end_angle - start_angle
    cdef int arc_count
    if delta_angle > 0:
        arc_count = <int> ceil(delta_angle / M_PI * 2.0)
        if segments > arc_count:
            arc_count = segments
    else:
        raise ValueError('Delta angle from start- to end angle has to be > 0.')

    cdef double segment_angle = delta_angle / arc_count
    cdef double tangent_length = TANGENT_FACTOR * tan(segment_angle / 4.0)
    cdef double angle = start_angle
    cdef Vec3 start_point, end_point, cp1, cp2
    end_point = v3_from_angle(angle, 1.0)

    for _ in range(arc_count):
        start_point = end_point
        angle += segment_angle
        end_point = v3_from_angle(angle, 1.0)
        cp1 = Vec3()
        cp1.x = start_point.x - start_point.y * tangent_length
        cp1.y = start_point.y + start_point.x * tangent_length
        cp2 = Vec3()
        cp2.x = end_point.x + end_point.y * tangent_length
        cp2.y = end_point.y - end_point.x * tangent_length
        yield start_point, cp1, cp2, end_point

def cubic_bezier_from_arc(
        center = (0, 0), double radius = 1.0, double start_angle = 0.0,
        double end_angle = 360.0, int segments = 1) -> Iterable[Bezier4P]:
    cdef CppVec3 center_ = Vec3(center).to_cpp_vec3()
    cdef CppVec3 tmp
    cdef list res
    cdef int i

    start_angle = normalize_deg_angle(start_angle) * DEG2RAD
    end_angle = normalize_deg_angle(end_angle) * DEG2RAD

    if isclose(end_angle, 0.0, ABS_TOL):
        end_angle = M_TAU
    if start_angle > end_angle:
        end_angle += M_TAU
    if isclose(end_angle, start_angle, ABS_TOL):
        return

    for control_points in cubic_bezier_arc_parameters(
            start_angle, end_angle, segments):
        res = list()
        for i in range(4):
            tmp = (<Vec3> control_points[i]).to_cpp_vec3()
            res.append(v3_from_cpp_vec3(center_ + tmp * radius))
        yield Bezier4P(res)

def cubic_bezier_from_ellipse(ellipse: 'ConstructionEllipse',
                              int segments = 1) -> Iterable[Bezier4P]:
    cdef start_angle = normalize_rad_angle(ellipse.start_param)
    cdef end_angle = normalize_rad_angle(ellipse.end_param)

    if isclose(end_angle, 0.0, ABS_TOL):
        end_angle = M_TAU

    if start_angle > end_angle:
        end_angle += M_TAU

    if isclose(end_angle, start_angle, ABS_TOL):
        return

    cdef CppVec3 center = Vec3(ellipse.center).to_cpp_vec3()
    cdef CppVec3 x_axis = Vec3(ellipse.major_axis).to_cpp_vec3()
    cdef CppVec3 y_axis = Vec3(ellipse.minor_axis).to_cpp_vec3()
    cdef Vec3 cp,
    cdef CppVec3 c_res
    cdef list res
    for control_points in cubic_bezier_arc_parameters(
            start_angle, end_angle, segments):
        res = list()
        for i in range(4):
            cp = <Vec3> control_points[i]
            c_res = center + x_axis * cp.x + y_axis * cp.y
            res.append(v3_from_cpp_vec3(c_res))
        yield Bezier4P(res)