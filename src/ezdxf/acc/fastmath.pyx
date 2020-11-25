# cython: language_level=3
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable, List, Sequence, TYPE_CHECKING
from libc.math cimport fabs, sin, cos, M_PI, hypot, atan2, acos
import cython

if TYPE_CHECKING:
    from ezdxf.eztypes import VecXY, Vertex

cdef double abs_tol = 1e-12

cdef bint isclose(double a, double b):
    return fabs(a - b) < abs_tol

cdef bint isclose_abs_tol(double a, double b, double tol):
    return fabs(a - b) < tol

cdef double RAD2DEG = 180.0 / M_PI
cdef double DEG2RAD = M_PI / 180.0


cdef class Vec2:
    """ Immutable 2D vector.

    Init:

    - Vec2()
    - Vec2(vec2)
    - Vec2(vec3)
    - Vec2((x, y))
    - Vec2((x, y, z)), ignore z-axis
    - Vec2(x, y)
    - Vec2(x, y, z), ignore z-axis

    """
    cdef readonly double x, y

    def __cinit__(self, *args):
        cdef Py_ssize_t count = len(<tuple> args)

        if count == 0:  # fastest init - default constructor
            self.x = 0
            self.y = 0
            return

        if count == 1:
            arg = args[0]
            if isinstance(arg, Vec2):
                # fast init by Vec2()
                self.x = (<Vec2> arg).x
                self.y = (<Vec2> arg).y
                return
            if isinstance(arg, Vec3):
                # fast init by Vec3()
                self.x = (<Vec3> arg).x
                self.y = (<Vec3> arg).y
                return
            args = arg
            count = len(args)

        # ignore z-axis but raise error for 4 or more arguments
        if count > 3:
            raise TypeError('invalid argument count')

        # slow init by sequence
        self.x = args[0]
        self.y = args[1]

    @property
    def vec3(self) -> 'Vec3':
        return Vec3(self)

    def round(self, ndigits=None) -> 'Vec2':
        # only used for testing
        return Vec2(round(self.x, ndigits), round(self.y, ndigits))

    @staticmethod
    def list(items: Iterable['Vertex']) -> List['Vec2']:
        return list(Vec2.generate(items))

    @staticmethod
    def tuple(items: Iterable['Vertex']) -> Sequence['Vec2']:
        return tuple(Vec2.generate(items))

    @staticmethod
    def generate(items: Iterable['Vertex']) -> Iterable['Vec2']:
        return (Vec2(item) for item in items)

    @staticmethod
    def from_angle(double angle, double length = 1.) -> 'Vec2':
        return v2_from_angle(angle, length)

    @staticmethod
    def from_deg_angle(double angle, double length = 1.0) -> 'Vec2':
        return v2_from_angle(angle * DEG2RAD, length)

    def __str__(self) -> str:
        return '({}, {})'.format(self.x, self.y)

    def __repr__(self) -> str:
        return 'Vec2' + self.__str__()

    def __len__(self) -> int:
        return 2

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def copy(self) -> 'Vec2':
        return self  # immutable

    def __copy__(self) -> 'Vec2':
        return self  # immutable

    def __deepcopy__(self, memodict: dict) -> 'Vec2':
        try:
            return memodict[id(self)]
        except KeyError:
            memodict[id(self)] = self
            return self

    def __getitem__(self, index: int) -> float:
        return (self.x, self.y)[index]

    def __iter__(self) -> Iterable[float]:
        yield self.x
        yield self.y

    def __abs__(self) -> float:
        return hypot(self.x, self.y)

    @property
    def magnitude(self) -> float:
        return hypot(self.x, self.y)

    @property
    def is_null(self) -> bool:
        return self.x == 0 and self.y == 0

    @property
    def angle(self) -> float:
        return atan2(self.y, self.x)

    @property
    def angle_deg(self) -> float:
        return atan2(self.y, self.x) * RAD2DEG

    def orthogonal(self, ccw: bool = True) -> 'Vec2':
        return v2_ortho(self, ccw)

    def lerp(self, other: 'VecXY', double factor = 0.5) -> 'Vec2':
        cdef Vec2 o = Vec2(other)
        return v2_lerp(self, o, factor)

    def normalize(self, double length = 1.) -> Vec2:
        return v2_normalize(self, length)

    def project(self, other: 'VecXY') -> 'Vec2':
        cdef Vec2 o = Vec2(other)
        return v2_project(self, o)

    def __neg__(self) -> 'Vec2':
        cdef Vec2 res = Vec2()
        res.x = -self.x
        res.y = -self.y
        return res

    reversed = __neg__

    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0

    def isclose(self, other: 'VecXY', double abs_tol = 1e-12) -> bool:
        cdef Vec2 o = Vec2(other)
        return isclose_abs_tol(self.x, o.x, abs_tol) and \
               isclose_abs_tol(self.y, o.y, abs_tol)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Vec2):
            other = Vec2(other)
        return bool(v2_isclose(self, other))

    def __lt__(self, other) -> bool:
        cdef Vec2 o = Vec2(other)
        if self.x == o.x:
            return self.y < o.y
        else:
            return self.x < o.x

    def __add__(self, other: 'VecXY') -> 'Vec2':
        cdef Vec2 o = Vec2(other)
        return v2_add(self, o)

    __iadd__ = __add__  # immutable

    def __sub__(self, other: 'VecXY') -> 'Vec2':
        cdef Vec2 o = Vec2(other)
        return v2_sub(self, o)

    def __rsub__(self, other: 'VecXY') -> 'Vec2':
        cdef Vec2 o = Vec2(other)
        return v2_sub(o, self)

    __isub__ = __sub__  # immutable

    def __mul__(self, factor) -> 'Vec2':
        if isinstance(self, Vec2):
            return v2_mul(self, factor)
        elif isinstance(factor, Vec2):
            return v2_mul(<Vec2> factor, <double> self)
        else:
            return NotImplemented

    __imul__ = __mul__  # immutable

    def __truediv__(self, double factor) -> 'Vec2':
        return v2_mul(self, 1.0 / factor)


    def dot(self, other: 'VecXY') -> float:
        cdef Vec2 o = Vec2(other)
        return v2_dot(self, o)

    def det(self, other: 'VecXY') -> float:
        cdef Vec2 o = Vec2(other)
        return v2_det(self, o)

    def distance(self, other: 'VecXY') -> float:
        cdef Vec2 o = Vec2(other)
        return v2_dist(self, o)

    def angle_between(self, other: 'VecXY') -> float:
        cdef Vec2 o = Vec2(other)
        return v2_angle_between(self, o)

    cpdef rotate(self, double angle: float):
        cdef double self_angle = atan2(self.y, self.x)
        cdef double magnitude = hypot(self.x, self.y)
        return v2_from_angle(self_angle + angle, magnitude)

    def rotate_deg(self, double angle) -> 'Vec2':
        return self.rotate(angle * DEG2RAD)

    @staticmethod
    def sum(items: Iterable['Vec2']) -> 'Vec2':
        cdef Vec2 res = Vec2()
        cdef Vec2 tmp
        res.x = 0.0
        res.y = 0.0
        for v in items:
            tmp = v
            res.x += tmp.x
            res.y += tmp.y
        return res


