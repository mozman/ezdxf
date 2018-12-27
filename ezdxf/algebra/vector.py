# Author:  mozman <me@mozman.at>
# Purpose: general purpose vector 2D/3D Vector and 2D/3D Point
# License: MIT License
from typing import Tuple, List, Iterable, Any, Sequence
import math
from .base import is_close, equals_almost


class Vector:
    """
    Vector represents a universal 3D Vector (x, y, z). This class is immutable and optimized for universality not for
    speed.

    Immutable means you can't change (x, y, z) components after initialization::

        v = Vector(1, 2, 3)
        v.x = 10  # raises AttributeError
        v = Vector(10, v.y, v.z)  # create a new vector instead

    Valid __init__() arguments are:

        no args: decompose() -> (0, 0, 0)
        1 arg: decompose(arg), arg is tuple or list, tuple has to be an (x, y[, z]) tuple, decompose((x, y)) -> (x, y, 0.)
        2 args: decompose(x, y), returns (x, y, 0.) tuple
        3 args: decompose(x, y, z) -> (x, y, z)

    """
    __slots__ = ['_x', '_y', '_z']

    def __init__(self, *args):
        self._x, self._y, self._z = self.decompose(*args)

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def z(self) -> float:
        return self._z

    @property
    def xy(self) -> 'Vector':
        """
        Returns Vector (x, y, 0)

        """
        return Vector(self._x, self._y)

    @property
    def xyz(self) -> Tuple[float, float, float]:
        """
        Returns vector as (x, y, z) tuple.

        """
        return self._x, self._y, self._z

    def replace(self, x: float = None, y: float = None, z: float = None) -> 'Vector':
        if x is None:
            x = self._x
        if y is None:
            y = self._y
        if z is None:
            z = self._z
        return self.__class__(x, y, z)

    @staticmethod
    def list(items: Iterable[Iterable]) -> List['Vector']:
        return list(Vector.generate(items))

    @staticmethod
    def generate(items: Iterable[Iterable]) -> Iterable['Vector']:
        return (Vector(item) for item in items)

    @staticmethod
    def from_rad_angle(angle: float, length: float = 1.) -> 'Vector':
        return Vector(math.cos(angle) * length, math.sin(angle) * length, 0.)

    @staticmethod
    def from_deg_angle(angle: float, length: float = 1.) -> 'Vector':
        return Vector.from_rad_angle(math.radians(angle), length)

    @staticmethod
    def decompose(*args) -> Tuple[float, float, float]:
        """
        Converts input into a (x, y, z) tuple.

        Valid arguments are:
            no args: decompose() -> (0, 0, 0)
            1 arg: decompose(arg), arg is tuple or list, tuple has to be an (x, y[, z]) tuple, decompose((x, y)) -> (x, y, 0.)
            2 args: decompose(x, y), returns (x, y, 0.) tuple
            3 args: decompose(x, y, z) -> (x, y, z)

        Returns:
            (x, y, z) tuple

        """
        length = len(args)
        if length == 0:
            return 0., 0., 0.
        elif length == 1:
            data = args[0]
            if isinstance(data, Vector):
                return data._x, data._y, data._z
            elif isinstance(data, (tuple, list)):
                x = data[0]
                y = data[1]
                if len(data) > 2:
                    z = data[2]
                else:
                    z = 0.
                return float(x), float(y), float(z)
        elif length == 2:
            x, y = args
            return float(x), float(y), 0.
        elif length == 3:
            x, y, z = args
            return float(x), float(y), float(z)
        raise ValueError('invalid arguments {}'.format(str(args)))

    def __str__(self) -> str:
        return '({0.x}, {0.y}, {0.z})'.format(self)

    def __repr__(self) -> str:
        return 'Vector' + self.__str__()

    def __len__(self) -> int:
        return 3

    def __hash__(self) -> int:
        return hash(self.xyz)

    def copy(self) -> 'Vector':
        return Vector(self._x, self._y, self._z)

    __copy__ = copy

    def __deepcopy__(self, memodict: dict) -> 'Vector':
        try:
            return memodict[id(self)]
        except KeyError:
            v = self.copy()
            memodict[id(self)] = v
            return v

    def __getitem__(self, index: int) -> float:
        return self.xyz[index]

    def __iter__(self) -> Iterable[float]:
        yield self._x
        yield self._y
        yield self._z

    def __abs__(self) -> float:
        return self.magnitude

    @property
    def magnitude(self) -> float:
        return self.magnitude_square ** .5

    @property
    def magnitude_square(self) -> float:
        x, y, z = self._x, self._y, self._z
        return x * x + y * y + z * z

    @property
    def is_null(self) -> bool:
        return self.__eq__((0, 0, 0))  # __eq__ uses is_close()

    @property
    def spatial_angle_rad(self) -> float:
        """
        Spatial angle between vector and x-axis.

        Returns:
            angle in radians
        """
        return math.acos(X_AXIS.dot(self.normalize()))

    @property
    def spatial_angle_deg(self) -> float:
        """
        Spatial angle between vector and x-axis.

        Returns:
            angle in degrees
        """
        return math.degrees(self.spatial_angle_rad)

    @property
    def angle_rad(self) -> float:
        """
        Angle of vector in the xy-plane

        Returns:
            angle in radians

        """
        return math.atan2(self._y, self._x)

    @property
    def angle_deg(self) -> float:
        """
        Angle of vector in the xy-plane

        Returns:
            angle in degrees

        """
        return math.degrees(self.angle_rad)

    def orthogonal(self, ccw: bool = True) -> 'Vector':
        """
        Orthogonal 2D vector, z value is unchanged.

        Args:
            ccw: counter clockwise if True else clockwise

        """
        return Vector(-self._y, self._x, self._z) if ccw else Vector(self._y, -self._x, self._z)

    def lerp(self, other: Any, factor=.5) -> 'Vector':
        """
        Linear interpolation between `self` and `other`.
        
        Args:
            other: target vector/point
            factor: interpolation factor (0=self, 1=other, 0.5=mid point)

        Returns: interpolated vector

        """
        d = (Vector(other) - self) * float(factor)
        return self.__add__(d)

    def project(self, other: Any) -> 'Vector':
        """
        Project vector `other` onto `self`.

        """
        uv = self.normalize()
        return uv * uv.dot(other)

    def normalize(self, length: float = 1.) -> 'Vector':
        return self.__mul__(length / self.magnitude)

    def reversed(self) -> 'Vector':
        return self.__mul__(-1.)

    __neg__ = reversed

    def __bool__(self) -> bool:
        return not self.is_null

    def is_almost_equal(self, other: Any, places: int = 6) -> bool:
        other = Vector(other)
        return equals_almost(self.x, other.x, places=places) and \
               equals_almost(self.y, other.y, places=places) and \
               equals_almost(self.z, other.z, places=places)

    def __eq__(self, other: Any) -> bool:
        """
        Equal operator.

        Args:
            other: point as args accepted by Vector()
        """
        x, y, z = self.decompose(other)
        return is_close(self._x, x) and is_close(self._y, y) and is_close(self._z, z)

    def __lt__(self, other: Any) -> bool:
        """
        Lower than operator.

        Args:
            other: point as args accepted by Vector()

        """
        x, y, z = self.decompose(other)
        if self._x == x:
            if self._y == y:
                return self._z < z
            else:
                return self._y < y
        else:
            return self._x < x

    def __add__(self, other: Any) -> 'Vector':
        """
        Add operator: `self` + `other`

        Args:
            other: point as args accepted by Vector()

        """
        if isinstance(other, (float, int)):
            scalar = float(other)
            return Vector(self._x + scalar, self._y + scalar, self._z + scalar)
        else:
            x, y, z = self.decompose(other)
            return Vector(self._x + x, self._y + y, self._z + z)

    def __radd__(self, other: Any) -> 'Vector':
        """
        RAdd operator: `other` + `self`

        Args:
            other: point as args accepted by Vector()

        """
        return self.__add__(other)

    def __sub__(self, other: Any) -> 'Vector':
        """
        Sub operator: `self` - `other`

        Args:
            other: point as args accepted by Vector()

        """
        if isinstance(other, (float, int)):
            scalar = float(other)
            return Vector(self._x - scalar, self._y - scalar, self._z - scalar)
        else:
            x, y, z = self.decompose(other)
            return Vector(self._x - x, self._y - y, self._z - z)

    def __rsub__(self, other: Any) -> 'Vector':
        """
        RSub operator: `other` - `self`

        Args:
            other: point as args accepted by Vector()

        """
        if isinstance(other, (float, int)):
            scalar = float(other)
            return Vector(scalar - self._x, scalar - self._y - scalar, scalar - self._z)
        else:
            x, y, z = self.decompose(other)
            return Vector(x - self._x, y - self._y, z - self._z)

    def __mul__(self, other: float) -> 'Vector':
        """
        Mul operator: `self` * `other`

        Args:
            other: scale factor
        """
        scalar = float(other)
        return Vector(self._x * scalar, self._y * scalar, self._z * scalar)

    def __rmul__(self, other: float) -> 'Vector':
        """
        RMul operator: `other` * `self`

        Args:
            other: scale factor
        """
        return self.__mul__(other)

    def __truediv__(self, other: float) -> 'Vector':
        """
        Div operator: `self` / `other`

        Args:
            other: scale factor
        """
        scalar = float(other)
        return Vector(self._x / scalar, self._y / scalar, self._z / scalar)

    __div__ = __truediv__

    def __rtruediv__(self, other: float) -> 'Vector':
        """
        RDiv operator: `other` / `self`

        Args:
            other: scale factor
        """
        scalar = float(other)
        return Vector(scalar / self._x, scalar / self._y, scalar / self._z)

    __rdiv__ = __rtruediv__

    def dot(self, other: Any) -> float:
        """
        Dot operator: `self` . `other`

        Args:
            other: vector as args accepted by Vector()
        """
        x, y, z = self.decompose(other)
        return self._x * x + self._y * y + self._z * z

    def cross(self, other: Any) -> 'Vector':
        """
        Dot operator: `self` x `other`

        Args:
            other: vector as args accepted by Vector()
        """
        x, y, z = self.decompose(other)
        return Vector(self._y * z - self._z * y, self._z * x - self._x * z, self._x * y - self._y * x)

    def distance(self, other: Any) -> float:
        v = Vector(other)
        return v.__sub__(self).magnitude

    def angle_between(self, other: Any) -> float:
        """
        Calculate angle between `self` and `other` in radians. +angle is counter clockwise orientation.

        Args:
            other: vector as args accepted by Vector()

        """
        v1 = self.normalize()
        v2 = Vector(other).normalize()
        return math.acos(v1.dot(v2))

    def rot_z_rad(self, angle: float) -> 'Vector':
        """
        Rotate vector around z axis.

        Args:
            angle: angle in radians

        Returns: rotated vector

        """
        v = Vector(self.x, self.y, 0.)
        v = Vector.from_rad_angle(v.angle_rad + angle, v.magnitude)
        return Vector(v.x, v.y, self.z)

    def rot_z_deg(self, angle: float) -> 'Vector':
        """
        Rotate vector around z axis.

        Args:
            angle: angle in degrees

        Returns: rotated vector

        """
        return self.rot_z_rad(math.radians(angle))


X_AXIS = Vector(1, 0, 0)
Y_AXIS = Vector(0, 1, 0)
Z_AXIS = Vector(0, 0, 1)
NULLVEC = Vector(0, 0, 0)


def distance(p1: Any, p2: Any) -> float:
    """
    Calc distance between two points

    Args:
        p1: first point as args accepted by Vector()
        p2: second point as args accepted by Vector()

    """
    return Vector(p1).distance(p2)


def lerp(p1: Any, p2: Any, factor: float = 0.5) -> 'Vector':
    """
    Linear interpolation between `p1` and `p2`.

    Args:
        p1: first point as args accepted by Vector()
        p2: second point as args accepted by Vector()
        factor:  interpolation factor (0=p1, 1=p2, 0.5=mid point)

    Returns: interpolated vector

    """
    return Vector(p1).lerp(p2, factor)
