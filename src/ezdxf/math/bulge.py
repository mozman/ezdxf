# Copyright (c) 2018-2026 Manfred Moitzi
# License: MIT License
# source: http://www.lee-mac.com/bulgeconversion.html
# source: http://www.afralisp.net/archive/lisp/Bulges1.htm
from __future__ import annotations
from typing import Any
import math
from ezdxf.math import Vec2, UVec

__all__ = [
    "bulge_to_arc",
    "bulge_3_points",
    "bulge_center",
    "bulge_radius",
    "arc_to_bulge",
    "bulge_from_radius_and_chord",
    "bulge_from_arc_angle",
]

# Tolerance to detect collinear points and floating point inaccuracies at the
# semicircle boundary, bulge values beyond 1e12 describe arcs which are
# indistinguishable from straight segments:
_TOLERANCE = 1e-12


def _polar(p: Any, angle: float, distance: float) -> Vec2:
    """Returns the point at a specified `angle` and `distance` from point `p`.

    Args:
        p: point as :class:`Vec2` compatible object
        angle: angle in radians
        distance: distance

    (internal API)

    """
    return Vec2(p) + Vec2.from_angle(angle, distance)


def _angle(p1: Any, p2: Any) -> float:
    """Returns the angle of the line defined by two endpoints and the x-axis in
    radians, the angle is in the range (-π, π].

    Args:
        p1: start point as :class:`Vec2` compatible object
        p2: end point as :class:`Vec2` compatible object

    (internal API)

    """
    return (Vec2(p2) - Vec2(p1)).angle


def arc_to_bulge(
    center: UVec, start_angle: float, end_angle: float, radius: float
) -> tuple[Vec2, Vec2, float]:
    """Returns bulge parameters from arc parameters.

    The arc is always interpreted as counter-clockwise from `start_angle` to
    `end_angle`, the sweep angle is normalized to the range [0, 2π). A full
    circle is not representable by a bulge value and returns the bulge value
    ``0``.

    Args:
        center: circle center point as :class:`Vec2` compatible object
        start_angle: start angle in radians
        end_angle: end angle in radians
        radius: circle radius

    Returns:
        (start_point, end_point, bulge)

    """
    start_point = _polar(center, start_angle, radius)
    end_point = _polar(center, end_angle, radius)
    pi2 = math.pi * 2
    a = math.fmod((pi2 + (end_angle - start_angle)), pi2) / 4.0
    bulge = math.tan(a)
    return start_point, end_point, bulge


def bulge_3_points(start_point: UVec, end_point: UVec, point: UVec) -> float:
    """Returns bulge value defined by three points.

    Based on 3-Points to Bulge by `Lee Mac`_.

    Args:
        start_point: start point as :class:`Vec2` compatible object
        end_point: end point as :class:`Vec2` compatible object
        point: a point on the arc as :class:`Vec2` compatible object

    Returns:
        bulge value, ``0`` if the three points are collinear or if two of them
        are equal

    """
    a = (math.pi - _angle(point, start_point) + _angle(point, end_point)) / 2.0
    if abs(math.cos(a)) < _TOLERANCE:  # the three points are collinear
        return 0.0
    return math.tan(a)


