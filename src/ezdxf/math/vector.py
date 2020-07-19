# Purpose: General purpose 2d/3d Vector() class and special 2d vector Vec2() class for more speed.
# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
from typing import Tuple, List, Iterable, Any, Union, Sequence, TYPE_CHECKING
from functools import partial
import math
import random

if TYPE_CHECKING:
    from ezdxf.eztypes import VecXY, Vertex

isclose = partial(math.isclose, abs_tol=1e-12)


class Vector:
    """
    This is an immutable universal 3D vector object. This class is optimized for universality not for speed.
    Immutable means you can't change (x, y, z) components after initialization::

        v1 = Vector(1, 2, 3)
        v2 = v1
        v2.z = 7  # this is not possible, raises AttributeError
        v2 = Vector(v2.x, v2.y, 7)  # this creates a new Vector() object
        assert v1.z == 3  # and v1 remains unchanged


    :class:`Vector` initialization:

        - ``Vector()``, returns ``Vector(0, 0, 0)``
        - ``Vector((x, y))``, returns ``Vector(x, y, 0)``
        - ``Vector((x, y, z))``, returns ``Vector(x, y, z)``
        - ``Vector(x, y)``, returns ``Vector(x, y, 0)``
        - ``Vector(x, y, z)``, returns  ``Vector(x, y, z)``

    Addition, subtraction, scalar multiplication and scalar division left and right handed are supported::

        v = Vector(1, 2, 3)
        v + (1, 2, 3) == Vector(2, 4, 6)
        (1, 2, 3) + v == Vector(2, 4, 6)
        v - (1, 2, 3) == Vector(0, 0, 0)
        (1, 2, 3) - v == Vector(0, 0, 0)
        v * 3 == Vector(3, 6, 9)
        3 * v == Vector(3, 6, 9)
        Vector(3, 6, 9) / 3 == Vector(1, 2, 3)
        -Vector(1, 2, 3) == (-1, -2, -3)

    Comparison between vectors and vectors or tuples is supported::

        Vector(1, 2, 3) < Vector (2, 2, 2)
        (1, 2, 3) < tuple(Vector(2, 2, 2))  # conversion necessary
        Vector(1, 2, 3) == (1, 2, 3)

        bool(Vector(1, 2, 3)) is True
        bool(Vector(0, 0, 0)) is False

    """
    __slots__ = ['_x', '_y', '_z']

    def __init__(self, *args):
        self._x, self._y, self._z = self.decompose(*args)

    @property
    def x(self) -> float:
        """ x-axis value """
        return self._x

    @property
    def y(self) -> float:
        """ y-axis value """
        return self._y

    @property
    def z(self) -> float:
        """ z-axis value """
        return self._z

    @property
    def xy(self) -> 'Vector':
        """ Vector as ``(x, y, 0)``, projected on the xy-plane. """
        return self.__class__(self._x, self._y)

    @property
    def xyz(self) -> Tuple[float, float, float]:
        """ Vector as ``(x, y, z)`` tuple. """
        return self._x, self._y, self._z

    @property
    def vec2(self) -> 'Vec2':
        """ Real 2D vector as :class:`Vec2` object. """
        return Vec2((self._x, self._y))

    def replace(self, x: float = None, y: float = None, z: float = None) -> 'Vector':
        """ Returns a copy of vector with replaced x-, y- and/or z-axis. """
        if x is None:
            x = self._x
        if y is None:
            y = self._y
        if z is None:
            z = self._z
        return self.__class__(x, y, z)

    def round(self, ndigits=None) -> 'Vector':
        """
        Returns a new vector where all components are rounded to `ndigits`.

        Uses standard Python :func:`round` function for rounding.
        """
        return self.__class__(
            round(self._x, ndigits),
            round(self._y, ndigits),
            round(self._z, ndigits),
        )

    @classmethod
    def list(cls, items: Iterable['Vertex']) -> List['Vector']:
        """ Returns a list of :class:`Vector` objects. """
        return list(cls.generate(items))

    @classmethod
    def tuple(cls, items: Iterable['Vertex']) -> Sequence['Vector']:
        """ Returns a tuple of :class:`Vector` objects. """
        return tuple(cls.generate(items))

    @classmethod
    def generate(cls, items: Iterable['Vertex']) -> Iterable['Vector']:
        """ Returns an iterable of :class:`Vector` objects. """
        return (cls(item) for item in items)

    @classmethod
    def from_angle(cls, angle: float, length: float = 1.) -> 'Vector':
        """ Returns a :class:`Vector` object from `angle` in radians in the xy-plane, z-axis = ``0``. """
        return cls(math.cos(angle) * length, math.sin(angle) * length, 0.)

    @classmethod
    def from_deg_angle(cls, angle: float, length: float = 1.) -> 'Vector':
        """ Returns a :class:`Vector` object from `angle` in degrees in the xy-plane, z-axis = ``0``. """
        return cls.from_angle(math.radians(angle), length)

    @staticmethod  # allows overriding by inheritance
    def decompose(*args) -> Tuple[float, float, float]:
        """
        Converts input into a (x, y, z) tuple.

        Valid arguments are:

            - no args: ``decompose()`` returns (0, 0, 0)
            - 1 arg: ``decompose(arg)``, `arg` is tuple or list, tuple has to be (x, y[, z]): ``decompose((x, y))`` returns (x, y, 0.)
            - 2 args: ``decompose(x, y)`` returns (x, y, 0)
            - 3 args: ``decompose(x, y, z)`` returns (x, y, z)

        Returns:
            (x, y, z) tuple

        (internal API)

        """
        length = len(args)
        if length == 0:
            return 0., 0., 0.
        elif length == 1:
            data = args[0]
            if isinstance(data, Vector):
                return data._x, data._y, data._z
            else:
                try:
                    x, y, *z = data
                except TypeError:
                    raise ValueError('invalid arguments {}'.format(str(args)))
                else:
                    if len(z):
                        z = z[0]
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

    @classmethod
    def random(cls, length: float = 1) -> 'Vector':
        """ Returns a random vector. """
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        z = random.uniform(-1, 1)
        return Vector(x, y, z).normalize(length)

    def __str__(self) -> str:
        """ Return ``'(x, y, z)'`` as string. """
        return '({0.x}, {0.y}, {0.z})'.format(self)

    def __repr__(self) -> str:
        """ Return ``'Vector(x, y, z)'`` as string. """
        return 'Vector' + self.__str__()

    def __len__(self) -> int:
        """ Returns always ``3``. """
        return 3

    def __hash__(self) -> int:
        """ Returns hash value of vector, enables the usage of vector as key in ``set`` and ``dict``. """
        return hash(self.xyz)

    def copy(self) -> 'Vector':
        """ Returns a copy of vector as :class:`Vector` object. """
        return self.__class__(self._x, self._y, self._z)

    __copy__ = copy

    def __deepcopy__(self, memodict: dict) -> 'Vector':
        """ :func:`copy.deepcopy` support. """
        try:
            return memodict[id(self)]
        except KeyError:
            v = self.copy()
            memodict[id(self)] = v
            return v

    def __getitem__(self, index: int) -> float:
        """
        Support for indexing:

            - v[0] is v.x
            - v[1] is v.y
            - v[2] is v.z

        """
        return self.xyz[index]

    def __iter__(self) -> Iterable[float]:
        """ Returns iterable of x-, y- and z-axis. """
        yield self._x
        yield self._y
        yield self._z

    def __abs__(self) -> float:
        """ Returns length (magnitude) of vector. """
        return self.magnitude

    @property
    def magnitude(self) -> float:
        """ Length of vector. """
        return self.magnitude_square ** .5

    @property
    def magnitude_xy(self) -> float:
        """ Length of vector in the xy-plane. """
        return math.hypot(self._x, self._y)

    @property
    def magnitude_square(self) -> float:
        """ Square length of vector. """
        x, y, z = self._x, self._y, self._z
        return x * x + y * y + z * z

    @property
    def is_null(self) -> bool:
        """ ``True`` for ``Vector(0, 0, 0)``. """
        return self.__eq__((0, 0, 0))

    def is_parallel(self, other: 'Vector', abs_tol: float = 1e-12) -> bool:
        """ Returns ``True`` if `self` and `other` are parallel to vectors. """
        v1 = self.normalize()
        v2 = other.normalize()
        return v1.isclose(v2, abs_tol=abs_tol) or v1.isclose(-v2, abs_tol=abs_tol)

    @property
    def spatial_angle(self) -> float:
        """ Spatial angle between vector and x-axis in radians.  """
        return math.acos(X_AXIS.dot(self.normalize()))

    @property
    def spatial_angle_deg(self) -> float:
        """ Spatial angle between vector and x-axis in degrees. """
        return math.degrees(self.spatial_angle)

    @property
    def angle(self) -> float:
        """ Angle between vector and x-axis in the xy-plane in radians. """
        return math.atan2(self._y, self._x)

    @property
    def angle_deg(self) -> float:
        """ Returns angle of vector and x-axis in the xy-plane in degrees. """
        return math.degrees(self.angle)

    def orthogonal(self, ccw: bool = True) -> 'Vector':
        """
        Returns orthogonal 2D vector, z-axis is unchanged.

        Args:
            ccw: counter clockwise if ``True`` else clockwise

        """
        return self.__class__(-self._y, self._x, self._z) if ccw else self.__class__(self._y, -self._x, self._z)

    def lerp(self, other: Any, factor=.5) -> 'Vector':
        """
        Returns linear interpolation between `self` and `other`.
        
        Args:
            other: end point as :class:`Vector` compatible object
            factor: interpolation factor (``0`` = self, ``1`` = other, ``0.5`` = mid point)

        """
        d = (self.__class__(other) - self) * float(factor)
        return self.__add__(d)

    def project(self, other: Any) -> 'Vector':
        """ Returns projected vector of `other` onto `self`. """
        uv = self.normalize()
        return uv * uv.dot(other)

    def normalize(self, length: float = 1.) -> 'Vector':
        """ Returns normalized vector, optional scaled by `length`. """
        return self.__mul__(length / self.magnitude)

    def reversed(self) -> 'Vector':
        """ Returns negated vector (-`self`). """
        return self.__mul__(-1.)

    __neg__ = reversed

    def __bool__(self) -> bool:
        """ Returns ``True`` if vector is not ``(0, 0, 0)``. """
        return not self.is_null

    def isclose(self, other: Any, abs_tol: float = 1e-12) -> bool:
        """ Returns ``True`` if `self` is close to `other`. Uses :func:`math.isclose` to compare all axis. """
        x, y, z = self.decompose(other)
        return math.isclose(self._x, x, abs_tol=abs_tol) and \
               math.isclose(self._y, y, abs_tol=abs_tol) and \
               math.isclose(self._z, z, abs_tol=abs_tol)

    def __eq__(self, other: Any) -> bool:
        """
        Equal operator.

        Args:
            other: :class:`Vector` compatible object
        """
        x, y, z = self.decompose(other)
        return isclose(self._x, x) and isclose(self._y, y) and isclose(self._z, z)

    def __lt__(self, other: Any) -> bool:
        """
        Lower than operator.

        Args:
            other: :class:`Vector` compatible object

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
            other: :class:`Vector` compatible object

        """
        if isinstance(other, (float, int)):
            scalar = float(other)
            return self.__class__(self._x + scalar, self._y + scalar, self._z + scalar)
        else:
            x, y, z = self.decompose(other)
            return self.__class__(self._x + x, self._y + y, self._z + z)

    def __radd__(self, other: Any) -> 'Vector':
        """
        RAdd operator: `other` + `self`

        Args:
            other: :class:`Vector` compatible object

        """
        return self.__add__(other)

    def __sub__(self, other: Any) -> 'Vector':
        """
        Sub operator: `self` - `other`

        Args:
            other: :class:`Vector` compatible object

        """
        if isinstance(other, (float, int)):
            scalar = float(other)
            return self.__class__(self._x - scalar, self._y - scalar, self._z - scalar)
        else:
            x, y, z = self.decompose(other)
            return self.__class__(self._x - x, self._y - y, self._z - z)

    def __rsub__(self, other: Any) -> 'Vector':
        """
        RSub operator: `other` - `self`

        Args:
            other: :class:`Vector` compatible object

        """
        if isinstance(other, (float, int)):
            scalar = float(other)
            return self.__class__(scalar - self._x, scalar - self._y, scalar - self._z)
        else:
            x, y, z = self.decompose(other)
            return self.__class__(x - self._x, y - self._y, z - self._z)

    def __mul__(self, other: float) -> 'Vector':
        """
        Mul operator: `self` * `other`

        Args:
            other: scale factor
        """
        scalar = float(other)
        return self.__class__(self._x * scalar, self._y * scalar, self._z * scalar)

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
        return self.__class__(self._x / scalar, self._y / scalar, self._z / scalar)

    __div__ = __truediv__

    def __rtruediv__(self, other: float) -> 'Vector':
        """
        RDiv operator: `other` / `self`

        Args:
            other: scale factor
        """
        scalar = float(other)
        return self.__class__(scalar / self._x, scalar / self._y, scalar / self._z)

    __rdiv__ = __rtruediv__

    def dot(self, other: Any) -> float:
        """
        Dot operator: `self` . `other`

        Args:
            other: :class:`Vector` compatible object
        """
        x, y, z = self.decompose(other)
        return self._x * x + self._y * y + self._z * z

    def cross(self, other: Any) -> 'Vector':
        """
        Dot operator: `self` x `other`

        Args:
            other: :class:`Vector` compatible object
        """
        x, y, z = self.decompose(other)
        return self.__class__(self._y * z - self._z * y, self._z * x - self._x * z, self._x * y - self._y * x)

    def distance(self, other: Any) -> float:
        """ Returns distance between `self` and `other` vector. """
        v = self.__class__(other)
        return v.__sub__(self).magnitude

    def angle_between(self, other: Any) -> float:
        """
        Returns angle between `self` and `other` in radians. +angle is counter clockwise orientation.

        Args:
            other: :class:`Vector` compatible object

        """
        v2 = self.__class__(other)
        cos_theta = self.dot(v2) / (self.magnitude * v2.magnitude)
        abs_cos_theta = math.fabs(cos_theta)
        if abs_cos_theta > 1.0:
            if abs_cos_theta - 1.0 < 1e-5:
                cos_theta = math.modf(cos_theta)[1]
            else:
                raise ValueError(f'domain error: {cos_theta}')
        return math.acos(cos_theta)

    def angle_about(self, base: 'Vector', target: 'Vector') -> float:
        # (c) 2020 by Matt Broadway, MIT License
        """
        Returns counter clockwise angle in radians about `self` from `base` to `target` when projected
        onto the plane defined by `self` as the normal vector.

        Args:
            base: base vector, defines angle 0
            target: target vector
        """
        x_axis = (base - self.project(base)).normalize()
        y_axis = self.cross(x_axis).normalize()
        target_projected_x = x_axis.dot(target)
        target_projected_y = y_axis.dot(target)
        return math.atan2(target_projected_y, target_projected_x) % math.tau

    def rotate(self, angle: float) -> 'Vector':
        """
        Returns vector rotated about `angle` around the z-axis.

        Args:
            angle: angle in radians

        """
        v = self.__class__(self.x, self.y, 0.)
        v = Vector.from_angle(v.angle + angle, v.magnitude)
        return self.__class__(v.x, v.y, self.z)

    def rotate_deg(self, angle: float) -> 'Vector':
        """
        Returns vector rotated about `angle` around the z-axis.

        Args:
            angle: angle in degrees

        """
        return self.rotate(math.radians(angle))


