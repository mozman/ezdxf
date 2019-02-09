# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple, Iterable
import math
from operator import le, ge, lt, gt
from abc import abstractmethod
from .vec2 import Vec2

if TYPE_CHECKING:
    from ezdxf.eztypes import BoundingBox2d, Vertex

HALF_PI = math.pi / 2.  # type: float
THREE_PI_HALF = 1.5 * math.pi  # type: float
DOUBLE_PI = math.pi * 2.  # type: float


def is_close_points(p1: 'Vertex', p2: 'Vertex', abs_tol=1e-12) -> bool:
    """
    Returns true if `p1` is very close to `p2`.

    Args:
        p1: vertex 1
        p2: vertex 2
        abs_tol: absolute tolerance
    """
    if len(p1) != len(p2):
        raise TypeError('incompatible points')

    for v1, v2 in zip(p1, p2):
        if not math.isclose(v1, v2, abs_tol=abs_tol):
            return False
    return True


def rotate_2d(point: 'Vertex', angle: float) -> Tuple[float, float]:
    """
    Rotate `point` in the XY-plane around the z-axis about `angle`.

    Args:
         point: Vertex
         angle: rotation angle in radians
    Returns:
        x, y - tuple

    """
    x = point[0] * math.cos(angle) - point[1] * math.sin(angle)
    y = point[1] * math.cos(angle) + point[0] * math.sin(angle)
    return x, y


def normalize_angle(angle: float) -> float:
    """
    Returns normalized angle between 0 and 2*pi.
    """
    angle = math.fmod(angle, DOUBLE_PI)
    if angle < 0:
        angle += DOUBLE_PI
    return angle


def is_vertical_angle(angle: float, abs_tol=1e-12) -> bool:
    """
    Returns True for 1/2pi and 3/2pi.
    """
    angle = normalize_angle(angle)
    return math.isclose(angle, HALF_PI, abs_tol=abs_tol) or math.isclose(angle, THREE_PI_HALF, abs_tol=abs_tol)


def get_angle(p1: 'Vertex', p2: 'Vertex') -> float:
    """
    Returns angle in radians between the line (p1, p2) and x-axis.

    Args:
        p1: start point
        p2: end point

    Returns:
        angle in radians

    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.atan2(dy, dx)


def left_of_line(point: 'Vertex', p1: 'Vertex', p2: 'Vertex', online=False) -> bool:
    """
    True if `point` is "left of line" (`p1`, `p2`). Point on the line is "left of line" if `online` is True.

    """

    px, py, *_ = point
    p1x, p1y, *_ = p1
    p2x, p2y, *_ = p2

    if online:
        lower, greater = le, ge  # lower/greater or equal
    else:
        lower, greater = lt, gt  # real lower/greater then

    # check if p1 and p2 are on the same vertical line
    if math.isclose(p1x, p2x):
        # compute on which side of the line point should be
        should_be_left = p1y < p2y
        return lower(px, p1x) if should_be_left else greater(px, p1y)
    else:
        # get pitch of line
        pitch = (p2y - p1y) / (p2x - p1x)
        # get y-value at points's x-position
        y = pitch * (px - p1x) + p1y
        # compute if point should be above or below the line
        should_be_above = p1x < p2x
        return greater(py, y) if should_be_above else lower(py, y)


class ConstructionTool:
    """
    Abstract base class for all 2D construction classes.

    """

    @property
    @abstractmethod
    def bounding_box(self) -> 'BoundingBox2d':
        pass

    @abstractmethod
    def move(self, dx: float, dy: float) -> None:
        pass

    @abstractmethod
    def rotate(self, angle: float) -> None:
        pass

    @abstractmethod
    def scale(self, sx: float, sy: float) -> None:
        pass


def move(vectors: Iterable['Vec2'], dx: float, dy: float) -> Iterable[Vec2]:
    """
    Move `vectors` along translation vector `v`.

    Args:
        vectors: iterable of Vec2
        dx: translation in x-axis
        dy: translation in y-axis

    Returns: iterable of Vec2

    """
    v = Vec2((dx, dy))
    return (v + vector for vector in vectors)


def rotate(vectors: Iterable['Vec2'], angle: float) -> Iterable[Vec2]:
    """
    Rotate `vectors` around the origin (0, 0) about `angle`.

    Args:
        vectors: iterable of 2d vectors
        angle: rotation angle in radians

    Returns: iterable of Vec2

    """
    return (vector.rotate(angle) for vector in vectors)


def scale(vectors: Iterable['Vec2'], sx: float, sy: float) -> Iterable[Vec2]:
    """
    Scale `vectors` about `sx` and `sy` factors.
    Args:
        vectors: iterable of Vec2
        sx: x-axis scale factor
        sy: y-axis scale factor

    Returns: iterable of Vec2

    """
    return (Vec2((vector.x * sx, vector.y * sy)) for vector in vectors)
