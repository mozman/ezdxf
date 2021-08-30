# Copyright (c) 2010-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Sequence
import math
from ezdxf.math import Vec2
from .line import ConstructionRay
from .bbox import BoundingBox2d

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

HALF_PI = math.pi / 2.0

__all__ = ["ConstructionCircle"]


class ConstructionCircle:
    """Circle construction tool.

    Args:
        center: center point as :class:`Vec2` compatible object
        radius: circle radius > `0`

    """

    def __init__(self, center: "Vertex", radius: float = 1.0):
        self.center = Vec2(center)
        self.radius = float(radius)
        if self.radius <= 0.0:
            raise ValueError("Radius has to be > 0.")

    def __str__(self) -> str:
        """Returns string representation of circle
        "ConstructionCircle(center, radius)".
        """
        return f"ConstructionCircle({self.center}, {self.radius})"

    @staticmethod
    def from_3p(
        p1: "Vertex", p2: "Vertex", p3: "Vertex"
    ) -> "ConstructionCircle":
        """Creates a circle from three points, all points have to be compatible
        to :class:`Vec2` class.
        """
        _p1 = Vec2(p1)
        _p2 = Vec2(p2)
        _p3 = Vec2(p3)
        ray1 = ConstructionRay(_p1, _p2)
        ray2 = ConstructionRay(_p1, _p3)
        center_ray1 = ray1.orthogonal(_p1.lerp(_p2))
        center_ray2 = ray2.orthogonal(_p1.lerp(_p3))
        center = center_ray1.intersect(center_ray2)
        return ConstructionCircle(center, center.distance(_p1))

    @property
    def bounding_box(self) -> "BoundingBox2d":
        """2D bounding box of circle as  :class:`BoundingBox2d` object."""
        rvec = Vec2((self.radius, self.radius))
        return BoundingBox2d((self.center - rvec, self.center + rvec))

    def translate(self, dx: float, dy: float) -> None:
        """Move circle about `dx` in x-axis and about `dy` in y-axis.

        Args:
            dx: translation in x-axis
            dy: translation in y-axis

        """
        self.center += Vec2((dx, dy))

    def point_at(self, angle: float) -> Vec2:
        """Returns point on circle at `angle` as :class:`Vec2` object.

        Args:
            angle: angle in radians

        """
        return self.center + Vec2.from_angle(angle, self.radius)

    def inside(self, point: "Vertex") -> bool:
        """Returns ``True`` if `point` is inside circle."""
        return self.radius >= self.center.distance(Vec2(point))

    def tangent(self, angle: float) -> ConstructionRay:
        """Returns tangent to circle at `angle` as :class:`ConstructionRay`
        object.

        Args:
            angle: angle in radians

        """
        point_on_circle = self.point_at(angle)
        ray = ConstructionRay(self.center, point_on_circle)
        return ray.orthogonal(point_on_circle)

    def intersect_ray(
        self, ray: ConstructionRay, abs_tol: float = 1e-10
    ) -> Sequence[Vec2]:
        """Returns intersection points of circle and `ray` as sequence of
        :class:`Vec2` objects.

        Args:
            ray: intersection ray
            abs_tol: absolute tolerance for tests (e.g. test for tangents)

        Returns:
            tuple of :class:`Vec2` objects

            =========== ==================================
            tuple size  Description
            =========== ==================================
            0           no intersection
            1           ray is a tangent to circle
            2           ray intersects with the circle
            =========== ==================================

        """
        ortho_ray = ray.orthogonal(self.center)
        intersection_point = ray.intersect(ortho_ray)
        dist = self.center.distance(intersection_point)
        result = []
        # Intersect in two points:
        if dist < self.radius:
            # Ray goes through center point:
            if math.isclose(dist, 0.0, abs_tol=abs_tol):
                angle = ortho_ray.angle
                alpha = HALF_PI
            else:
                # The exact direction of angle (all 4 quadrants Q1-Q4) is
                # important: ortho_ray.angle is only correct at the center point
                angle = (intersection_point - self.center).angle
                alpha = math.acos(
                    intersection_point.distance(self.center) / self.radius
                )
            result.append(self.point_at(angle + alpha))
            result.append(self.point_at(angle - alpha))
        # Ray is a tangent of the circle:
        elif math.isclose(dist, self.radius, abs_tol=abs_tol):
            result.append(intersection_point)
        # else: No intersection
        return tuple(result)

    def intersect_circle(
        self, other: "ConstructionCircle", abs_tol: float = 1e-10
    ) -> Sequence[Vec2]:
        """Returns intersection points of two circles as sequence of
        :class:`Vec2` objects.

        Args:
            other: intersection circle
            abs_tol: absolute tolerance for tests

        Returns:
            tuple of :class:`Vec2` objects

            =========== ==================================
            tuple size  Description
            =========== ==================================
            0           no intersection
            1           circle touches the `other` circle at one point
            2           circle intersects with the `other` circle
            =========== ==================================

        """
        r1 = self.radius
        r2 = other.radius
        d = self.center.distance(other.center)
        d_max = r1 + r2
        d_min = math.fabs(r1 - r2)
        result = []
        if d_min <= d <= d_max:
            angle = (other.center - self.center).angle
            # Circles touches at one point:
            if math.isclose(d, d_max, abs_tol=abs_tol) or math.isclose(
                d, d_min, abs_tol=abs_tol
            ):
                result.append(self.point_at(angle))
            else:  # Circles intersect in two points:
                # Law of Cosines:
                alpha = math.acos(
                    (r2 ** 2 - r1 ** 2 - d ** 2) / (-2.0 * r1 * d)
                )
                result.append(self.point_at(angle + alpha))
                result.append(self.point_at(angle - alpha))
        return tuple(result)
