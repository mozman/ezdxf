#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterator, Sequence, List
import enum
import math
import dataclasses
from ezdxf.math import Vec2

MIN_HATCH_LINE_DISTANCE = 1e-4  # ??? what's a good choice
NONE_VEC2 = Vec2(math.nan, math.nan)


class IntersectionType(enum.IntEnum):
    NONE = 0
    REGULAR = 1
    START = 2
    END = 3
    COLLINEAR = 4


class HatchingError(Exception):
    pass


class HatchLineDirectionError(HatchingError):
    pass


class DenseHatchingLinesError(HatchingError):
    pass


class PatternRenderer:
    """
    A hatch pattern has one or more hatch baselines with an origin,
    direction, offset and line pattern.
    The origin is the starting point of the hatch line and also the starting
    point of the line pattern. The offset defines the origin of the adjacent
    hatch line and doesn't have to be orthogonal to the hatch line direction.
    """

    pass


@dataclasses.dataclass(frozen=True)
class Line:
    start: Vec2
    end: Vec2
    distance: float  # normal distance to the hatch baseline


@dataclasses.dataclass(frozen=True)
class Intersection:
    type: IntersectionType = IntersectionType.NONE
    p0: Vec2 = NONE_VEC2
    p1: Vec2 = NONE_VEC2


@dataclasses.dataclass(frozen=True)
class HatchLine:
    origin: Vec2
    direction: Vec2
    distance: float  # normal distance to the hatch baseline

    def intersect_line(
        self, a: Vec2, b: Vec2, dist_a: float, dist_b: float
    ) -> Intersection:
        # all distances are normal distances to the hatch baseline
        line_distance = self.distance
        if math.isclose(dist_a, line_distance):
            if math.isclose(dist_b, line_distance):
                return Intersection(IntersectionType.COLLINEAR, a, b)
            else:
                return Intersection(IntersectionType.START, a)
        elif math.isclose(dist_b, line_distance):
            return Intersection(IntersectionType.END, b)
        elif dist_a > line_distance > dist_b:
            # points a,b on opposite sides of the hatch line
            factor = abs(dist_a - line_distance) / (dist_a - dist_b)
            return Intersection(IntersectionType.REGULAR, a.lerp(b, factor))
        elif dist_a < line_distance < dist_b:
            # points a,b on opposite sides of the hatch line
            factor = abs(line_distance - dist_a) / (dist_b - dist_a)
            return Intersection(IntersectionType.REGULAR, a.lerp(b, factor))
        return Intersection()


class HatchBaseLine:
    def __init__(self, origin: Vec2, direction: Vec2, offset: Vec2):
        self.origin = origin
        try:
            self.direction = direction.normalize()
        except ZeroDivisionError:
            raise HatchLineDirectionError("hatch line has no direction")
        self.offset = offset
        self.normal_distance: float = (-offset).det(self.direction - offset)
        if abs(self.normal_distance) < MIN_HATCH_LINE_DISTANCE:
            raise DenseHatchingLinesError("hatching lines are too narrow")
        self._end = self.origin + self.direction

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(origin={self.origin!r}, "
            f"direction={self.direction!r}, offset={self.offset!r})"
        )

    def hatch_line(self, distance: float) -> HatchLine:
        """Returns the hatch line at the given signed `distance`."""
        factor = distance / self.normal_distance
        return HatchLine(
            self.origin + self.offset * factor, self.direction, distance
        )

    def signed_point_distance(self, point: Vec2) -> float:
        """Returns the signed normal distance of the given point to the hatch
        baseline.
        """
        # denominator (_end - origin).magnitude is 1.0 !!!
        return (self.origin - point).det(self._end - point)

    def hatch_lines_intersecting_triangle(
        self, triangle: Sequence[Vec2]
    ) -> Iterator[Line]:
        """Returns all hatch lines intersecting the triangle (a, b, c)."""
        a, b, c = triangle
        if a.isclose(b) or b.isclose(c) or a.isclose(c):
            return  # invalid triangle

        dist_a = self.signed_point_distance(a)
        dist_b = self.signed_point_distance(b)
        dist_c = self.signed_point_distance(c)
        points: List[Vec2] = []

        def append_intersection_point(ip: Intersection):
            if ip.type == IntersectionType.COLLINEAR:
                # intersection_points may contain a and/or b already as end
                # points of other triangle lines:
                points.clear()
                points.append(ip.p0)
                points.append(ip.p1)
            elif ip.type:
                points.append(ip.p0)

        for hatch_line_distance in hatch_line_distances(
            (dist_a, dist_b, dist_c), self.normal_distance
        ):
            points.clear()
            hatch_line = self.hatch_line(hatch_line_distance)
            append_intersection_point(
                hatch_line.intersect_line(a, b, dist_a, dist_b)
            )
            if len(points) == 2:
                yield Line(points[0], points[1], hatch_line_distance)
                continue
            append_intersection_point(
                hatch_line.intersect_line(b, c, dist_b, dist_c)
            )
            if len(points) == 2:
                p0, p1 = points
                if not p0.isclose(p1):  # not a corner point
                    yield Line(p0, p1, hatch_line_distance)
                    continue
            append_intersection_point(
                hatch_line.intersect_line(c, a, dist_c, dist_a)
            )
            if len(points) == 3:
                # one intersection point is duplicated as corner point
                if points[0].isclose(points[1]):
                    yield Line(points[0], points[2], hatch_line_distance)
                else:
                    yield Line(points[0], points[1], hatch_line_distance)
            elif len(points) == 2 and not points[0].isclose(points[1]):
                yield Line(points[0], points[1], hatch_line_distance)


def hatch_line_distances(
    point_distances: Sequence[float], normal_distance: float
) -> Iterator[float]:
    """Yields all hatch line distances in the range of the given points
    distances. (All hatch lines which do intersect the triangle)
    """
    line_numbers = [d / normal_distance for d in point_distances]
    hatch_line_distance = math.floor(max(line_numbers)) * normal_distance
    min_hatch_line_distance = math.ceil(min(line_numbers)) * normal_distance
    while hatch_line_distance >= min_hatch_line_distance:
        yield hatch_line_distance
        hatch_line_distance -= normal_distance
