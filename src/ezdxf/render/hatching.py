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
    COLLINEAR = 2


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


def side_of_line(distance: float) -> int:
    if abs(distance) < 1e-9:
        return 0
    if distance > 0.0:
        return +1
    return -1


@dataclasses.dataclass(frozen=True)
class HatchLine:
    origin: Vec2
    direction: Vec2
    distance: float  # normal distance to the hatch baseline

    def intersect_line(
        self,
        a: Vec2,
        b: Vec2,
        dist_a: float,
        dist_b: float,
    ) -> Intersection:
        """Returns the intersection of this hatch line with the line (a, b).
        The arguments `dist_a` and `dist_b` are the normal distances of the
        points a,b from the hatch baseline.
        """
        # all distances are normal distances to the hatch baseline
        line_distance = self.distance
        side_a = side_of_line(dist_a - line_distance)
        side_b = side_of_line(dist_b - line_distance)
        if side_a == 0:
            if side_b == 0:
                return Intersection(IntersectionType.COLLINEAR, a, b)
            else:
                return Intersection(IntersectionType.REGULAR, a)
        elif side_b == 0:
            return Intersection(IntersectionType.REGULAR, b)
        elif side_a != side_b:
            factor = abs((dist_a - line_distance) / (dist_a - dist_b))
            return Intersection(IntersectionType.REGULAR, a.lerp(b, factor))
        return Intersection()  # no intersection


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
) -> List[float]:
    """Returns all hatch line distances in the range of the given point
    distances.
    """
    assert normal_distance != 0.0
    normal_factors = [d / normal_distance for d in point_distances]
    max_line_number = int(math.ceil(max(normal_factors)))
    min_line_number = int(math.ceil(min(normal_factors)))
    return [
        normal_distance * num for num in range(min_line_number, max_line_number)
    ]


def intersect_polygon(
    baseline: HatchBaseLine, polygon: Sequence[Vec2]
) -> Iterator[Tuple[Intersection, float]]:
    """Yields all intersection points of the hatch defined by the `baseline` and
    the given `polygon`.

    Returns the intersection point and the normal-distance from the baseline,
    intersection points with the same normal-distance lay on the same hatch
    line.

    """
    count = len(polygon)
    if count < 3:
        return
    if polygon[0].isclose(polygon[-1]):
        count -= 1

    prev_point = polygon[count - 1]  # last point
    dist_prev = baseline.signed_distance(prev_point)
    for index in range(count):
        point = polygon[index]
        dist_point = baseline.signed_distance(point)
        for hatch_line_distance in hatch_line_distances(
            (dist_prev, dist_point), baseline.normal_distance
        ):
            hatch_line = baseline.hatch_line(hatch_line_distance)
            ip = hatch_line.intersect_line(
                prev_point,
                point,
                dist_prev,
                dist_point,
            )
            if (
                ip.type != IntersectionType.NONE
                and ip.type != IntersectionType.COLLINEAR
            ):
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
        start = None
        end = None
        for line in _line_segments(vertices, distance):
            if start is None:
                start = line.start
                end = line.end
                continue
            if line.start.isclose(end):
                end = line.end
            else:
                yield Line(start, end, distance)
                start = line.start
                end = line.end

        if start is not None:
            yield Line(start, end, distance)


def _line_segments(
    vertices: List[Intersection], distance: float
) -> Iterator[Line]:
    if len(vertices) < 2:
        return
    vertices.sort(key=lambda p: p.p0)
    inside = False
    prev_point = NONE_VEC2
    for ip in vertices:
        if ip.type == IntersectionType.COLLINEAR:
            if not inside:
                if not ip.p0.isclose(ip.p1):
                    yield Line(ip.p0, ip.p1, distance)
                inside = True
                prev_point = ip.p1
            else:
                inside = False
                prev_point = ip.p1
            continue

        if ip.type == IntersectionType.NONE:
            continue
        point = ip.p0

        if prev_point is NONE_VEC2:
            inside = True
            prev_point = point
            continue

        if inside:
            yield Line(prev_point, point, distance)

        inside = not inside
        prev_point = point
