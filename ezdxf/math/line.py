# Created: 13.03.2010
# Copyright (c) 2010, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Optional
import math
from .construct2d import ConstructionTool
from .bbox import BoundingBox2d
from .vector import Vector
from .vec2 import Vec2

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


class ParallelRaysError(ArithmeticError):
    pass


HALF_PI = math.pi / 2.
THREE_PI_HALF = 1.5 * math.pi
DOUBLE_PI = math.pi * 2.


class ConstructionRay:
    """
    Infinite construction ray.

    Args:
        p1: definition point 1
        p2: ray direction as 2nd point or None
        angle: ray direction as angle in radians or None

    """

    def __init__(self, p1: 'Vertex', p2: 'Vertex' = None, angle: float = None):
        self._p1 = Vec2(p1)
        if p2 is not None:
            p2 = Vec2(p2)
            if self._p1.x < p2.x:
                self._direction = (p2 - self._p1).normalize()
            else:
                self._direction = (self._p1 - p2).normalize()
            self._angle = self._direction.angle
        elif angle is not None:
            self._angle = angle
            self._direction = Vec2.from_angle(angle)
        else:
            raise ValueError('p2 or angle required.')

        if math.isclose(self._direction.x, 0., abs_tol=1e-12):
            self._slope = None
            self._yof0 = None
        else:
            self._slope = self._direction.y / self._direction.x
            self._yof0 = self._p1.y - self._slope * self._p1.x
        self._is_vertical = self._slope is None
        self._is_horizontal = math.isclose(self._direction.y, 0., abs_tol=1e-12)

    def __str__(self):
        return 'ConstructionRay(x={0._x:.3f}, y={0._y:.3f}, phi={0.angle:.5f} rad)'.format(self)

    def is_parallel(self, other: 'ConstructionRay') -> bool:
        """
        Return True if the rays are parallel, else False.

        """

        if self._is_vertical:
            return other._is_vertical

        if other._is_vertical:
            return False

        return math.isclose(self._slope, other._slope, abs_tol=1e-12)

    def intersect(self, other: 'ConstructionRay') -> Vec2:
        """
        Returns the intersection point (xy-tuple) of self and other_ray.

        Raises:
             ParallelRaysError: if the rays are parallel

        """
        ray1 = self
        ray2 = other
        if not ray1.is_parallel(ray2):
            if ray1._is_vertical:
                x = self._p1.x
                y = ray2.yof(x)
            elif ray2._is_vertical:
                x = ray2._p1.x
                y = ray1.yof(x)
            else:
                # calc intersection with the 'straight-line-equation'
                # based on y(x) = y0 + x*slope
                x = (ray1._yof0 - ray2._yof0) / (ray2._slope - ray1._slope)
                y = ray1.yof(x)
            return Vec2((x, y))
        else:
            raise ParallelRaysError("Rays are parallel")

    def orthogonal(self, point: 'Vertex') -> 'ConstructionRay':
        """
        Returns orthogonal construction ray through `point`.

        """
        return ConstructionRay(point, angle=self._angle + HALF_PI)

    def yof(self, x: float) -> float:
        if self._is_vertical:
            raise ArithmeticError
        return self._yof0 + float(x) * self._slope

    def xof(self, y: float) -> float:
        if self._is_vertical:
            return self._p1.x
        elif not self._is_horizontal:
            return (float(y) - self._yof0) / self._slope
        else:
            raise ArithmeticError

    def bisectrix(self, other: 'ConstructionRay') -> 'ConstructionRay':
        """
        Bisectrix between self and other construction ray.

        """
        if self.is_parallel(other):
            raise ParallelRaysError
        intersection = self.intersect(other)
        alpha = (self._angle + other._angle) / 2.
        return ConstructionRay(intersection, angle=alpha)


class ConstructionLine(ConstructionTool):
    """
    ConstructionLine is similar to ConstructionRay, but has a start and endpoint and therefor also an direction.
    The direction goes from start to end, 'left of line' is always in relation to this line direction.

    """

    def __init__(self, start: 'Vertex', end: 'Vertex'):
        self.start = Vec2(start)
        self.end = Vec2(end)

    def __str__(self):
        return 'ConstructionLine({0.start}, {0.end})'.format(self)

    # ConstructionTool interface
    @property
    def bounding_box(self):
        return BoundingBox2d(self.start, self.end)

    def move(self, dx: float, dy: float) -> None:
        """
        Move line about `dx` in x-axis and about `dy` in y-axis.

        Args:
            dx: translation in x-axis
            dy: translation in y-axis

        """
        v = Vec2((dx, dy))
        self.start += v
        self.end += v

    @property
    def sorted_points(self):
        return (self.end, self.start) if self.start > self.end else (self.start, self.end)

    @property
    def ray(self):
        return ConstructionRay(self.start, self.end)

    def __eq__(self, other: 'ConstructionLine') -> bool:
        return self.sorted_points == other.sorted_points

    def __lt__(self, other: 'ConstructionLine') -> bool:
        return self.sorted_points < other.sorted_points

    def length(self) -> float:
        return (self.end - self.start).magnitude

    def midpoint(self) -> Vec2:
        return self.start.lerp(self.end)

    @property
    def is_vertical(self) -> bool:
        return math.isclose(self.start.x, self.end.x)

    def inside_bounding_box(self, point: 'Vertex') -> bool:
        return self.bounding_box.inside(point)

    def intersect(self, other: 'ConstructionLine') -> Optional[Vec2]:
        """
        Returns the intersection point of to lines or None if they have no intersection point.

        Args:
            other: other construction line

        Returns: intersection point or None

        """
        try:
            point = self.ray.intersect(other.ray)
        except ParallelRaysError:
            return None
        else:
            if self.inside_bounding_box(point) and other.inside_bounding_box(point):
                return point
            else:
                return None

    def has_intersection(self, other: 'ConstructionLine') -> bool:
        # required because intersection Vector(0, 0, 0) is also False
        return self.intersect(other) is not None

    def left_of_line(self, point: 'Vertex') -> bool:
        """
        True if `point` is left of construction line in relation to the line direction from start to end.

        Points exact at the line are not left of the line.

        """
        start, end = self.start, self.end
        point = Vec2(point)
        if self.is_vertical:
            # compute on which site of the line self should be
            should_be_left = self.start.y < self.end.y
            if should_be_left:
                return point.x < self.start.x
            else:
                return point.x > self.start.x
        else:
            y = self.ray.yof(point.x)
            # compute if point should be above or below the line
            should_be_above = start.x < end.x
            if should_be_above:
                return point.y > y
            else:
                return point.y < y
