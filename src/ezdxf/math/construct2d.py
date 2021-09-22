# Copyright (c) 2010-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List, Union

from functools import partial
import math
import warnings
from ezdxf.math import Vec3, Vec2, Matrix44, X_AXIS, Y_AXIS
from decimal import Decimal

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

TOLERANCE = 1e-10
RADIANS_90 = math.pi / 2.0
RADIANS_180 = math.pi
RADIANS_270 = RADIANS_90 * 3.0
RADIANS_360 = 2.0 * math.pi

__all__ = [
    "is_close_points",
    "closest_point",
    "convex_hull_2d",
    "distance_point_line_2d",
    "is_point_on_line_2d",
    "is_point_in_polygon_2d",
    "is_point_left_of_line",
    "point_to_line_relation",
    "linspace",
    "enclosing_angles",
    "reflect_angle_x_deg",
    "reflect_angle_y_deg",
    "sign",
    "area",
    "circle_radius_3p",
    "TOLERANCE",
    "has_matrix_2d_stretching"
]


def is_close_points(p1: "Vertex", p2: "Vertex", abs_tol=TOLERANCE) -> bool:
    """Deprecated function will be removed in v0.18! Use Vec(p1).isclose(p2)."""
    warnings.warn(
        "Deprecated function will be removed in v0.18! "
        "Use Vec3(p1).isclose(p2).",
        DeprecationWarning,
    )
    return Vec3(p1).isclose(p2, abs_tol=abs_tol)


def linspace(
    start: float, stop: float, num: int, endpoint=True
) -> Iterable[float]:
    """Return evenly spaced numbers over a specified interval, like
    numpy.linspace().

    Returns `num` evenly spaced samples, calculated over the interval
    [start, stop]. The endpoint of the interval can optionally be excluded.

    """
    if num < 0:
        raise ValueError(f"Number of samples, {num}, must be non-negative.")
    elif num == 0:
        return
    elif num == 1:
        yield start
        return

    start_dec = Decimal(start)
    count = (num - 1) if endpoint else num
    delta = (Decimal(stop) - start_dec) / count
    for _ in range(num):
        yield float(start_dec)
        start_dec += delta


def sign(f: float) -> float:
    """Return sign of float `f` as -1 or +1, 0 returns +1"""
    return -1.0 if f < 0.0 else +1.0


def reflect_angle_x_deg(a: float) -> float:
    """Returns reflected angle of `a` in x-direction in degrees.
    Angles are counter clockwise orientated and +x-axis is at 0 degrees.

    Args:
        a: angle to reflect in degrees

    """
    return (180.0 - (a % 360.0)) % 360.0


def reflect_angle_y_deg(a: float) -> float:
    """Returns reflected angle of `a` in y-direction in degrees.
    Angles are counter clockwise orientated and +y-axis is at 90 degrees.

    Args:
        a: angle to reflect in degrees

    """
    return (360.0 - (a % 360.0)) % 360.0


def closest_point(base: "Vertex", points: Iterable["Vertex"]) -> "Vec3":
    """Returns closest point to `base`.

    Args:
        base: base point as :class:`Vec3` compatible object
        points: iterable of points as :class:`Vec3` compatible object

    """
    base = Vec3(base)
    min_dist = None
    found = None
    for point in points:
        p = Vec3(point)
        dist = (base - p).magnitude
        if (min_dist is None) or (dist < min_dist):
            min_dist = dist
            found = p
    return found


def convex_hull_2d(points: Iterable["Vertex"]) -> List["Vertex"]:
    """Returns 2D convex hull for `points`.

    Args:
        points: iterable of points as :class:`Vec3` compatible objects,
            z-axis is ignored

    """

    def _convexhull(hull):
        while len(hull) > 2:
            # the last three points
            start_point, check_point, destination_point = hull[-3:]
            # curve not turns right
            if not is_point_left_of_line(
                check_point, start_point, destination_point
            ):
                # remove the penultimate point
                del hull[-2]
            else:
                break
        return hull

    points = sorted(set(Vec2.generate(points)))  # remove duplicate points

    if len(points) < 3:
        raise ValueError(
            "Convex hull calculation requires 3 or more unique points."
        )

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


def enclosing_angles(
    angle, start_angle, end_angle, ccw=True, abs_tol=TOLERANCE
):
    isclose = partial(math.isclose, abs_tol=abs_tol)

    s = start_angle % math.tau
    e = end_angle % math.tau
    a = angle % math.tau
    if isclose(s, e):
        return isclose(s, a)

    if s < e:
        r = s < a < e
    else:
        r = not (e < a < s)
    return r if ccw else not r


def is_point_on_line_2d(
    point: Vec2, start: Vec2, end: Vec2, ray=True, abs_tol=TOLERANCE
) -> bool:
    """Returns ``True`` if `point` is on `line`.

    Args:
        point: 2D point to test as :class:`Vec2`
        start: line definition point as :class:`Vec2`
        end: line definition point as :class:`Vec2`
        ray: if ``True`` point has to be on the infinite ray, if ``False``
            point has to be on the line segment
        abs_tol: tolerance for on line test

    """
    point_x, point_y = point
    start_x, start_y = start
    end_x, end_y = end
    on_line = (
        math.fabs(
            (end_y - start_y) * point_x
            - (end_x - start_x) * point_y
            + (end_x * start_y - end_y * start_x)
        )
        <= abs_tol
    )
    if not on_line or ray:
        return on_line
    else:
        if start_x > end_x:
            start_x, end_x = end_x, start_x
        if not (start_x - abs_tol <= point_x <= end_x + abs_tol):
            return False
        if start_y > end_y:
            start_y, end_y = end_y, start_y
        if not (start_y - abs_tol <= point_y <= end_y + abs_tol):
            return False
        return True


