# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
import math
from .ray import Ray2D
from .base import equals_almost

HALF_PI = math.pi / 2.


def distance(point1, point2):
    return math.hypot(point1[0] - point2[0], point1[1] - point2[1])


def midpoint(point1, point2):
    return (point1[0] + point2[0]) * .5, (point1[1] + point2[1]) * .5


class Circle(object):
    def __init__(self, center_point, radius=1.0):
        self._center_point = center_point
        self._radius = float(radius)
        assert (self.radius > 0.)

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
        center = center_ray1.intersect(center_ray2)
        r = distance(center, p1)
        return Circle(center, r)

    @property
    def center_point(self):
        return self._center_point

    @property
    def radius(self):
        return self._radius

    def get_point(self, angle):
        """ calculate point on circle at angle as Point2D
        """
        x = self.center_point[0] + self.radius * math.cos(angle)
        y = self.center_point[1] + self.radius * math.sin(angle)
        return x, y

    def within(self, point):
        """ test if point is within circle
        """
        radius2 = distance(self._center_point, point)
        return self.radius >= radius2

    def in_x_range(self, x):
        mx = self.center_point[0]
        r = self.radius
        return (mx - r) <= x <= (mx + r)

    def in_y_range(self, y):
        my = self.center_point[1]
        r = self.radius
        return (my - r) <= y <= (my + r)

    def get_y(self, x):
        """ calculate the y-coordinate at the given x-coordinate
        result: list of Point2D
        list is empty if the x-coordinate ist out of range of the circle
        """
        result = list()
        if self.in_x_range(x):
            dx = self.center_point[0] - x
            dy = (self.radius ** 2 - dx ** 2) ** 0.5  # pythagoras
            result.append(self.center_point[1] + dy)
            result.append(self.center_point[1] - dy)
        return result

    def get_x(self, y):
        """ calculate the x-coordinate at the given y-coordinate
        result: list of Point2D
        list is empty if the y-coordinate ist out of range of the circle
        """
        result = list()
        if self.in_y_range(y):
            dy = self.center_point[1] - y
            dx = (self.radius ** 2 - dy ** 2) ** 0.5  # pythagoras
            result.append(self.center_point[0] + dx)
            result.append(self.center_point[0] - dx)
        return result

    def tangent(self, angle):
        """ calulate tangent to circle at angle as Ray2D
        """
        point_on_circle = self.get_point(angle)
        ray = Ray2D(self.center_point, point_on_circle)
        return ray.normal_through(point_on_circle)

    def intersect_ray(self, ray, places=7):
        """ calculates the intersection points for circle with ray
            returns a list of Point2D
            places: significant decimal places for tests (e.g. test for tangents)
            list contains:
            0 points .. no intersection
            1 point .. ray is a tangent on the circle
            2 points .. ray intersects with the circle

        """
        def get_angle(point):
            dx = point[0] - self.center_point[0]
            dy = point[1] - self.center_point[1]
            return math.atan2(dy, dx)

        normal_ray = ray.normal_through(self.center_point)
        cross_point = ray.intersect(normal_ray)
        dist = distance(self.center_point, cross_point)
        result = list()
        if dist < self.radius:  # intersect in two points
            if equals_almost(dist, 0., places):  # if ray goes through midpoint
                angle = normal_ray.angle
                alpha = HALF_PI
            else:  # the exact direction of angle (all 4 quadrants Q1-Q4) is important:
                # normal_ray.angle is only at the center point correct
                angle = get_angle(cross_point)
                alpha = math.acos(distance(cross_point, self.center_point) / self.radius)
            result.append(self.get_point(angle + alpha))
            result.append(self.get_point(angle - alpha))
        elif equals_almost(dist, self.radius, places):  # ray is a tangent of circle
            result.append(cross_point)
            # else no intersection
        return result

    def intersect_circle(self, other_circle, places=7):
        """ calculates the intersection points for circle with other_circle
            places: significant decimal places for tests (e.g. test for circle touch point)
            returns a list of Point2D
            list contains:
            0 points .. no intersection
            1 point .. circle touches the other_circle in one point
            2 points .. circle intersects with the other_circle

        """
        def get_angle_through_center_points():
            dx = other_circle.center_point[0] - self.center_point[0]
            dy = other_circle.center_point[1] - self.center_point[1]
            return math.atan2(dy, dx)

        R1 = self.radius
        R2 = other_circle.radius
        dist = distance(self.center_point, other_circle.center_point)
        max_dist = R1 + R2
        min_dist = math.fabs(R1 - R2)
        result = list()
        if min_dist <= dist <= max_dist:
            if equals_almost(dist, max_dist, places) or equals_almost(dist, min_dist,
                                                                      places):  # circles touches in one point
                angle = get_angle_through_center_points()
                result.append(self.get_point(angle))
            else:  # circles intersect in two points
                alpha = math.acos((R2 ** 2 - R1 ** 2 - dist ** 2) / (-2. * R1 * dist))  # 'Cosinus-Satz'
                angle = get_angle_through_center_points()
                result.append(self.get_point(angle + alpha))
                result.append(self.get_point(angle - alpha))
        return result
