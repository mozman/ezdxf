#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterator, Sequence, List, Tuple, Dict, TYPE_CHECKING
from collections import defaultdict
import enum
import math
import dataclasses
from ezdxf.math import Vec2, AnyVec


if TYPE_CHECKING:
    from ezdxf.path import Path
    from ezdxf.entities.polygon import DXFPolygon

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
    if distance > 0.0:
        return +1
    elif distance < 0.0:
        return -1
    return 0


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
                return Intersection(IntersectionType.START, a)
        elif side_b == 0:
            return Intersection(IntersectionType.END, b)
        elif side_a != side_b:
            factor = abs((dist_a - line_distance) / (dist_a - dist_b))
            return Intersection(IntersectionType.REGULAR, a.lerp(b, factor))
        return Intersection()  # no intersection


class PatternRenderer:
    """
    A hatch pattern has one or more hatch baselines with an origin,
    direction, offset and line pattern.
    The origin is the starting point of the hatch line and also the starting
    point of the line pattern. The offset defines the origin of the adjacent
    hatch line and doesn't have to be orthogonal to the hatch line direction.

    Line pattern is a list of floats, where a value > 0.0 is a dash, a
    value < 0.0 is a gap and value == 0.0 is a point.

    """

    def __init__(self, hatch_line: HatchLine, pattern: Sequence[float]):
        self.origin = hatch_line.origin
        self.direction = hatch_line.direction
        self.pattern = pattern
        self.pattern_length = math.fsum([abs(e) for e in pattern])

    def sequence_origin(self, index: float) -> Vec2:
        return self.origin + self.direction * (self.pattern_length * index)

    def render(self, start: Vec2, end: Vec2) -> Iterator[Tuple[Vec2, Vec2]]:
        if start.isclose(end):
            return
        length = self.pattern_length
        if length < 1e-9:
            yield start, end
            return

        def pattern_offset(index, distance):
            if math.isclose(index * length, distance):
                # fix floating point imprecision:
                # modulo and floor() do not play nice together
                return 0.0
            return distance % length

        direction = self.direction
        if direction.dot(end - start) < 0.0:
            # Line direction is reversed to the pattern line direction!
            start, end = end, start
        origin = self.origin
        s_dist = direction.dot(start - origin)
        e_dist = direction.dot(end - origin)
        s_index = math.floor(s_dist / length)
        s_offset = pattern_offset(s_index, s_dist)
        e_index = math.floor(e_dist / length)
        e_offset = pattern_offset(e_index, e_dist)

        if s_index == e_index:
            yield from self.render_offset_to_offset(s_index, s_offset, e_offset)
            return
        # line crosses pattern border
        if s_offset > 0.0:
            yield from self.render_offset_to_offset(
                s_index,
                s_offset,
                length,
            )
            s_index += 1

        while s_index < e_index:
            yield from self.render_full_pattern(s_index)
            s_index += 1

        if e_offset > 0.0:
            yield from self.render_offset_to_offset(
                s_index,
                0.0,
                e_offset,
            )

    def render_full_pattern(self, index: float) -> Iterator[Tuple[Vec2, Vec2]]:
        # fast pattern rendering
        direction = self.direction
        start_point = self.sequence_origin(index)
        for dash in self.pattern:
            if dash == 0.0:
                yield start_point, start_point
            else:
                end_point = start_point + direction * abs(dash)
                if dash > 0.0:
                    yield start_point, end_point
                start_point = end_point

    def render_offset_to_offset(
        self, index: float, s_offset: float, e_offset: float
    ) -> Iterator[Tuple[Vec2, Vec2]]:
        direction = self.direction
        origin = self.sequence_origin(index)
        start_point = origin + direction * s_offset
        distance = 0.0
        for dash in self.pattern:
            distance += abs(dash)
            if distance < s_offset:
                continue
            if dash == 0.0:
                yield start_point, start_point
            else:
                end_point = origin + direction * min(distance, e_offset)
                if dash > 0.0:
                    yield start_point, end_point
                if distance >= e_offset:
                    return
                start_point = end_point


class HatchBaseLine:
    def __init__(
        self,
        origin: Vec2,
        direction: Vec2,
        offset: Vec2,
        line_pattern: List[float] = None,
    ):
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
        self.line_pattern: List[float] = line_pattern if line_pattern else []

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

    def pattern_renderer(self, distance: float) -> PatternRenderer:
        return PatternRenderer(self.hatch_line(distance), self.line_pattern)


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
        if count < 3:
            return

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
        start = NONE_VEC2
        end = NONE_VEC2
        for line in _line_segments(vertices, distance):
            if start is NONE_VEC2:
                start = line.start
                end = line.end
                continue
            if line.start.isclose(end):
                end = line.end
            else:
                yield Line(start, end, distance)
                start = line.start
                end = line.end

        if start is not NONE_VEC2:
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
        if ip.type == IntersectionType.NONE:
            continue
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
        point = ip.p0
        if prev_point is NONE_VEC2:
            inside = True
            prev_point = point
            continue
        if inside:
            yield Line(prev_point, point, distance)

        inside = not inside
        prev_point = point


def explode_hatch_pattern(
    hatch: DXFPolygon, max_flattening_distance: float
) -> Iterator[Tuple[AnyVec, AnyVec]]:
    if hatch.pattern is None or hatch.dxf.solid_fill:
        return
    if len(hatch.pattern.lines) == 0:
        return
    ocs = hatch.ocs()
    elevation = hatch.dxf.elevation.z
    paths = hatch_paths(hatch)
    polygons = [Vec2.list(p.flattening(max_flattening_distance)) for p in paths]
    # All polygons in OCS!
    for baseline in pattern_baselines(hatch):
        for line in hatch_polygons(baseline, polygons):
            line_pattern = baseline.pattern_renderer(line.distance)
            for s, e in line_pattern.render(line.start, line.end):
                if ocs.transform:
                    yield ocs.to_wcs((s.x, s.y, elevation)), ocs.to_wcs(
                        (e.x, e.y, elevation)
                    )
                yield s, e


def hatch_paths(polygon: DXFPolygon) -> List[Path]:
    from ezdxf.path import from_hatch_boundary_path

    loops = []
    for boundary in polygon.paths.rendering_paths(polygon.dxf.hatch_style):
        path = from_hatch_boundary_path(boundary)
        for sub_path in path.sub_paths():
            if len(sub_path):
                sub_path.close()
                loops.append(sub_path)
    return loops


def pattern_baselines(polygon: DXFPolygon) -> Iterator[HatchBaseLine]:
    pattern = polygon.pattern
    if not pattern:
        return
    # The hatch pattern parameters are already scaled and rotated for direct
    # usage!
    # The stored scale and angle is just for reconstructing the base pattern
    # when applying a new scaling or rotation.
    for line in pattern.lines:
        direction = Vec2.from_deg_angle(line.angle)
        yield HatchBaseLine(
            line.base_point, direction, line.offset, line.dash_length_items
        )
