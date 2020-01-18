# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List
from functools import partial
import math
from operator import le, ge, lt, gt
from abc import abstractmethod

from .vector import Vector

if TYPE_CHECKING:
    from ezdxf.eztypes import BoundingBox2d, Vertex

HALF_PI = math.pi / 2.  # type: float
THREE_PI_HALF = 1.5 * math.pi  # type: float
DOUBLE_PI = math.pi * 2.  # type: float


def is_close_points(p1: 'Vertex', p2: 'Vertex', abs_tol=1e-12) -> bool:
    """
    Returns ``True`` if `p1` is very close to `p2`.

    Args:
        p1: first vertex as :class:`Vector` compatible object
        p2: second vertex as :class:`Vector` compatible object
        abs_tol: absolute tolerance

    Raises:
        TypeError: for incompatible vertices

    """
    if len(p1) != len(p2):
        raise TypeError('incompatible points')

    for v1, v2 in zip(p1, p2):
        if not math.isclose(v1, v2, abs_tol=abs_tol):
            return False
    return True


def closest_point(base: 'Vertex', points: Iterable['Vertex']) -> 'Vector':
    """
    Returns closest point to `base`.

    Args:
        base: base point as :class:`Vector` compatible object
        points: iterable of points as :class:`Vector` compatible object


    """
    base = Vector(base)
    min_dist = None
    found = None
    for point in points:
        p = Vector(point)
        dist = (base - p).magnitude
        if (min_dist is None) or (dist < min_dist):
            min_dist = dist
            found = p
    return found


def convex_hull(points: Iterable['Vertex']) -> List['Vertex']:
    """ Returns 2D convex hull for `points`.

    Args:
        points: iterable of points as :class:`Vector` compatible objects, z-axis is ignored

    """

    def _convexhull(hull):
        while len(hull) > 2:
            start_point, check_point, destination_point = hull[-3:]  # the last three points
            if not left_of_line(check_point, start_point, destination_point):  # curve not turns right
                del hull[-2]  # remove the penultimate point
            else:
                break
        return hull

    points = sorted(set(points))  # remove duplicate points

    if len(points) < 3:
        raise ValueError("Convex hull calculation requires 3 or more unique points.")

    upper_hull = points[:2]  # first two points
    for next_point in points[2:]:
        upper_hull.append(next_point)
        upper_hull = _convexhull(upper_hull)
    lower_hull = [points[-1], points[-2]]  # last two points

    for next_point in reversed(points[:-2]):
        lower_hull.append(next_point)
        lower_hull = _convexhull(lower_hull)
    upper_hull.extend(lower_hull[1:-1])
    return upper_hull


def normalize_angle(angle: float) -> float:
    """
    Returns normalized angle between ``0`` and ``2*pi``.

    """
    angle = math.fmod(angle, DOUBLE_PI)
    if angle < 0:
        angle += DOUBLE_PI
    return angle


def enclosing_angles(angle, start_angle, end_angle, ccw=True, abs_tol=1e-9):
    isclose = partial(math.isclose, abs_tol=abs_tol)

    s = normalize_angle(start_angle)
    e = normalize_angle(end_angle)
    a = normalize_angle(angle)
    if isclose(s, e):
        return isclose(s, a)

    if s < e:
        r = s < a < e
    else:
        r = not (e < a < s)
    return r if ccw else not r


def left_of_line(point: 'Vertex', p1: 'Vertex', p2: 'Vertex', online=False) -> bool:
    """
    Returns ``True`` if `point` is "left of line" (`p1`, `p2`).
    A `point` on the line is also "left of line", if `online` is ``True``.

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
