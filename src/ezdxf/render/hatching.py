#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterator, Tuple, Sequence, List
import math
import dataclasses
from ezdxf.math import Vec2

MIN_HATCH_LINE_DISTANCE = 1e-4  # ??? what's a good choice


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


@dataclasses.dataclass
class Line:
    start: Vec2
    end: Vec2
    distance: float


class HatchLine:
    def __init__(self, origin: Vec2, direction: Vec2, distance: float):
        self.origin = origin
        self.direction = direction
        self.distance = distance

    def intersect_triangle_side(
        self,
        a: Vec2,
        b: Vec2,
        dist_a: float,
        dist_b: float,
        intersection_points: List[Vec2],
    ):
        # all distances are normal distances to the hatch baseline
        line_distance = self.distance
        if math.isclose(dist_a, line_distance):
            if math.isclose(dist_b, line_distance):
                # Hatch line is collinear to line a,b - not a common case,
                # no need for optimization!
                # intersection_points may contain a and/or b already as end
                # points of the two other triangle lines:
                intersection_points.clear()
                intersection_points.append(a)
                intersection_points.append(b)
            else:  # hatch line passes only corner point a
                intersection_points.append(a)
        elif math.isclose(dist_b, line_distance):
            intersection_points.append(b)  # hatch line passes corner point b
        elif dist_a > line_distance > dist_b:
            # points a,b on opposite sides of the hatch line
            factor = abs(dist_a - line_distance) / (dist_a - dist_b)
            intersection_points.append(a.lerp(b, factor))
        elif dist_a < line_distance < dist_b:
            # points a,b on opposite sides of the hatch line
            factor = abs(line_distance - dist_a) / (dist_b - dist_a)
            intersection_points.append(a.lerp(b, factor))


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

    def hatch_lines_intersecting_triangle(
        self, triangle: Sequence[Vec2]
    ) -> Iterator[Line]:
        """Returns all hatch lines intersecting the triangle (a, b, c)."""
        a, b, c = triangle
        if a.isclose(b) or b.isclose(c) or a.isclose(c):
            return  # invalid triangle

        point_distances = self.signed_point_distances(a, b, c)

        dist_a, dist_b, dist_c = point_distances
        points: List[Vec2] = []
        for hatch_line_distance in hatch_line_distances(
            point_distances, self.normal_distance
        ):
            points.clear()
            hatch_line = self.hatch_line(hatch_line_distance)
            hatch_line.intersect_triangle_side(a, b, dist_a, dist_b, points)
            if len(points) == 2:
                yield Line(points[0], points[1], hatch_line_distance)
                continue
            hatch_line.intersect_triangle_side(b, c, dist_b, dist_c, points)
            if len(points) == 2:
                p0, p1 = points
                if not p0.isclose(p1):  # not a corner point
                    yield Line(p0, p1, hatch_line_distance)
                    continue
            hatch_line.intersect_triangle_side(c, a, dist_c, dist_a, points)
            if len(points) == 3:
                # one intersection point is duplicated as corner point
                if points[0].isclose(points[1]):
                    yield Line(points[0], points[2], hatch_line_distance)
                else:
                    yield Line(points[0], points[1], hatch_line_distance)
            elif len(points) == 2 and not points[0].isclose(points[1]):
                yield Line(points[0], points[1], hatch_line_distance)

    def hatch_line(self, distance: float) -> HatchLine:
        """Returns the hatch line at the given signed `distance`."""
        factor = distance / self.normal_distance
        return HatchLine(
            self.origin + self.offset * factor, self.direction, distance
        )

    def signed_point_distances(
        self, a: Vec2, b: Vec2, c: Vec2
    ) -> Tuple[float, float, float]:
        """Returns the signed normal distances of the given points a, b and c to
        the hatch baseline.
        """

        def signed_distance(point: Vec2) -> float:
            # denominator (base_end - base_start).magnitude is 1.0 !!!
            return (base_start - point).det(base_end - point)

        base_start = self.origin
        base_end = base_start + self.direction
        return signed_distance(a), signed_distance(b), signed_distance(c)


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
