# Author:  mozman <me@mozman.at>
# Purpose: special 2D vector, optimized for speed
# License: MIT License
from typing import List, Iterable, Union, Sequence, TYPE_CHECKING
from functools import partial
import math

if TYPE_CHECKING:
    from ezdxf.eztypes import VecXY, Vertex


isclose = partial(math.isclose, abs_tol=1e-14)


TVec2 = Union["VecXY", Sequence[float]]


class Vec2:
    """
    Vec2 represents a special 2D Vector (x, y). This class is optimized for speed.

    Args:
        v: Vec2 or sequence of float [x, y, ...]

    """
    __slots__ = ['x', 'y']

    def __init__(self, v: TVec2):
        if isinstance(v, Vec2):
            self.x = v.x
            self.y = v.y
        else:
            self.x = v[0]
            self.y = v[1]

    @classmethod
    def list(cls, items: Iterable[TVec2]) -> List['Vec2']:
        return list(cls.generate(items))

    @classmethod
    def generate(cls, items: Iterable[TVec2]) -> Iterable['Vec2']:
        return (cls(item) for item in items)

    @classmethod
    def from_angle(cls, angle: float, length: float = 1.) -> 'Vec2':
        return cls((math.cos(angle) * length, math.sin(angle) * length))

    @classmethod
    def from_deg_angle(cls, angle: float, length: float = 1.) -> 'Vec2':
        return cls.from_angle(math.radians(angle), length)

    def __str__(self) -> str:
        return '({0.x}, {0.y})'.format(self)

    def __repr__(self) -> str:
        return 'Vector' + self.__str__()

    def __len__(self) -> int:
        return 2

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def copy(self) -> 'Vec2':
        return self.__class__((self.x, self.y))

    __copy__ = copy

    def __deepcopy__(self, memodict: dict) -> 'Vec2':
        try:
            return memodict[id(self)]
        except KeyError:
            v = self.copy()
            memodict[id(self)] = v
            return v

    def __getitem__(self, index: int) -> float:
        return (self.x, self.y)[index]

    def __iter__(self) -> Iterable[float]:
        yield self.x
        yield self.y

    def __abs__(self) -> float:
        return self.magnitude

    @property
    def magnitude(self) -> float:
        """
        Faster magnitude function for only 2d purposes.

        """
        return math.hypot(self.x, self.y)

    @property
    def is_null(self) -> bool:
        return isclose(self.x, 0.) and isclose(self.y, 0.)

    @property
    def angle(self) -> float:
        """
        Angle of vector.

        Returns:
            angle in radians

        """
        return math.atan2(self.y, self.x)

    @property
    def angle_deg(self) -> float:
        """
        Angle of vector.

        Returns:
            angle in degrees

        """
        return math.degrees(self.angle)

    def orthogonal(self, ccw: bool = True) -> 'Vec2':
        """
        Orthogonal vector

        Args:
            ccw: counter clockwise if True else clockwise

        """
        if ccw:
            return Vec2((-self.y, self.x))
        else:
            return Vec2((self.y, -self.x))

    def lerp(self, other: 'VecXY', factor: float = .5) -> 'Vec2':
        """
        Linear interpolation between `self` and `other`.
        
        Args:
            other: target vector/point
            factor: interpolation factor (0=self, 1=other, 0.5=mid point)

        Returns: interpolated vector

        """
        d = (other - self) * factor
        return self.__add__(d)

    def project(self, other: 'VecXY') -> 'Vec2':
        """
        Project vector `other` onto `self`.

        """
        uv = self.normalize()
        return uv * uv.dot(other)

    def normalize(self, length: float = 1.) -> 'Vec2':
        return self.__mul__(length / self.magnitude)

    def reversed(self) -> 'Vec2':
        return Vec2((-self.x, -self.y))

    __neg__ = reversed

    def __bool__(self) -> bool:
        return not self.is_null

    def isclose(self, other: 'VecXY', abs_tol: float = 1e-12) -> bool:
        return math.isclose(self.x, other.x, abs_tol=abs_tol) and math.isclose(self.y, other.y, abs_tol=abs_tol)

    def __eq__(self, other: 'Vertex') -> bool:
        x, y, *_ = other
        return isclose(self.x, x) and isclose(self.y, y)

    def __lt__(self, other: 'Vertex') -> bool:
        x, y, *_ = other
        if self.x == x:
            return self.y < y
        else:
            return self.x < x

    def __add__(self, other: Union['VecXY', float]) -> 'Vec2':
        if isinstance(other, (float, int)):
            return self.__class__((self.x + other, self.y + other))
        else:
            return self.__class__((self.x + other.x, self.y + other.y))

    def __radd__(self, other: Union['VecXY', float]) -> 'Vec2':
        return self.__add__(other)

    def __iadd__(self, other: Union['VecXY', float]) -> 'Vec2':
        if isinstance(other, (float, int)):
            x = other
            y = other
        else:
            x = other.x
            y = other.y
        self.x += x
        self.y += y
        return self

    def __sub__(self, other: Union['VecXY', float]) -> 'Vec2':
        if isinstance(other, (float, int)):
            return self.__class__((self.x - other, self.y - other))
        else:
            return self.__class__((self.x - other.x, self.y - other.y))

    def __rsub__(self, other: Union['VecXY', float]) -> 'Vec2':
        if isinstance(other, (float, int)):
            return self.__class__((other - self.x, other - self.y))
        else:
            return self.__class__((other.x - self.x, other.y - self.y))

    def __isub__(self, other: Union['VecXY', float]) -> 'Vec2':
        if isinstance(other, (float, int)):
            x = other
            y = other
        else:
            x = other.x
            y = other.y
        self.x -= x
        self.y -= y
        return self

    def __mul__(self, other: float) -> 'Vec2':
        return self.__class__((self.x * other, self.y * other))

    def __rmul__(self, other: float) -> 'Vec2':
        return self.__mul__(other)

    def __imul__(self, other: float) -> 'Vec2':
        self.x *= other
        self.y *= other
        return self

    def __truediv__(self, other: float) -> 'Vec2':
        return self.__class__((self.x / other, self.y / other))

    __div__ = __truediv__

    def __itruediv__(self, other: float) -> 'Vec2':
        self.x /= other
        self.y /= other
        return self

    __idiv__ = __itruediv__

    def __rtruediv__(self, other: float) -> 'Vec2':
        return self.__class__((other / self.x, other / self.y))

    __rdiv__ = __rtruediv__

    def dot(self, other: 'VecXY') -> float:
        return self.x * other.x + self.y * other.y

    def distance(self, other: 'VecXY') -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def angle_between(self, other: 'VecXY') -> float:
        """
        Calculate angle between `self` and `other` in radians. +angle is counter clockwise orientation.

        """
        return math.acos(self.normalize().dot(other.normalize()))

    def rotate(self, angle: float) -> 'Vec2':
        """
        Rotate vector around origin.

        Args:
            angle: angle in radians

        """
        return Vec2.from_angle(self.angle + angle, self.magnitude)

    def rotate_deg(self, angle: float) -> 'Vec2':
        """
        Rotate vector around origin.

        Args:
            angle: angle in degrees

        Returns: rotated vector

        """
        return Vec2.from_angle(self.angle + math.radians(angle), self.magnitude)
