# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple, Sequence
import math
from .line import ConstructionRay
from .vector import Vector, Vec2
from .bbox import BoundingBox2d
from .construct2d import ConstructionTool

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, VecXY

HALF_PI = math.pi / 2.


def _distance(point1: 'Vertex', point2: 'Vertex') -> float:
    return math.hypot(point1[0] - point2[0], point1[1] - point2[1])


def midpoint(point1: 'Vertex', point2: 'Vertex') -> Tuple[float, float]:
    return (point1[0] + point2[0]) * .5, (point1[1] + point2[1]) * .5


class ConstructionCircle(ConstructionTool):
    def __init__(self, center: 'Vertex', radius: float = 1.0):
        self.center = Vec2(center)
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
        center_ray1 = ray1.orthogonal(mid_point1)
        center_ray2 = ray2.orthogonal(mid_point2)
        center = Vector(center_ray1.intersect(center_ray2))
        r = center.distance(p1)
        return ConstructionCircle(center, r)

    @property
    def bounding_box(self) -> 'BoundingBox2d':
        rvec = Vec2((self.radius, self.radius))
        return BoundingBox2d(self.center - rvec, self.center + rvec)

    def move(self, dx: float, dy: float) -> None:
        """
        Move circle about `dx` in x-axis and about `dy` in y-axis.

        Args:
            dx: translation in x-axis
            dy: translation in y-axis

        """
        self.center += Vec2((dx, dy))

    def get_point(self, angle: float) -> Vec2:
        """
        Calculate point on circle at `angle` as Vector.

        """
        return self.center + Vec2.from_angle(angle, self.radius)

    def within(self, point: 'Vertex') -> bool:
        """
        Test if point is within circle.

        """
        radius2 = self.center.distance(Vec2(point))
        return self.radius >= radius2

    def in_x_range(self, x: float) -> bool:
        mx = self.center.x
        r = self.radius
        return (mx - r) <= x <= (mx + r)

    def in_y_range(self, y: float) -> bool:
        my = self.center.y
        r = self.radius
        return (my - r) <= y <= (my + r)

    def get_y(self, x: float) -> Sequence[float]:
        """
        Calculates y-coordinates at the given x-coordinate.

        Args:
            x: x-coordinate

        Returns: tuple of y-coordinates, empty tuple if the x-coordinate ist outside of circle

        """
        if self.in_x_range(x):
            dx = self.center.x - x
            dy = (self.radius ** 2 - dx ** 2) ** 0.5  # pythagoras
            return self.center.y + dy, self.center.y - dy
        else:
            return tuple()

    def get_x(self, y: float) -> Sequence[float]:
        """
        Calculates x-coordinates at the given y-coordinate.

        Args:
            y: y-coordinate

        Returns: tuple of x-coordinates, empty tuple if the y-coordinate ist outside of circle

        """

        if self.in_y_range(y):
            dy = self.center.y - y
            dx = (self.radius ** 2 - dy ** 2) ** 0.5  # pythagoras
            return self.center.x + dx, self.center.x - dx
        else:
            return tuple()

    def tangent(self, angle: float) -> ConstructionRay:
        """
        Calculate tangent to circle at angle as ConstructionRay().

        """
        point_on_circle = self.get_point(angle)
        ray = ConstructionRay(self.center, point_on_circle)
        return ray.orthogonal(point_on_circle)

    def intersect_ray(self, ray: ConstructionRay, abs_tol: float = 1e-12) -> Sequence[Vec2]:
        """
        Calculates the intersection points for this circle with a ray.

        Args:
            ray: intersection ray
            abs_tol: absolute tolerance for tests (e.g. test for tangents)

        Returns: tuple of Vector()

            tuple contains:
            0 points .. no intersection
            1 point .. ray is a tangent on the circle
            2 points .. ray intersects with the circle

        """
        normal_ray = ray.orthogonal(self.center)
        intersection_point = ray.intersect(normal_ray)
        dist = self.center.distance(intersection_point)
        result = []
        if dist < self.radius:  # intersect in two points
            if math.isclose(dist, 0., abs_tol=abs_tol):  # if ray goes through midpoint
                angle = normal_ray._angle
                alpha = HALF_PI
            else:  # the exact direction of angle (all 4 quadrants Q1-Q4) is important:
                # normal_ray.angle is only at the center point correct
                angle = (intersection_point - self.center).angle
                alpha = math.acos(intersection_point.distance(self.center) / self.radius)
            result.append(self.get_point(angle + alpha))
            result.append(self.get_point(angle - alpha))
        elif math.isclose(dist, self.radius, abs_tol=abs_tol):  # ray is a tangent of circle
            result.append(intersection_point)
            # else no intersection
        return tuple(result)

    def intersect_circle(self, other: 'ConstructionCircle', abs_tol: float = 1e-12) -> Sequence[Vec2]:
        """
        Calculates the intersection points for two circles.

        Args:
            other: intersection circle
            abs_tol: absolute tolerance for tests (e.g. test for circle touch point)

        Returns: tuple of Vector()

            tuple contains:
            0 points .. no intersection
            1 point .. circle touches the other_circle in one point
            2 points .. circle intersects with the other_circle

        """

        def get_angle_through_center_points():
            return (other.center - self.center).angle

        radius1 = self.radius
        radius2 = other.radius
        dist = self.center.distance(other.center)
        max_dist = radius1 + radius2
        min_dist = math.fabs(radius1 - radius2)
        result = []
        if min_dist <= dist <= max_dist:
            if math.isclose(dist, max_dist, abs_tol=abs_tol) or math.isclose(dist, min_dist,
                                                                             abs_tol=abs_tol):  # circles touches in one point
                angle = get_angle_through_center_points()
                result.append(self.get_point(angle))
            else:  # circles intersect in two points
                alpha = math.acos((radius2 ** 2 - radius1 ** 2 - dist ** 2) / (-2. * radius1 * dist))  # 'Cosinus-Satz'
                angle = get_angle_through_center_points()
                result.append(self.get_point(angle + alpha))
                result.append(self.get_point(angle - alpha))
        return tuple(result)
