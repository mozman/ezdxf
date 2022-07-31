#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterator, Sequence, List, Tuple, Dict
from collections import defaultdict
import enum
import math
import dataclasses
from ezdxf.math import Vec2

MIN_HATCH_LINE_DISTANCE = 1e-4  # ??? what's a good choice
NONE_VEC2 = Vec2(math.nan, math.nan)
NDIGITS = 4


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

    def signed_distance(self, point: Vec2) -> float:
        """Returns the signed normal distance of the given point to the hatch
        baseline.
        """
        # denominator (_end - origin).magnitude is 1.0 !!!
        return (self.origin - point).det(self._end - point)


def hatch_line_distances(
    point_distances: Sequence[float], normal_distance: float
) -> Iterator[float]:
    """Yields all hatch line distances in the range of the given points
    distances. (All hatch lines which do intersect the triangle)
    """
    assert normal_distance != 0.0
    line_numbers = [d / normal_distance for d in point_distances]
    max_line_number = int(math.ceil(max(line_numbers)))
    min_line_number = int(math.ceil(min(line_numbers)))
    for num in range(min_line_number, max_line_number):
        yield normal_distance * num


def hatch_triangle(
    baseline: HatchBaseLine, triangle: Sequence[Vec2]
) -> Iterator[Line]:
    """Returns all hatch lines intersecting the triangle (a, b, c)."""
    a, b, c = triangle
    if a.isclose(b) or b.isclose(c) or a.isclose(c):
        return  # invalid triangle

    dist_a = baseline.signed_distance(a)
    dist_b = baseline.signed_distance(b)
    dist_c = baseline.signed_distance(c)
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
        (dist_a, dist_b, dist_c), baseline.normal_distance
    ):
        points.clear()
        hatch_line = baseline.hatch_line(hatch_line_distance)
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


def intersect_polygon(
    baseline: HatchBaseLine, polygon: Sequence[Vec2]
) -> Iterator[Tuple[Intersection, float]]:
    """Yields all intersection points of the hatch defined by the `baseline` and
    the given `polygon`.

    Returns the intersection point and the normal-distance from the baseline,
    intersection points with the same normal-distance lay on the same hatch
    line.

    """
    if len(polygon) < 3:
        return
    if polygon[0].isclose(polygon[-1]):
        polygon = polygon[:-1]
    prev_point = polygon[-1]
    dist_prev = baseline.signed_distance(prev_point)

    for point in polygon:
        dist_point = baseline.signed_distance(point)
        for hatch_line_distance in hatch_line_distances(
            (dist_prev, dist_point), baseline.normal_distance
        ):
            hatch_line = baseline.hatch_line(hatch_line_distance)
            ip = hatch_line.intersect_line(
                prev_point, point, dist_prev, dist_point
            )
            if ip.type != IntersectionType.NONE:
                yield ip, hatch_line_distance
        prev_point = point
        dist_prev = dist_point


def hatch_polygons(
    baseline: HatchBaseLine, polygons: Sequence[Sequence[Vec2]]
) -> Iterator[Line]:
    """Returns all hatch lines intersecting the given polygons."""
    points: Dict[float, List[Intersection]] = defaultdict(list)
    for polygon in polygons:
        for ip, distance in intersect_polygon(baseline, polygon):
            assert ip.type != IntersectionType.NONE
            points[round(distance, NDIGITS)].append(ip)
    for distance, vertices in points.items():
        yield from _line_segments(vertices, distance)


def _line_segments(
    vertices: List[Intersection], distance: float
) -> Iterator[Line]:
    if len(vertices) < 2:
        return
    vertices.sort(key=lambda p: p.p0)
    prev_point = vertices[0].p0
    inside = True
    for ip in vertices[1:]:
        point = ip.p0
        if prev_point.isclose(point):
            continue
        if inside:
            yield Line(prev_point, point, distance)
        if ip.type == IntersectionType.COLLINEAR and not ip.p1.isclose(point):
            yield Line(point, ip.p1, distance)
            point = ip.p1
        inside = not inside
        prev_point = point