cdef Vec2 v2_add(Vec2 a, Vec2 b):
    res = Vec2()
    res.x = a.x + b.x
    res.y = a.y + b.y
    return res

cdef Vec2 v2_sub(Vec2 a, Vec2 b):
    res = Vec2()
    res.x = a.x - b.x
    res.y = a.y - b.y
    return res

cdef Vec2 v2_mul(Vec2 a, double factor):
    res = Vec2()
    res.x = a.x * factor
    res.y = a.y * factor
    return res

cdef double v2_dot(Vec2 a, Vec2 b):
    return a.x * b.x + a.y * b.y

cdef double v2_det(Vec2 a, Vec2 b):
    return a.x * b.y - a.y * b.x

cdef double v2_dist(Vec2 a, Vec2 b):
    return hypot(a.x - b.x, a.y - b.y)

cdef Vec2 v2_from_angle(double angle, double length = 1.0):
    return Vec2(cos(angle) * length, sin(angle) * length)

cdef double v2_angle_between(Vec2 a, Vec2 b):
    return acos(v2_dot(v2_normalize(a), v2_normalize(b)))

cdef Vec2 v2_normalize(Vec2 a, double length = 1.0):
    cdef double factor = length / hypot(a.x, a.y)
    cdef Vec2 res = Vec2()
    res.x = a.x * factor
    res.y = a.y * factor
    return res

