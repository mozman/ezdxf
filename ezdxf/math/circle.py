# Copyright (c) 2010-2019 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Sequence
import math
from .line import ConstructionRay
from .vector import Vec2
from .bbox import BoundingBox2d
from .construct2d import ConstructionTool

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

HALF_PI = math.pi / 2.


class ConstructionCircle(ConstructionTool):
    def __init__(self, center: 'Vertex', radius: float = 1.0):
        self.center = Vec2(center)
        self.radius = float(radius)
        if self.radius <= 0.:
            raise ValueError("Radius has to be > 0.")

    @staticmethod
    def from_3p(p1: 'Vertex', p2: 'Vertex', p3: 'Vertex') -> 'ConstructionCircle':
        """ Creates a circle from three points. """
        p1 = Vec2(p1)
        p2 = Vec2(p2)
        p3 = Vec2(p3)
        ray1 = ConstructionRay(p1, p2)
        ray2 = ConstructionRay(p1, p3)
        center_ray1 = ray1.orthogonal(p1.lerp(p2))
        center_ray2 = ray2.orthogonal(p1.lerp(p3))
        center = center_ray1.intersect(center_ray2)
        return ConstructionCircle(center, center.distance(p1))

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

    def point_at(self, angle: float) -> Vec2:
        """
        Returns point on circle at `angle` as 2d vector.

        Args:
            angle: angle in radians

        """
        return self.center + Vec2.from_angle(angle, self.radius)

    def inside(self, point: 'Vertex') -> bool:
        """ Test if `point` is inside circle. """
        return self.radius >= self.center.distance(Vec2(point))

    def tangent(self, angle: float) -> ConstructionRay:
        """
        Returns tangent to circle at `angle` as ConstructionRay().

        Args:
            angle: angle in radians

        """
        point_on_circle = self.point_at(angle)
        ray = ConstructionRay(self.center, point_on_circle)
        return ray.orthogonal(point_on_circle)

    def intersect_ray(self, ray: ConstructionRay, abs_tol: float = 1e-12) -> Sequence[Vec2]:
        """
        Returns intersection points for intersection of this circle with `ray` as sequence of 2d points.

        Args:
            ray: intersection ray
            abs_tol: absolute tolerance for tests (e.g. test for tangents)

        Returns: tuple of Vec2()

            tuple contains:
            0 points .. no intersection
            1 point .. ray is a tangent on the circle
            2 points .. ray intersects with the circle

        """
        ortho_ray = ray.orthogonal(self.center)
        intersection_point = ray.intersect(ortho_ray)
        dist = self.center.distance(intersection_point)
        result = []
        if dist < self.radius:  # intersect in two points
            if math.isclose(dist, 0., abs_tol=abs_tol):  # if ray goes through center point
                angle = ortho_ray.angle
                alpha = HALF_PI
            else:
                # the exact direction of angle (all 4 quadrants Q1-Q4) is important:
                # ortho_ray.angle is only at the center point correct
                angle = (intersection_point - self.center).angle
                alpha = math.acos(intersection_point.distance(self.center) / self.radius)
            result.append(self.point_at(angle + alpha))
            result.append(self.point_at(angle - alpha))
        elif math.isclose(dist, self.radius, abs_tol=abs_tol):  # ray is a tangent of circle
            result.append(intersection_point)
        # else no intersection
        return tuple(result)

    def intersect_circle(self, other: 'ConstructionCircle', abs_tol: float = 1e-12) -> Sequence[Vec2]:
        """
        Returns intersection points of two circles as sequence of 2d points.

        Args:
            other: intersection circle
            abs_tol: absolute tolerance for tests (e.g. test for circle touch point)

        Returns: tuple of Vec2()

            tuple contains:
            0 points .. no intersection
            1 point .. circle touches the other_circle in one point
            2 points .. circle intersects with the other_circle

        """
        r1 = self.radius
        r2 = other.radius
        d = self.center.distance(other.center)
        d_max = r1 + r2
        d_min = math.fabs(r1 - r2)
        result = []
        if d_min <= d <= d_max:
            angle = (other.center - self.center).angle
            # if circles touches in one point
            if math.isclose(d, d_max, abs_tol=abs_tol) or math.isclose(d, d_min, abs_tol=abs_tol):
                result.append(self.point_at(angle))
            else:  # circles intersect in two points
                alpha = math.acos((r2 ** 2 - r1 ** 2 - d ** 2) / (-2. * r1 * d))  # 'Cosinus-Satz'
                result.append(self.point_at(angle + alpha))
                result.append(self.point_at(angle - alpha))
        return tuple(result)
