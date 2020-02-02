# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence

from functools import partial
import math
from abc import abstractmethod

from .vector import Vector, Vec2
from .bbox import BoundingBox2d

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

HALF_PI = math.pi / 2.  # type: float
THREE_PI_HALF = 1.5 * math.pi  # type: float
DOUBLE_PI = math.pi * 2.  # type: float
TOLERANCE = 1e-12


def is_close_points(p1: 'Vertex', p2: 'Vertex', abs_tol=TOLERANCE) -> bool:
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


def enclosing_angles(angle, start_angle, end_angle, ccw=True, abs_tol=TOLERANCE):
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


def left_of_line(point: 'Vertex', p1: 'Vertex', p2: 'Vertex', colinear=False) -> bool:
    """
    Returns ``True`` if `point` is "left of line" (`p1`, `p2`).
    If `colinear` is ``True``, a colinear point is also left of the line.

    """
    cx, cy, *_ = point
    ax, ay, *_ = p1
    bx, by, *_ = p2
    det = ((bx - ax) * (cy - ay) - (by - ay) * (cx - ax))
    if colinear and math.isclose(det, 0, abs_tol=TOLERANCE):
        return True
    else:
        return det > 0


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


def intersection_line_line(
        line1: Sequence[Vec2],
        line2: Sequence[Vec2],
        virtual=True,
        abs_tol=TOLERANCE) -> Optional[Vec2]:
    """
    Compute the intersection of two lines in the xy-plane.

    Args:
        line1: start- and end point of first line to test e.g. ((x1, y1), (x2, y2)).
        line2: start- and end point of second line to test e.g. ((x3, y3), (x4, y4)).
        virtual: ``True`` returns any intersection point, ``False`` returns only real intersection points.
        abs_tol: tolerance for intersection test.

    Returns:
        ``None`` if there is no intersection point (parallel lines) or intersection point as :class:`Vec2`

    """
    # Sources:
    # compas: https://github.com/compas-dev/compas/blob/master/src/compas/geometry/_core/intersections.py (MIT)
    # wikipedia: https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection

    a, b = line1
    c, d = line2

    x1, y1 = a.x, a.y
    x2, y2 = b.x, b.y
    x3, y3 = c.x, c.y
    x4, y4 = d.x, d.y

    x1_x2 = x1 - x2
    y3_y4 = y3 - y4
    y1_y2 = y1 - y2
    x3_x4 = x3 - x4

    d = x1_x2 * y3_y4 - y1_y2 * x3_x4

    if math.fabs(d) <= abs_tol:
        return None

    a = x1 * y2 - y1 * x2
    b = x3 * y4 - y3 * x4
    x = (a * x3_x4 - x1_x2 * b) / d
    y = (a * y3_y4 - y1_y2 * b) / d

    if not virtual:
        if x1 > x2:
            in_range = x2 <= x <= x1
        else:
            in_range = x1 <= x <= x2

        if not in_range:
            return None

        if x3 > x4:
            in_range = x4 <= x <= x3
        else:
            in_range = x3 <= x <= x4

        if not in_range:
            return None

        if y1 > y2:
            in_range = y2 <= y <= y1
        else:
            in_range = y1 <= y <= y2

        if not in_range:
            return None

        if y3 > y4:
            in_range = y4 <= y <= y3
        else:
            in_range = y3 <= y <= y4

        if not in_range:
            return None

    return Vec2((x, y))


def is_point_on_line(point: Vec2, line: Sequence[Vec2], ray=True, abs_tol=TOLERANCE) -> bool:
    """ Returns ``True`` if `point` is on `line`.

    Args:
        point: 2D point to test
        line: sequence of 2D start- and end point
        ray: if ``True`` point has to be on the infinite ray, if ``False`` point has to be on the line segment
        abs_tol: tolerance for minimum distance to line

    """

    px, py = point
    x1, y1 = line[0]
    x2, y2 = line[1]
    on_line = math.fabs((y2 - y1) * px - (x2 - x1) * py + (x2 * y1 - y2 * x1)) <= abs_tol
    if not on_line or ray:
        return on_line
    else:
        if x1 > x2:
            x1, x2 = x2, x1
        if not (x1 <= px <= x2):
            return False
        if y1 > y2:
            y1, y2 = y2, y1
        if not (y1 <= py <= y2):
            return False
        return True


def distance_point_line(point: Vec2, line: Sequence[Vec2]) -> float:
    """ Returns distance from `point` to `line`.

    Args:
         point: 2D point to test
         line: sequence of 2D start- and end point.

    """
    # wikipedia: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line.
    a, b = line
    if a.isclose(b):
        raise ZeroDivisionError('Not a line.')
    # |(b.y-a.y)*p.x - (b.x-a.x)*p.y + (b.x*a.y-b.y*a.x)|
    return math.fabs((a - point).det(b - point)) / (b - a).magnitude


def is_point_in_polygon(point: 'Vertex', polygon: Iterable['Vertex'], abs_tol=TOLERANCE) -> int:
    """
    Test if `point` is inside `polygon`.

    Args:
        point: 2D point to test
        polygon: iterable of 2D points
        abs_tol: tolerance for distance check

    Returns:
        ``+1`` for inside, ``0`` for on boundary line, ``-1`` for outside

    """
    # Source: http://www.faqs.org/faqs/graphics/algorithms-faq/
    # Subject 2.03: How do I find if a point lies within a polygon?

    polygon = Vec2.list(polygon)
    if not polygon[0].isclose(polygon[-1]):
        polygon.append(polygon[0])
    if len(polygon) < 4:  # 3+1 because first point == last point
        raise ValueError('At least 3 polygon points required.')
    x, y, *_ = point
    inside = False
    for i in range(len(polygon) - 1):
        x1, y1 = polygon[i]
        x2, y2 = polygon[i + 1]
        # is point on polygon boundary line:
        # is point in x-range of line
        a, b = (x2, x1) if x2 < x1 else (x1, x2)
        if a <= x <= b:
            # is point in y-range of line
            c, d = (y2, y1) if y2 < y1 else (y1, y2)
            if (c <= y <= d) and math.fabs((y2 - y1) * x - (x2 - x1) * y + (x2 * y1 - y2 * x1)) <= abs_tol:
                return 0
        if ((y1 <= y < y2) or (y2 <= y < y1)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside
    if inside:
        return 1
    else:
        return -1
