# Copyright (c) 2018-2021 Manfred Moitzi
# License: MIT License
# source: http://www.lee-mac.com/bulgeconversion.html
# source: http://www.afralisp.net/archive/lisp/Bulges1.htm
from typing import Any, TYPE_CHECKING, Tuple
import math
from ezdxf.math import Vec2

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

__all__ = [
    "bulge_to_arc",
    "bulge_3_points",
    "bulge_center",
    "bulge_radius",
    "arc_to_bulge",
]


def polar(p: Any, angle: float, distance: float) -> Vec2:
    """Returns the point at a specified `angle` and `distance` from point `p`.

    Args:
        p: point as :class:`Vec2` compatible object
        angle: angle in radians
        distance: distance

    """
    return Vec2(p) + Vec2.from_angle(angle, distance)


def angle(p1: Any, p2: Any) -> float:
    """Returns angle a line defined by two endpoints and x-axis in radians.

    Args:
        p1: start point as :class:`Vec2` compatible object
        p2: end point as :class:`Vec2` compatible object

    """
    return (Vec2(p2) - Vec2(p1)).angle


def arc_to_bulge(
    center: "Vertex", start_angle: float, end_angle: float, radius: float
) -> Tuple["Vec2", "Vec2", float]:
    """Returns bulge parameters from arc parameters.

    Args:
        center: circle center point as :class:`Vec2` compatible object
        start_angle: start angle in radians
        end_angle: end angle in radians
        radius: circle radius

    Returns:
        tuple: (start_point, end_point, bulge)

    """
    start_point = polar(center, start_angle, radius)
    end_point = polar(center, end_angle, radius)
    pi2 = math.pi * 2
    a = math.fmod((pi2 + (end_angle - start_angle)), pi2) / 4.0
    bulge = math.sin(a) / math.cos(a)
    return start_point, end_point, bulge


def bulge_3_points(
    start_point: "Vertex", end_point: "Vertex", point: "Vertex"
) -> float:
    """Returns bulge value defined by three points.

    Based on 3-Points to Bulge by `Lee Mac`_.

    Args:
        start_point: start point as :class:`Vec2` compatible object
        end_point: end point as :class:`Vec2` compatible object
        point: arbitrary point as :class:`Vec2` compatible object

    """
    a = (math.pi - angle(point, start_point) + angle(point, end_point)) / 2
    return math.sin(a) / math.cos(a)


def bulge_to_arc(
    start_point: "Vertex", end_point: "Vertex", bulge: float
) -> Tuple["Vec2", float, float, float]:
    """Returns arc parameters from bulge parameters.

    The arcs defined by bulge values of :class:`~ezdxf.entities.LWPolyline`
    and 2D :class:`~ezdxf.entities.Polyline` entities start at the vertex which
    includes the bulge value and ends at the following vertex.

    Based on Bulge to Arc by `Lee Mac`_.

    Args:
        start_point: start vertex as :class:`Vec2` compatible object
        end_point: end vertex as :class:`Vec2` compatible object
        bulge: bulge value

    Returns:
        Tuple: (center, start_angle, end_angle, radius)

    """
    r = signed_bulge_radius(start_point, end_point, bulge)
    a = angle(start_point, end_point) + (math.pi / 2 - math.atan(bulge) * 2)
    c = polar(start_point, a, r)
    if bulge < 0:
        return c, angle(c, end_point), angle(c, start_point), abs(r)
    else:
        return c, angle(c, start_point), angle(c, end_point), abs(r)


def bulge_center(
    start_point: "Vertex", end_point: "Vertex", bulge: float
) -> "Vec2":
    """Returns center of arc described by the given bulge parameters.

    Based on  Bulge Center by `Lee Mac`_.

    Args:
        start_point: start point as :class:`Vec2` compatible object
        end_point: end point as :class:`Vec2` compatible object
        bulge: bulge value as float


    """
    start_point = Vec2(start_point)
    a = angle(start_point, end_point) + (math.pi / 2.0 - math.atan(bulge) * 2.0)
    return start_point + Vec2.from_angle(
        a, signed_bulge_radius(start_point, end_point, bulge)
    )


def signed_bulge_radius(
    start_point: "Vertex", end_point: "Vertex", bulge: float
) -> float:
    return (
        Vec2(start_point).distance(Vec2(end_point))
        * (1.0 + (bulge * bulge))
        / 4.0
        / bulge
    )


def bulge_radius(
    start_point: "Vertex", end_point: "Vertex", bulge: float
) -> float:
    """Returns radius of arc defined by the given bulge parameters.

    Based on Bulge Radius by `Lee Mac`_

    Args:
        start_point: start point as :class:`Vec2` compatible object
        end_point: end point as :class:`Vec2` compatible object
        bulge: bulge value

    """
    return abs(signed_bulge_radius(start_point, end_point, bulge))
