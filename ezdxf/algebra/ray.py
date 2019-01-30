# Created: 13.03.2010
# Copyright (c) 2010, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Optional
import math
from .base import equals_almost, normalize_angle, is_vertical_angle
from .vector import Vector

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


class ParallelRaysError(ArithmeticError):
    pass


HALF_PI = math.pi / 2.
THREE_PI_HALF = 1.5 * math.pi
DOUBLE_PI = math.pi * 2.

XCOORD = 0
YCOORD = 1


class ConstructionRay:
    """
    Defines an infinite ray (line with no end points)
    treat it as IMMUTABLE - don't change the status
    possible keyword args: slope, angle as float
    point1, point2 as 2d-tuples

    Case A: point1, point2
    ray goes through point1 and point2, vertical lines are possible
    ignores the keyword arguments slope and angle

    Case B: point1, slope
    ray goes through point1 with slope
    argument point2 have to be None
    vertical lines are not possible because slope can't be infinite.
    ignores the keyword argument angle

    Case C: point1, angle (in radian)
    argument point2 have to be None
    ray goes through point1 with the submitted angle
    vertical lines are possible
    if keyword argument slope is defined, angle will be ignored

    """

    def __init__(self, point1: 'Vertex', point2: 'Vertex' = None, **kwargs):
        self._vertical = False  # type: bool
        self.places = 7  # type: int
        p1x = float(point1[XCOORD])
        p1y = float(point1[YCOORD])
        if point2 is not None:  # case A
            # normalize point order to assure consist signs for slopes
            # +slope goes up and -slope goes down
            self._slope = 0
            self._angle = 0
            p2x = float(point2[XCOORD])
            p2y = float(point2[YCOORD])

            if p1x > p2x:
                p1x, p2x = p2x, p1x
                p1y, p2y = p2y, p1y
            dx = p2x - p1x
            dy = p2y - p1y
            if dx == 0.:  # line is vertical
                self._x = p1x
                self._set_angle(HALF_PI)
            else:
                self._set_slope(dy / dx)
        elif 'slope' in kwargs:  # case B
            self._set_slope(float(kwargs['slope']))
        elif 'angle' in kwargs:  # case C
            self._set_angle(normalize_angle(float(kwargs['angle'])))
            if self.is_vertical:
                self._x = p1x
        if not self.is_vertical:
            # y0 is the y-coordinate of this ray at x-coordinate == 0
            self._y0 = p1y - self.slope * p1x

    @property
    def slope(self) -> float:
        """
        Get slope of the ray.

        """
        return self._slope

    def _set_slope(self, slope):
        self._slope = slope  # type: float
        self._angle = normalize_angle(math.atan(slope))  # type: float

    def __str__(self):
        return 'ConstructionRay(x={0._x:.3f}, y={0._y:.3f}, k={0.slope:.3f}, phi={0.angle:.5f} rad)'.format(self)

    @property
    def angle(self) -> float:
        return self._angle

    def _set_angle(self, angle: float) -> None:
        self._angle = angle
        self._slope = math.tan(angle)
        self._vertical = is_vertical_angle(angle)

    @property
    def is_vertical(self) -> bool:
        return self._vertical

    @property
    def is_horizontal(self) -> bool:
        return equals_almost(self.slope, 0., self.places)

    def is_parallel(self, ray: 'ConstructionRay') -> bool:
        """
        Return True if the rays are parallel, else False.

        """
        if self.is_vertical:
            return ray.is_vertical
        else:
            return equals_almost(self.slope, ray.slope, self.places)

    def intersect(self, other: 'ConstructionRay') -> Vector:
        """
        Returns the intersection point (xy-tuple) of self and other_ray.

        Raises:
             ParallelRaysError: if the rays are parallel

        """
        ray1 = self
        ray2 = other
        if not ray1.is_parallel(ray2):
            if ray1.is_vertical:
                x = ray1._x
                y = ray2.get_y(x)
            elif ray2.is_vertical:
                x = ray2._x
                y = ray1.get_y(x)
            else:
                # calc intersection with the 'straight-line-equation'
                # based on y(x) = y0 + x*slope
                x = (ray1._y0 - ray2._y0) / (ray2.slope - ray1.slope)
                y = ray1.get_y(x)
            return Vector(x, y)
        else:
            raise ParallelRaysError("no intersection, rays are parallel")

    def normal_through(self, point: 'Vertex') -> 'ConstructionRay':
        """
        Returns a ray which is normal to self and goes through point.

        """
        return ConstructionRay(point, angle=self.angle + HALF_PI)

    def goes_through(self, point: 'Vertex') -> bool:
        """
        Returns True if ray goes through point, else False.

        """
        if self.is_vertical:
            return equals_almost(point[XCOORD], self._x, self.places)
        else:
            return equals_almost(point[YCOORD], self.get_y(point[XCOORD]),
                                 self.places)

    def get_y(self, x: float) -> float:
        """
        Get y-coordinate by x-coordinate, raises ArithmeticError for vertical lines.

        """
        if self.is_vertical:
            raise ArithmeticError
        return self._y0 + float(x) * self.slope

    def get_x(self, y: float) -> float:
        """
        Get x-coordinate by y-coordinate, raises ArithmeticError for horizontal lines.

        """
        if self.is_vertical:
            return self._x
        else:
            if self.is_horizontal:
                raise ArithmeticError
            return (float(y) - self._y0) / self.slope

    def bisectrix(self, other_ray: 'ConstructionRay') -> 'ConstructionRay':
        """
        Bisectrix between self and other_ray.

        """
        if self.is_parallel(other_ray):
            raise ParallelRaysError
        cross_point = self.intersect(other_ray)
        alpha = (self.angle + other_ray.angle) / 2.0
        return ConstructionRay(cross_point, angle=alpha)


class ConstructionLine:
    """
    ConstructionLine is similar to ConstructionRay, but has a start and endpoint and therefor also an direction.
    The direction goes from start to end, 'left of line' is always in relation to this line direction.

    """
    def __init__(self, start: 'Vertex', end: 'Vertex'):
        self.start = Vector(start)
        self.end = Vector(end)

    def __str__(self):
        return 'ConstructionLine({0.start}, {0.end})'.format(self)

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

    def midpoint(self) -> Vector:
        return self.start.lerp(self.end)

    @property
    def is_vertical(self) -> bool:
        return math.isclose(self.start.x, self.end.x)

    def is_in_coordinate_range(self, point: Vector) -> bool:
        start, end = self.sorted_points
        if not self.is_vertical:
            return start.x <= point.x <= end.x
        else:
            return start.y <= point.y <= end.y

    def intersect(self, other: 'ConstructionLine') -> Optional[Vector]:
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
            if self.is_in_coordinate_range(point) and other.is_in_coordinate_range(point):
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
        point = Vector(point)
        if self.is_vertical:
            # compute on which site of the line self should be
            should_be_left = self.start.y < self.end.y
            if should_be_left:
                return point.x < self.start.x
            else:
                return point.x > self.start.x
        else:
            y = self.ray.get_y(point.x)
            # compute if point should be above or below the line
            should_be_above = start.x < end.x
            if should_be_above:
                return point.y > y
            else:
                return point.y < y
