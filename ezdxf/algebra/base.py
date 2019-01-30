# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple
import math
from functools import partial
from operator import le, ge, lt, gt

if TYPE_CHECKING:
    from eztypes import Vertex

HALF_PI = math.pi / 2.  # type: float
THREE_PI_HALF = 1.5 * math.pi  # type: float
DOUBLE_PI = math.pi * 2.  # type: float

is_close = partial(math.isclose, abs_tol=1e-9)


def is_close_points(p1: 'Vertex', p2: 'Vertex') -> bool:
    """
    Returns true if `p1` is very close to `p2`.

    Args:
        p1: vertex 1
        p2: vertex 2

    """
    if len(p1) == 2:
        p1 = p1[0], p1[1], 0.
    if len(p2) == 2:
        p2 = p2[0], p2[1], 0.

    for v1, v2 in zip(p1, p2):
        if not is_close(v1, v2):
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


def equals_almost(v1: float, v2: float, places: int = 7) -> bool:
    """
    True if `v1` is close to `v2`, similar to `is_close`, but uses rounding.

    Args:
        v1: first value
        v2: second value
        places: rounding precision

    """
    return round(v1, places) == round(v2, places)


def almost_equal_points(p1: 'Vertex', p2: 'Vertex', places: int = 7) -> bool:
    """
    Returns true if `p1` is very close to `p2`, similar to `is_close_points` but uses rounding.

    Args:
        p1: vertex 1
        p2: vertex 2
        places: rounding precision

    """
    if len(p1) == 2:
        p1 = p1[0], p1[1], 0.
    if len(p2) == 2:
        p2 = p2[0], p2[1], 0.

    for v1, v2 in zip(p1, p2):
        if not equals_almost(v1, v2, places=places):
            return False
    return True


def normalize_angle(angle: float) -> float:
    """
    Returns normalized angle between 0 and 2*pi.
    """
    angle = math.fmod(angle, DOUBLE_PI)
    if angle < 0:
        angle += DOUBLE_PI
    return angle


def is_vertical_angle(angle: float, places: int = 7) -> bool:
    """
    Returns True for 1/2pi and 3/2pi.
    """
    angle = normalize_angle(angle)
    return equals_almost(angle, HALF_PI, places) or equals_almost(angle, THREE_PI_HALF, places)


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


def xround(value: float, rounding: float = 0.) -> float:
    """
    Extended rounding.

    `rounding` defines the rounding limit:
        - 0 = remove fraction
        - 0.1 = round next to x.1, x.2, ... x.0
        - 0.25 = round next to x.25, x.50, x.75 or x.00
        - 0.5 = round next to x.5 or x.0
        - 1. = round to a multiple of 1: remove fraction
        - 2. = round to a multiple of 2: xxx2, xxx4, xxx6 ...
        - 5. = round to a multiple of 5: xxx5 or xxx0
        - 10. = round to a multiple of 10: xx10, xx20, ...

    Args:
        value: float value to round
        rounding: rounding limit

    """
    if rounding == 0:
        return round(value)
    factor = 1. / rounding
    return round(value * factor) / factor
