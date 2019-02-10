# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
# source: http://www.lee-mac.com/bulgeconversion.html
# source: http://www.afralisp.net/archive/lisp/Bulges1.htm
from typing import Any, TYPE_CHECKING, Tuple
from .vector import Vector
import math

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


def polar(p: Any, angle: float, distance: float) -> Vector:
    """
    Returns the point at a specified `angle` and `distance` from point `p`.

    Args:
        p: point (x, y) as args accepted by Vector()
        angle: angle in radians
        distance: distance

    """
    return Vector(p) + Vector.from_angle(angle, distance)


def angle(p1: Any, p2: Any) -> float:
    """
    Returns an angle in radians of a line defined by two endpoints
    Args:
        p1: start point (x, y) as args accepted by Vector()
        p2: end point (x, y) as args accepted by Vector()

    """
    return (Vector(p2) - p1).angle


def arc_to_bulge(center: 'Vertex', start_angle: float, end_angle: float, radius: float) -> Tuple[Vector, Vector, float]:
    """
    Calculate bulge parameters from arc parameters.

    Args:
        center: circle center point (x, y) as args accepted by Vector()
        start_angle: start angle in radians
        end_angle: end angle in radians
        radius: circle radius

    Returns: (start_point, end_point, bulge)

    """
    start_point = polar(center, start_angle, radius)
    end_point = polar(center, end_angle, radius)
    pi2 = math.pi * 2
    a = math.fmod((pi2 + (end_angle - start_angle)), pi2) / 4.
    bulge = math.sin(a) / math.cos(a)
    return start_point, end_point, bulge


def bulge_3_points(start_point: 'Vertex', end_point: 'Vertex', point: 'Vertex') -> float:
    """
    Calculate bulge value defined by three points.

    Args:
        start_point: start point (x, y) of arc as args accepted by Vector()
        end_point: end point (x, y) of arc as args accepted by Vector()
        point: arbitrary point (x, y) on arc as args accepted by Vector()

    Returns: bulge value

    Based on 3-Points to Bulge by Lee Mac

    """
    a = (math.pi - angle(point, start_point) + angle(point, end_point)) / 2
    return math.sin(a) / math.cos(a)


def bulge_to_arc(start_point: 'Vertex', end_point: 'Vertex', bulge: float) -> Tuple[Vector, float, float, float]:
    """
    Calculate arc parameters from bulge parameters.

    Based on Bulge to Arc by Lee Mac

    Args:
        start_point: start vertex (x, y) as args accepted by Vector()
        end_point: end vertex (x, y) as args accepted by Vector()
        bulge: bulge value

    Returns: (center, start_angle, end_angle, radius)

    """
    r = signed_bulge_radius(start_point, end_point, bulge)
    a = angle(start_point, end_point) + (math.pi / 2 - math.atan(bulge) * 2)
    c = polar(start_point, a, r)
    if bulge < 0:
        return c, angle(c, end_point), angle(c, start_point), abs(r)
    else:
        return c, angle(c, start_point), angle(c, end_point), abs(r)


def bulge_center(start_point: 'Vertex', end_point: 'Vertex', bulge: float) -> Vector:
    """
    Calculate center of arc described by the given bulge parameters.

    Based on  Bulge Center by Lee Mac.

    Args:
        start_point: start point (x, y) as args accepted by Vector()
        end_point: end point (x, y) as args accepted by Vector()
        bulge: bulge value

    Returns: Vector

    """
    start_point = Vector(start_point)
    a = angle(start_point, end_point) + (math.pi / 2. - math.atan(bulge) * 2.)
    return start_point + Vector.from_angle(a, signed_bulge_radius(start_point, end_point, bulge))


def signed_bulge_radius(start_point: 'Vertex', end_point: 'Vertex', bulge: float) -> float:
    return Vector(start_point).distance(end_point) * (1. + (bulge * bulge)) / 4. / bulge


def bulge_radius(start_point: 'Vertex', end_point: 'Vertex', bulge: float) -> float:
    """
    Calculate radius of arc defined by the given bulge parameters.

    Based on Bulge Radius by Lee Mac

    Args:
        start_point: start point (x, y) as args accepted by Vector()
        end_point: end point (x, y) as args accepted by Vector()
        bulge: bulge value

    """
    return abs(signed_bulge_radius(start_point, end_point, bulge))