def point_to_line_relation(
    point: Vec2, start: Vec2, end: Vec2, abs_tol=TOLERANCE
) -> int:
    """Returns ``-1`` if `point` is left `line`, ``+1`` if `point` is right of
    `line` and ``0`` if `point` is on the `line`. The `line` is defined by two
    vertices given as arguments `start` and `end`.

    Args:
        point: 2D point to test as :class:`Vec2`
        start: line definition point as :class:`Vec2`
        end: line definition point as :class:`Vec2`
        abs_tol: tolerance for minimum distance to line

    """
    rel = (end.x - start.x) * (point.y - start.y) - (end.y - start.y) * (
        point.x - start.x
    )
    if abs(rel) <= abs_tol:
        return 0
    elif rel < 0:
        return +1
    else:
        return -1


def is_point_left_of_line(
    point: Vec2, start: Vec2, end: Vec2, colinear=False
) -> bool:
    """Returns ``True`` if `point` is "left of line" defined by `start-` and
    `end` point, a colinear point is also "left of line" if argument `colinear`
    is ``True``.

    Args:
        point: 2D point to test as :class:`Vec2`
        start: line definition point as :class:`Vec2`
        end: line definition point as :class:`Vec2`
        colinear: a colinear point is also "left of line" if ``True``

    """
    rel = point_to_line_relation(point, start, end)
    if colinear:
        return rel < 1
    else:
        return rel < 0


def distance_point_line_2d(point: Vec2, start: Vec2, end: Vec2) -> float:
    """Returns the normal distance from `point` to 2D line defined by `start-`
    and `end` point.
    """
    # wikipedia: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line.
    if start.isclose(end):
        raise ZeroDivisionError("Not a line.")
    return math.fabs((start - point).det(end - point)) / (end - start).magnitude


def is_point_in_polygon_2d(
    point: Union[Vec2, Vec3], polygon: Iterable[Vec2], abs_tol=TOLERANCE
) -> int:
    """Test if `point` is inside `polygon`.

    Args:
        point: 2D point to test as :class:`Vec2`
        polygon: iterable of 2D points as :class:`Vec2`
        abs_tol: tolerance for distance check

    Returns:
        ``+1`` for inside, ``0`` for on boundary line, ``-1`` for outside

    """
    # Source: http://www.faqs.org/faqs/graphics/algorithms-faq/
    # Subject 2.03: How do I find if a point lies within a polygon?
    polygon = list(polygon)  # shallow copy, because list will be modified
    if not polygon[0].isclose(polygon[-1]):
        polygon.append(polygon[0])
    if len(polygon) < 4:  # 3+1 because first point == last point
        raise ValueError("At least 3 polygon points required.")
    x = point.x
    y = point.y
    # ignore z-axis of Vec3()
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
            if (c <= y <= d) and math.fabs(
                (y2 - y1) * x - (x2 - x1) * y + (x2 * y1 - y2 * x1)
            ) <= abs_tol:
                return 0
        if ((y1 <= y < y2) or (y2 <= y < y1)) and (
            x < (x2 - x1) * (y - y1) / (y2 - y1) + x1
        ):
            inside = not inside
    if inside:
        return 1
    else:
        return -1


def circle_radius_3p(a: Vec3, b: Vec3, c: Vec3) -> float:
    ba = b - a
    ca = c - a
    cb = c - b
    upper = ba.magnitude * ca.magnitude * cb.magnitude
    lower = ba.cross(ca).magnitude * 2.0
    return upper / lower


def area(vertices: Iterable["Vertex"]) -> float:
    """Returns the area of a polygon, returns the projected area in the
    xy-plane for 3D vertices.
    """
    _vertices = Vec3.list(vertices)
    if len(_vertices) < 3:
        raise ValueError("At least 3 vertices required.")

    # Close polygon:
    if not _vertices[0].isclose(_vertices[-1]):
        _vertices.append(_vertices[0])

    return abs(
        sum(
            (p1.x * p2.y - p1.y * p2.x)
                for p1, p2 in zip(_vertices, _vertices[1:])
        )
        / 2
    )


def has_matrix_2d_stretching(m: Matrix44) -> bool:
    """Returns ``True`` if matrix `m` performs a non-uniform xy-scaling.
    Uniform scaling is not stretching in this context.

    Does not check if the target system is a cartesian coordinate system, use the
    :class:`~ezdxf.math.Matrix44` property :attr:`~ezdxf.math.Matrix44.is_cartesian`
    for that.
    """
    ux = m.transform_direction(X_AXIS)
    uy = m.transform_direction(Y_AXIS)
    return not math.isclose(ux.magnitude_square, uy.magnitude_square)