cdef Vec2 v2_lerp(Vec2 a, Vec2 b, double factor = 0.5):
    cdef Vec2 res = Vec2()
    res.x = a.x + (b.x - a.x) * factor
    res.y = a.y + (b.y - a.y) * factor
    return res

cdef Vec2 v2_ortho(Vec2 a, bint ccw):
    cdef Vec2 res = Vec2()
    if ccw:
        res.x = -a.y
        res.y = a.x
    else:
        res.x = a.y
        res.y = -a.x
    return res

cdef Vec2 v2_project(Vec2 a, Vec2 b):
    cdef Vec2 uv = v2_normalize(a)
    return v2_mul(uv, v2_dot(uv, b))

cdef bint v2_isclose(Vec2 a, Vec2 b):
    return isclose(a.x, b.x) and isclose(a.y, b.y)

cdef class Vec3:
    """ Immutable 3D vector.

    Init:

    - Vec3()
    - Vec3(vec3)
    - Vec3(vec2)
    - Vec3((x, y))
    - Vec3((x, y, z))
    - Vec3(x, y)
    - Vec3(x, y, z)

    """
    cdef readonly double x, y, z

    def __cinit__(self, *args):
        cdef Py_ssize_t count = len(<tuple> args)
        if count == 0:  # fastest init - default constructor
            self.x = 0
            self.y = 0
            self.z = 0
            return

        if count == 1:
            arg0 = args[0]
            if isinstance(arg0, Vec3):
                # fast init by Vec3()
                self.x = (<Vec3> arg0).x
                self.y = (<Vec3> arg0).y
                self.z = (<Vec3> arg0).z
                return
            if isinstance(arg0, Vec2):
                # fast init by Vec2()
                self.x = (<Vec2> arg0).x
                self.y = (<Vec2> arg0).y
                self.z = 0
                return
            args = arg0
            count = len(args)

        if count > 3:
            raise TypeError('invalid argument count')

        # slow init by sequence
        self.x = args[0]
        self.y = args[1]
        if count > 2:
            self.z = args[2]
        else:
            self.z = 0.0

    def __len__(self) -> int:
        return 3

    def __eq__(self, other) -> bool:
        if not isinstance(other, Vec3):
            other = Vec3(other)
        return bool(v3_isclose(self, other))

    def __lt__(self, other) -> bool:
        cdef Vec3 o = Vec3(other)
        if self.x == o.x:
            return self.y < o.y
        else:
            return self.x < o.x

    def __repr__(self)-> str:
        return f"Vec3({self.x}, {self.y}, {self.z})"

    def __add__(self, other) -> 'Vec3':
        if not isinstance(other, Vec3):
            other = Vec3(other)
        return v3_add(self, other)

    def __radd__(self, other) -> 'Vec3':
        if not isinstance(other, Vec3):
            other = Vec3(other)
        return v3_add(other, self)

    def __sub__(self, other) -> 'Vec3':
        if not isinstance(other, Vec3):
            other = Vec3(other)
        return v3_sub(self, other)

    def __rsub__(self, other) -> 'Vec3':
        if not isinstance(other, Vec3):
            other = Vec3(other)
        return v3_sub(other, self)

X_AXIS = Vec3(1, 0, 0)
Y_AXIS = Vec3(0, 1, 0)
Z_AXIS = Vec3(0, 0, 1)
NULLVEC = Vec3(0, 0, 0)

cdef Vec3 v3_add(Vec3 a, Vec3 b):
    res = Vec3()
    res.x = a.x + b.x
    res.y = a.y + b.y
    res.z = a.z + b.z
    return res

cdef Vec3 v3_sub(Vec3 a, Vec3 b):
    res = Vec3()
    res.x = a.x - b.x
    res.y = a.y - b.y
    res.z = a.z - b.z
    return res

cdef bint v3_isclose(Vec3 a, Vec3 b):
    return isclose(a.x, b.x) and isclose(a.y, b.y) and isclose(a.z, b.z)
