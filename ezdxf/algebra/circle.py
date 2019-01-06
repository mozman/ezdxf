# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple
import math
from .ray import ConstructionRay
from .vector import Vector
from .base import equals_almost

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

HALF_PI = math.pi / 2.


def _distance(point1: 'Vertex', point2: 'Vertex') -> float:
    return math.hypot(point1[0] - point2[0], point1[1] - point2[1])


def midpoint(point1: 'Vertex', point2: 'Vertex') -> Tuple[float, float]:
    return (point1[0] + point2[0]) * .5, (point1[1] + point2[1]) * .5


class ConstructionCircle:
    def __init__(self, center: 'Vertex', radius: float = 1.0):
        self.center = Vector(center)
        self.radius = float(radius)
        if self.radius <= 0.:
            raise ValueError("Radius has to be > 0.")

    @staticmethod
    def from_3p(p1: 'Vertex', p2: 'Vertex', p3: 'Vertex') -> 'ConstructionCircle':
        """ Creates a circle by three points.
        """
        ray1 = ConstructionRay(p1, p2)
        ray2 = ConstructionRay(p1, p3)
        mid_point1 = midpoint(p1, p2)
        mid_point2 = midpoint(p1, p3)
        center_ray1 = ray1.normal_through(mid_point1)
        center_ray2 = ray2.normal_through(mid_point2)
        center = Vector(center_ray1.intersect(center_ray2))
        r = center.distance(p1)
        return ConstructionCircle(center, r)

    def get_point(self, angle: float) -> Vector:
        """
        Calculate point on circle at `angle` as Vector.

        """
        return self.center + Vector.from_rad_angle(angle, self.radius)

    def within(self, point: 'Vertex') -> bool:
        """
        Test if point is within circle.

        """
        radius2 = self.center.distance(point)
        return self.radius >= radius2

    def in_x_range(self, x: float) -> bool:
        mx = self.center.x
        r = self.radius
        return (mx - r) <= x <= (mx + r)

    def in_y_range(self, y: float) -> bool:
        my = self.center.y
        r = self.radius
        return (my - r) <= y <= (my + r)

    def get_y(self, x: float) -> Tuple[float]:
        """
        Calculates y-coordinates at the given x-coordinate.

        Args:
            x: x-coordinate

        Returns: tuple of y-coordinates, empty tuple if the x-coordinate ist outside of circle

        """
        result = []
        if self.in_x_range(x):
            dx = self.center.x - x
            dy = (self.radius ** 2 - dx ** 2) ** 0.5  # pythagoras
            result.append(self.center.y + dy)
            result.append(self.center.y - dy)
        return tuple(result)

    def get_x(self, y: float) -> Tuple[float]:
        """
        Calculates x-coordinates at the given y-coordinate.

        Args:
            y: y-coordinate

        Returns: tuple of x-coordinates, empty tuple if the y-coordinate ist outside of circle

        """
        result = []
        if self.in_y_range(y):
            dy = self.center.y - y
            dx = (self.radius ** 2 - dy ** 2) ** 0.5  # pythagoras
            result.append(self.center.x + dx)
            result.append(self.center.x - dx)
        return tuple(result)

    def tangent(self, angle: float) -> ConstructionRay:
        """
        Calculate tangent to circle at angle as ConstructionRay().

        """
        point_on_circle = self.get_point(angle)
        ray = ConstructionRay(self.center, point_on_circle)
        return ray.normal_through(point_on_circle)

    def intersect_ray(self, ray: ConstructionRay, places: int = 7) -> Tuple[Vector]:
        """
        Calculates the intersection points for this circle with a ray.

        Args:
            ray: intersection ray
            places: significant decimal places for tests (e.g. test for tangents)

        Returns: tuple of Vector()

            tuple contains:
            0 points .. no intersection
            1 point .. ray is a tangent on the circle
            2 points .. ray intersects with the circle

        """
        normal_ray = ray.normal_through(self.center)
        intersection_point = ray.intersect(normal_ray)
        dist = self.center.distance(intersection_point)
        result = []
        if dist < self.radius:  # intersect in two points
            if equals_almost(dist, 0., places):  # if ray goes through midpoint
                angle = normal_ray.angle
                alpha = HALF_PI
            else:  # the exact direction of angle (all 4 quadrants Q1-Q4) is important:
                # normal_ray.angle is only at the center point correct
                angle = (intersection_point - self.center).angle_rad
                alpha = math.acos(intersection_point.distance(self.center) / self.radius)
            result.append(self.get_point(angle + alpha))
            result.append(self.get_point(angle - alpha))
        elif equals_almost(dist, self.radius, places):  # ray is a tangent of circle
            result.append(intersection_point)
            # else no intersection
        return tuple(result)

    def intersect_circle(self, other: 'ConstructionCircle', places: int = 7) -> Tuple[Vector]:
        """
        Calculates the intersection points for two circles.

        Args:
            other: intersection circle
            places: significant decimal places for tests (e.g. test for circle touch point)

        Returns: tuple of Vector()

            tuple contains:
            0 points .. no intersection
            1 point .. circle touches the other_circle in one point
            2 points .. circle intersects with the other_circle

        """

        def get_angle_through_center_points():
            return (other.center - self.center).angle_rad

        radius1 = self.radius
        radius2 = other.radius
        dist = self.center.distance(other.center)
        max_dist = radius1 + radius2
        min_dist = math.fabs(radius1 - radius2)
        result = []
        if min_dist <= dist <= max_dist:
            if equals_almost(dist, max_dist, places) or equals_almost(dist, min_dist,
                                                                      places):  # circles touches in one point
                angle = get_angle_through_center_points()
                result.append(self.get_point(angle))
            else:  # circles intersect in two points
                alpha = math.acos((radius2 ** 2 - radius1 ** 2 - dist ** 2) / (-2. * radius1 * dist))  # 'Cosinus-Satz'
                angle = get_angle_through_center_points()
                result.append(self.get_point(angle + alpha))
                result.append(self.get_point(angle - alpha))
        return tuple(result)
