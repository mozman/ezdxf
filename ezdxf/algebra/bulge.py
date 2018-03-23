# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
# source: http://www.lee-mac.com/bulgeconversion.html
# source: http://www.afralisp.net/archive/lisp/Bulges1.htm
from .vector import Vector
import math


# minusp: Verifies that a number is negative
# rem: Divides the first number by the second, and returns the remainder (math.fmod)
# polar signature: (polar pt ang dist) - Returns the UCS 3D point at a specified angle and distance from a point
def polar(p, ang, dist):
    return Vector(p) + Vector.from_rad_angle(ang, dist)


# angle signature: (angle pt1 pt2) - Returns an angle in radians of a line defined by two endpoints
def angle(p1, p2):
    return (Vector(p2) - p1).angle_rad


def arc_to_bulge(center, start_angle, end_angle, radius):
    """
    Calculate bulge parameters from arc parameters.

    Args:
        center: circle center point as (x, y) tuple
        start_angle: start angle in radians
        end_angle: end angle in radians
        radius: circle radius

    Returns: (start_point, end_point, bulge)

    """
    start_point = polar(center, start_angle, radius)
    end_point = polar(center, end_angle, radius)
    pi2 = math.pi*2
    a = math.fmod((pi2 + (end_angle - start_angle)), pi2) / 4.
    bulge = math.sin(a) / math.cos(a)
    return start_point, end_point, bulge


def bulge_3_points(start_point, end_point, point):
    """
    Calculate bulge value defined by three points.

    Args:
        start_point: start point of arc
        end_point: end point of arc
        point: arbitrary point on arc

    Returns: bulge value as float

    Based on 3-Points to Bulge by Lee Mac

    """
    a = (math.pi - angle(point, start_point) + angle(point, end_point)) / 2
    return math.sin(a) / math.cos(a)


def bulge_to_arc(start_point, end_point, bulge):
    """
    Calculate arc parameters from bulge parameters.

    Based on Bulge to Arc by Lee Mac

    Args:
        start_point: start vertex as (x, y) tuple
        end_point: end vertex as (x, y) tuple
        bulge: bulge value as float

    Returns: (center, start_angle, end_angle, radius)

    """
    r = signed_bulge_radius(start_point, end_point, bulge)
    a = angle(start_point, end_point) + (math.pi / 2 - math.atan(bulge) * 2)
    c = polar(start_point, a, r)
    if bulge < 0:
        return c, angle(c, end_point), angle(c, start_point), abs(r)
    else:
        return c, angle(c, start_point), angle(c, end_point), abs(r)


def bulge_center(start_point, end_point, bulge):
    """
    Calculate center of arc described by the given bulge parameters.

    Based on  Bulge Center by Lee Mac.

    Args:
        start_point: start vertex as (x, y) tuple
        end_point: end vertex as (x, y) tuple
        bulge: bulge value as float

    Returns: Vector

    """
    start_point = Vector(start_point)
    a = angle(start_point, end_point) + (math.pi / 2. - math.atan(bulge) * 2.)
    return start_point + Vector.from_rad_angle(a, signed_bulge_radius(start_point, end_point, bulge))


def signed_bulge_radius(start_point, end_point, bulge):
    return Vector(start_point).distance(end_point) * (1. + (bulge * bulge)) / 4. / bulge


def bulge_radius(start_point, end_point, bulge):
    """
    Calculate radius of arc defined by the given bulge parameters.

    Based on Bulge Radius by Lee Mac

    Args:
        start_point: start vertex as (x, y) tuple
        end_point: end vertex as (x, y) tuple
        bulge: bulge value as float

    """
    return abs(signed_bulge_radius(start_point, end_point, bulge))

