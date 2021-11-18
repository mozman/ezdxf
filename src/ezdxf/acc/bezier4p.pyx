# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
from typing import List, Tuple, TYPE_CHECKING, Sequence, Iterable
import cython
from .vector cimport (
    Vec3, isclose, v3_dist, v3_from_angle, normalize_rad_angle,
    v3_from_cpp_vec3,
)
from .matrix44 cimport Matrix44
from libc.math cimport ceil, tan
from ._cpp_vec3 cimport CppVec3
from ._cpp_cubic_bezier cimport CppCubicBezier
from .construct import arc_angle_span_deg

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex
    from ezdxf.math.ellipse import ConstructionEllipse

__all__ = [
    'Bezier4P', 'cubic_bezier_arc_parameters',
    'cubic_bezier_from_arc', 'cubic_bezier_from_ellipse',
]

DEF ABS_TOL = 1e-12
DEF REL_TOL = 1e-9
DEF M_PI = 3.141592653589793
DEF M_TAU = M_PI * 2.0
DEF DEG2RAD = M_PI / 180.0


# noinspection PyUnresolvedReferences
cdef class Bezier4P:
    cdef CppCubicBezier curve

    def __cinit__(self, defpoints: Sequence['Vertex']):
        if len(defpoints) == 4:
            self.curve = CppCubicBezier(
                Vec3(defpoints[0]).to_cpp_vec3(),
                Vec3(defpoints[1]).to_cpp_vec3(),
                Vec3(defpoints[2]).to_cpp_vec3(),
                Vec3(defpoints[3]).to_cpp_vec3(),
            )
        else:
            raise ValueError("Four control points required.")

    @property
    def control_points(self) -> Tuple[Vec3, Vec3, Vec3, Vec3]:
        return v3_from_cpp_vec3(self.curve.p0), \
               v3_from_cpp_vec3(self.curve.p1), \
               v3_from_cpp_vec3(self.curve.p2), \
               v3_from_cpp_vec3(self.curve.p3)

    @property
    def start_point(self) -> Vec3:
        return v3_from_cpp_vec3(self.curve.p0)

    @property
    def end_point(self) -> Vec3:
        return v3_from_cpp_vec3(self.curve.p3)

    def __reduce__(self):
        return Bezier4P, (self.control_points,)

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

    def reverse(self) -> 'Bezier4P':
        p0, p1, p2, p3 = self.control_points
        return Bezier4P((p3, p2, p1, p0))

    def transform(self, Matrix44 m) -> 'Bezier4P':
        p0, p1, p2, p3 = self.control_points
        transform = m.transform
        return Bezier4P((
            transform(<Vec3> p0),
            transform(<Vec3> p1),
            transform(<Vec3> p2),
            transform(<Vec3> p3),
        ))

cdef class _Flattening:
    cdef CppCubicBezier curve
    cdef double distance
    cdef list points

    def __cinit__(self, Bezier4P curve, double distance):
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
            # keep in sync with CPython implementation: ezdxf/math/_bezier4p.py
            # Convert CppVec3 to Python type Vec3:
            self.points.append(v3_from_cpp_vec3(end_point))
        else:
            self.flatten(start_point, mid_point, start_t, mid_t)
            self.flatten(mid_point, end_point, mid_t, end_t)

DEF DEFAULT_TANGENT_FACTOR = 4.0 / 3.0  # 1.333333333333333333
DEF OPTIMIZED_TANGENT_FACTOR = 1.3324407374108935
DEF TANGENT_FACTOR = DEFAULT_TANGENT_FACTOR

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
    cdef double angle_span = arc_angle_span_deg(start_angle, end_angle)
    if abs(angle_span) < 1e-9:
        return

    cdef double s = start_angle
    start_angle = (s * DEG2RAD) % M_TAU
    end_angle = (s + angle_span) * DEG2RAD
    while start_angle > end_angle:
        end_angle += M_TAU

    for control_points in cubic_bezier_arc_parameters(
            start_angle, end_angle, segments):
        res = list()
        for i in range(4):
            tmp = (<Vec3> control_points[i]).to_cpp_vec3()
            res.append(v3_from_cpp_vec3(center_ + tmp * radius))
        yield Bezier4P(res)

def cubic_bezier_from_ellipse(ellipse: 'ConstructionEllipse',
                              int segments = 1) -> Iterable[Bezier4P]:
    cdef double param_span = ellipse.param_span
    if abs(param_span) < 1e-9:
        return

    cdef double start_angle = normalize_rad_angle(ellipse.start_param)
    cdef double end_angle = start_angle + param_span

    while start_angle > end_angle:
        end_angle += M_TAU

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