def bulge_to_arc(
    start_point: UVec, end_point: UVec, bulge: float
) -> tuple[Vec2, float, float, float]:
    """Returns arc parameters from bulge parameters.

    The arcs defined by bulge values of :class:`~ezdxf.entities.LWPolyline`
    and 2D :class:`~ezdxf.entities.Polyline` entities start at the vertex which
    includes the bulge value and ends at the following vertex.

    .. important::

        The return values always describe a counter-clockwise oriented arc, so for
        clockwise arcs (negative bulge values) the start and end angles are swapped and
        the arc starts at the `end_point` and ends at the `start_point`.

    Based on Bulge to Arc by `Lee Mac`_.

    .. note::

        Treat bulge values below the required accuracy (e.g. ``abs(bulge) < 1e-6``)
        as straight segments, the radius of such arcs is very large.

        A zero-length chord (equal `start_point` and `end_point`) returns a
        degenerate arc with radius ``0``.

    Args:
        start_point: start vertex as :class:`Vec2` compatible object
        end_point: end vertex as :class:`Vec2` compatible object
        bulge: bulge value

    Returns:
        (center, start_angle, end_angle, radius)

    Raises:
        ValueError: `bulge` is ``0``

    """
    if bulge == 0.0:
        raise ValueError("bulge value must not be 0")
    center = bulge_center(start_point, end_point, bulge)
    radius = abs(_signed_bulge_radius(start_point, end_point, bulge))
    if bulge < 0:
        return center, _angle(center, end_point), _angle(center, start_point), radius
    return center, _angle(center, start_point), _angle(center, end_point), radius


def bulge_center(start_point: UVec, end_point: UVec, bulge: float) -> Vec2:
    """Returns center of arc described by the given bulge parameters.

    Based on Bulge Center by `Lee Mac`_.

    Args:
        start_point: start point as :class:`Vec2` compatible object
        end_point: end point as :class:`Vec2` compatible object
        bulge: bulge value as float

    Raises:
        ValueError: `bulge` is ``0``

    """
    if bulge == 0.0:
        raise ValueError("bulge value must not be 0")
    start_point = Vec2(start_point)
    a = _angle(start_point, end_point) + (math.pi / 2.0 - math.atan(bulge) * 2.0)
    return start_point + Vec2.from_angle(
        a, _signed_bulge_radius(start_point, end_point, bulge)
    )


def _signed_bulge_radius(start_point: UVec, end_point: UVec, bulge: float) -> float:
    """Returns the signed radius of the arc defined by the given bulge
    parameters, the sign of the radius is the sign of the `bulge` value.

    Args:
        start_point: start point as :class:`Vec2` compatible object
        end_point: end point as :class:`Vec2` compatible object
        bulge: bulge value

    (internal API)

    """
    return (
        Vec2(start_point).distance(Vec2(end_point))
        * (1.0 + (bulge * bulge))
        / 4.0
        / bulge
    )


def bulge_radius(start_point: UVec, end_point: UVec, bulge: float) -> float:
    """Returns radius of arc defined by the given bulge parameters.

    Based on Bulge Radius by `Lee Mac`_.

    Args:
        start_point: start point as :class:`Vec2` compatible object
        end_point: end point as :class:`Vec2` compatible object
        bulge: bulge value

    Raises:
        ValueError: `bulge` is ``0``

    """
    if bulge == 0.0:
        raise ValueError("bulge value must not be 0")
    return abs(_signed_bulge_radius(start_point, end_point, bulge))


def bulge_from_radius_and_chord(radius: float, chord: float) -> float:
    """Returns the bulge value for the given arc radius and chord length.

    The bulge value depends on the magnitude of the arguments, the sign of
    `radius` and `chord` is ignored. Returns 0 if the radius is zero or the
    radius is too small for the given chord length to create an arc.

    Args:
        radius: arc radius
        chord: chord length

    """
    # https://github.com/mozman/ezdxf/discussions/758
    if radius == 0.0:
        return 0.0
    x = abs(chord) / (2.0 * abs(radius))
    if x > 1.0:  # the chord is too long for the given radius
        # tolerate floating point inaccuracies at the semicircle boundary:
        return 1.0 if math.isclose(x, 1.0, rel_tol=_TOLERANCE) else 0.0
    return x / (1.0 + math.sqrt(1.0 - x * x))


def bulge_from_arc_angle(angle: float) -> float:
    """Returns the bulge value for the given arc angle.

    The `angle` is normalized to the range (-2π, 2π), a full circle is not
    representable by a bulge value and returns ``0``.

    Args:
        angle: arc angle in radians

    """
    # https://github.com/mozman/ezdxf/discussions/758
    angle = math.fmod(angle, math.pi * 2)
    return math.tan(angle / 4.0)