X_AXIS = Vector(1, 0, 0)
Y_AXIS = Vector(0, 1, 0)
Z_AXIS = Vector(0, 0, 1)
NULLVEC = Vector(0, 0, 0)


def distance(p1: Any, p2: Any) -> float:
    """
    Returns distance between points `p1` and `p2`.

    Args:
        p1: first point as :class:`Vector` compatible object
        p2: second point as :class:`Vector` compatible object

    """
    return Vector(p1).distance(p2)


def lerp(p1: Any, p2: Any, factor: float = 0.5) -> 'Vector':
    """
    Returns linear interpolation between points `p1` and `p2` as :class:`Vector`.

    Args:
        p1: first point as :class:`Vector` compatible object
        p2: second point as :class:`Vector` compatible object
        factor:  interpolation factor (``0`` = `p1`, ``1`` = `p2`, ``0.5`` = mid point)

    """
    return Vector(p1).lerp(p2, factor)


TVec2 = Union["VecXY", Sequence[float]]


class Vec2:
    """
    :class:`Vec2` represents a special 2D vector ``(x, y)``. The :class:`Vec2` class is optimized for speed and not
    immutable, :meth:`iadd`, :meth:`isub`, :meth:`imul` and :meth:`idiv` modifies the vector itself, the
    :class:`Vector` class returns a new object.

    :class:`Vec2` initialization accepts float-tuples ``(x, y[, z])``, two floats or any object providing
    :attr:`x` and :attr:`y` attributes like :class:`Vec2` and :class:`Vector` objects.

    Args:
        v: vector object with :attr:`x` and :attr:`y` attributes/properties or a sequence of float ``[x, y, ...]`` or
           x-axis as float if argument `y` is not ``None``
        y: second float for :code:`Vec2(x, y)`

    :class:`Vec2` implements a subset of :class:`Vector`.

    """
    __slots__ = ['x', 'y']

    def __init__(self, v: Any, y: float = None):
        try:  # fast path for Vec2() and Vector() or any object providing x and y attributes
            self.x = v.x
            self.y = v.y
        except AttributeError:
            if y is None:  # given one tuple
                self.x = float(v[0])
                self.y = float(v[1])
            else:  # two floats given
                self.x = float(v)
                self.y = float(y)

    @property
    def vec3(self) -> 'Vector':
        """
        Returns a 3D vector.

        """
        return Vector(self.x, self.y, 0)

    def round(self, ndigits=None) -> 'Vec2':
        """
        Returns a new vector where all components are rounded to `ndigits`.

        Uses standard Python :func:`round` function for rounding.
        """
        return self.__class__((round(self.x, ndigits), round(self.y, ndigits)))

    @classmethod
    def list(cls, items: Iterable[TVec2]) -> List['Vec2']:
        return list(cls.generate(items))

    @classmethod
    def tuple(cls, items: Iterable['Vertex']) -> Sequence['Vec2']:
        """ Returns a tuple of :class:`Vector` objects. """
        return tuple(cls.generate(items))

    @classmethod
    def generate(cls, items: Iterable[TVec2]) -> Iterable['Vec2']:
        return (cls(item) for item in items)

    @classmethod
    def from_angle(cls, angle: float, length: float = 1.) -> 'Vec2':
        return cls(math.cos(angle) * length, math.sin(angle) * length)

    @classmethod
    def from_deg_angle(cls, angle: float, length: float = 1.) -> 'Vec2':
        return cls.from_angle(math.radians(angle), length)

    def __str__(self) -> str:
        return '({0.x}, {0.y})'.format(self)

    def __repr__(self) -> str:
        return 'Vec2' + self.__str__()

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
        Returns length of vector.

        """
        return math.hypot(self.x, self.y)

    @property
    def is_null(self) -> bool:
        return isclose(self.x, 0.) and isclose(self.y, 0.)

    @property
    def angle(self) -> float:
        """
        Angle of vector in radians.

        """
        return math.atan2(self.y, self.x)

    @property
    def angle_deg(self) -> float:
        """
        Angle of vector in degrees.

        """
        return math.degrees(self.angle)

    def orthogonal(self, ccw: bool = True) -> 'Vec2':
        """
        Orthogonal vector

        Args:
            ccw: counter clockwise if ``True`` else clockwise

        """
        if ccw:
            return self.__class__((-self.y, self.x))
        else:
            return self.__class__((self.y, -self.x))

    def lerp(self, other: 'VecXY', factor: float = .5) -> 'Vec2':
        """
        Linear interpolation between `self` and `other`.

        Args:
            other: target vector/point
            factor: interpolation factor (0=self, 1=other, 0.5=mid point)

        Returns: interpolated vector

        """
        x = self.x + (other.x - self.x) * factor
        y = self.y + (other.y - self.y) * factor
        return self.__class__((x, y))

    def project(self, other: 'VecXY') -> 'Vec2':
        """
        Project vector `other` onto `self`.

        """
        uv = self.normalize()
        return uv * uv.dot(other)

    def normalize(self, length: float = 1.) -> 'Vec2':
        return self.__mul__(length / self.magnitude)

    def reversed(self) -> 'Vec2':
        return self.__class__((-self.x, -self.y))

    __neg__ = reversed

    def __bool__(self) -> bool:
        return not self.is_null

    def isclose(self, other: 'VecXY', abs_tol: float = 1e-12) -> bool:
        return math.isclose(self.x, other.x, abs_tol=abs_tol) and math.isclose(self.y, other.y, abs_tol=abs_tol)

    def __eq__(self, other: 'Vertex') -> bool:
        # accepts also tuples, for more convenience at testing
        x, y, *_ = other
        return isclose(self.x, x) and isclose(self.y, y)

    def __lt__(self, other: 'Vertex') -> bool:
        # accepts also tuples, for more convenience at testing
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

    def det(self, other: 'VecXY') -> float:
        return self.x * other.y - self.y * other.x

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
        return self.__class__.from_angle(self.angle + angle, self.magnitude)

    def rotate_deg(self, angle: float) -> 'Vec2':
        """
        Rotate vector around origin.

        Args:
            angle: angle in degrees

        Returns: rotated vector

        """
        return self.__class__.from_angle(self.angle + math.radians(angle), self.magnitude)
