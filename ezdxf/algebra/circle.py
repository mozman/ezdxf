# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
import math
from .ray import Ray2D
from .vector import Vector
from .base import equals_almost

HALF_PI = math.pi / 2.


def _distance(point1, point2):
    return math.hypot(point1[0] - point2[0], point1[1] - point2[1])


def midpoint(point1, point2):
    return (point1[0] + point2[0]) * .5, (point1[1] + point2[1]) * .5


class Circle(object):
    def __init__(self, center, radius=1.0):
        self.center = Vector(center)
        self.radius = float(radius)
        if self.radius <= 0.:
            raise ValueError("Radius has to be > 0.")

    @staticmethod
    def from_3p(p1, p2, p3):
        """ creates a circle through 3 points
        """
        ray1 = Ray2D(p1, p2)
        ray2 = Ray2D(p1, p3)
        mid_point1 = midpoint(p1, p2)
        mid_point2 = midpoint(p1, p3)
        center_ray1 = ray1.normal_through(mid_point1)
        center_ray2 = ray2.normal_through(mid_point2)
        center = Vector(center_ray1.intersect(center_ray2))
        r = center.distance(p1)
        return Circle(center, r)

    def get_point(self, angle):
        """
        Calculate point on circle at angle as Vector.

        """
        return self.center + Vector.from_rad_angle(angle, self.radius)

    def within(self, point):
        """
        Test if point is within circle.

        """
        radius2 = self.center.distance(point)
        return self.radius >= radius2

    def in_x_range(self, x):
        mx = self.center.x
        r = self.radius
        return (mx - r) <= x <= (mx + r)

    def in_y_range(self, y):
        my = self.center.y
        r = self.radius
        return (my - r) <= y <= (my + r)

    def get_y(self, x):
        """
        Calculate the y-coordinate at the given x-coordinate.

        Args:
            x: x-coordinate

        Returns: list of Vector, empty list if the x-coordinate ist outside of circle

        """
        result = []
        if self.in_x_range(x):
            dx = self.center.x - x
            dy = (self.radius ** 2 - dx ** 2) ** 0.5  # pythagoras
            result.append(self.center.y + dy)
            result.append(self.center.y - dy)
        return result

    def get_x(self, y):
        """
        Calculate the x-coordinate at the given y-coordinate.
        Args:
            y: y-coordinate

        Returns: list of Vector, empty list if the y-coordinate ist outside of circle

        """
        result = []
        if self.in_y_range(y):
            dy = self.center.y - y
            dx = (self.radius ** 2 - dy ** 2) ** 0.5  # pythagoras
            result.append(self.center.x + dx)
            result.append(self.center.x - dx)
        return result

    def tangent(self, angle):
        """
        Calculate tangent to circle at angle as Ray2D

        """
        point_on_circle = self.get_point(angle)
        ray = Ray2D(self.center, point_on_circle)
        return ray.normal_through(point_on_circle)

    def intersect_ray(self, ray, places=7):
        """
        Calculates the intersection points for circle with a ray.

        Args:
            ray: Ray2D() object
            places: significant decimal places for tests (e.g. test for tangents)

        Returns: list of Vector

            return list contains:
            0 points .. no intersection
            1 point .. ray is a tangent on the circle
            2 points .. ray intersects with the circle

        """
        normal_ray = ray.normal_through(self.center)
        cross_point = ray.intersect(normal_ray)
        dist = self.center.distance(cross_point)
        result = []
        if dist < self.radius:  # intersect in two points
            if equals_almost(dist, 0., places):  # if ray goes through midpoint
                angle = normal_ray.angle
                alpha = HALF_PI
            else:  # the exact direction of angle (all 4 quadrants Q1-Q4) is important:
                # normal_ray.angle is only at the center point correct
                angle = (cross_point - self.center).angle_rad
                alpha = math.acos(cross_point.distance(self.center) / self.radius)
            result.append(self.get_point(angle + alpha))
            result.append(self.get_point(angle - alpha))
        elif equals_almost(dist, self.radius, places):  # ray is a tangent of circle
            result.append(cross_point)
            # else no intersection
        return result

    def intersect_circle(self, other, places=7):
        """
        Calculates the intersection points for circle with other circle.

        Args:
            other: other Circle() instance
            places: significant decimal places for tests (e.g. test for circle touch point)


        Returns: list of Vector

        Return list contains:
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
        return result
