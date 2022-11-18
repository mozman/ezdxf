#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Sequence, Optional, Iterator, Union, Callable
from typing_extensions import Protocol
from ezdxf.math import (
    Vec2,
    UVec,
    intersection_line_line_2d,
    is_point_in_polygon_2d,
    has_clockwise_orientation,
    TOLERANCE,
    BoundingBox2d,
)
import enum

__all__ = [
    "greiner_hormann_union",
    "greiner_hormann_difference",
    "greiner_hormann_intersection",
    "cohen_sutherland_line_clipping_2d",
    "Clipping",
    "ClippingPolygon2d",
    "ClippingRect2d",
]


class Clipping(Protocol):
    def clip_polygon(self, polygon: Iterable[Vec2]) -> Sequence[Vec2]:
        """Returns the clipped polygon."""
        ...

    def clip_polyline(
        self, polyline: Iterable[Vec2]
    ) -> Sequence[Sequence[Vec2]]:
        """Returns the parts of the clipped polyline."""
        ...

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[Vec2]:
        """Returns the clipped line."""
        ...

    def is_inside(self, point: Vec2) -> bool:
        """Returns ``True`` if `point is inside the clipping path."""
        ...


def _clip_polyline(
    polyline: Iterable[Vec2],
    line_clipper: Callable[[Vec2, Vec2], Sequence[Vec2]],
) -> Sequence[Sequence[Vec2]]:
    """Returns the parts of the clipped polyline."""
    vertices = list(polyline)
    if len(vertices) < 2:
        return []
    result: list[Vec2] = []
    parts: list[list[Vec2]] = []
    start = vertices[0]
    for end in vertices[1:]:
        clipped_line = line_clipper(start, end)
        start = end
        if len(clipped_line) == 2:
            if result:
                clip_start, clip_end = clipped_line
                if result[-1].isclose(clip_start):
                    result.append(clip_end)
                    continue
                parts.append(result)
            result = list(clipped_line)
    if result:
        parts.append(result)
    return parts


class ClippingPolygon2d:
    """The clipping path is an arbitrary polygon.

    .. versionadded: 0.18.1

    """

    def __init__(self, vertices: Iterable[Vec2], ccw_check=True):
        clip = list(vertices)
        if len(clip) > 1:
            if clip[0].isclose(clip[-1]):
                clip.pop()
        if len(clip) < 3:
            raise ValueError(
                "more than 3 vertices as clipping polygon required"
            )
        if ccw_check and has_clockwise_orientation(clip):
            clip.reverse()
        self._clipping_polygon: list[Vec2] = clip

    def clip_polyline(
        self, polyline: Iterable[Vec2]
    ) -> Sequence[Sequence[Vec2]]:
        """Returns the parts of the clipped polyline."""
        return _clip_polyline(polyline, self.clip_line)

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[Vec2]:
        """Returns the clipped line."""

        def is_inside(point: Vec2) -> bool:
            # is point left of line:
            return (clip_end.x - clip_start.x) * (point.y - clip_start.y) - (
                clip_end.y - clip_start.y
            ) * (point.x - clip_start.x) >= 0.0

        def edge_intersection() -> Vec2:
            return intersection_line_line_2d(
                (edge_start, edge_end), (clip_start, clip_end)
            )

        # The clipping polygon is always treated as a closed polyline!
        clip_start = self._clipping_polygon[-1]
        edge_start = start
        edge_end = end
        for clip_end in self._clipping_polygon:
            if is_inside(edge_start):
                if not is_inside(edge_end):
                    edge_end = edge_intersection()
            elif is_inside(edge_end):
                if not is_inside(edge_start):
                    edge_start = edge_intersection()
            else:
                return tuple()
            clip_start = clip_end
        return edge_start, edge_end

    def clip_polygon(self, polygon: Iterable[Vec2]) -> Sequence[Vec2]:
        """Returns the clipped polygon."""

        def is_inside(point: Vec2) -> bool:
            # is point left of line:
            return (clip_end.x - clip_start.x) * (point.y - clip_start.y) - (
                clip_end.y - clip_start.y
            ) * (point.x - clip_start.x) > 0.0

        def edge_intersection() -> Vec2:
            return intersection_line_line_2d(
                (edge_start, edge_end), (clip_start, clip_end)
            )

        # The clipping polygon is always treated as a closed polyline!
        clip_start = self._clipping_polygon[-1]
        clipped = list(polygon)
        for clip_end in self._clipping_polygon:
            # next clipping edge to test: clip_start -> clip_end
            if not clipped:  # no subject vertices left to test
                break

            vertices = clipped.copy()
            if len(vertices) > 1 and vertices[0].isclose(vertices[-1]):
                vertices.pop()

            clipped.clear()
            edge_start = vertices[-1]
            for edge_end in vertices:
                # next polygon edge to test: edge_start -> edge_end
                if is_inside(edge_end):
                    if not is_inside(edge_start):
                        clipped.append(edge_intersection())
                    clipped.append(edge_end)
                elif is_inside(edge_start):
                    clipped.append(edge_intersection())
                edge_start = edge_end
            clip_start = clip_end
        return clipped

    def is_inside(self, point: Vec2) -> bool:
        """Returns ``True`` if `point` is inside the clipping polygon."""
        return is_point_in_polygon_2d(point, self._clipping_polygon) >= 0


class ClippingRect2d:
    """The clipping path is a rectangle parallel to the x- and y-axis.

    This class will get an optimized implementation in the future.

    .. versionadded: 0.18.1

    """

    def __init__(self, bottom_left: Vec2, top_right: Vec2):
        self._bbox = BoundingBox2d((bottom_left, top_right))
        bottom_left = self._bbox.extmin
        top_right = self._bbox.extmax
        self._clipping_polygon = ClippingPolygon2d(
            [
                bottom_left,
                Vec2(top_right.x, bottom_left.y),
                top_right,
                Vec2(bottom_left.x, top_right.y),
            ],
            ccw_check=False,
        )

    def clip_polygon(self, polygon: Iterable[Vec2]) -> Sequence[Vec2]:
        """Returns the clipped polygon."""
        return self._clipping_polygon.clip_polygon(polygon)

    def clip_polyline(
        self, polyline: Iterable[Vec2]
    ) -> Sequence[Sequence[Vec2]]:
        """Returns the parts of the clipped polyline."""
        return _clip_polyline(polyline, self.clip_line)

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[Vec2]:
        """Returns the clipped line."""
        return cohen_sutherland_line_clipping_2d(
            self._bbox.extmin, self._bbox.extmax, start, end
        )

    def is_inside(self, point: Vec2) -> bool:
        """Returns ``True`` if `point` is inside the clipping rectangle."""
        return self._bbox.inside(point)


def clip_polygon_2d(
    clip: Iterable[UVec],
    subject: Iterable[UVec],
    ccw_check: bool = True,
) -> Sequence[Vec2]:
    """Clip the `subject` polygon by the **convex** clipping polygon `clip`.

    Implements the `Sutherland–Hodgman`_ algorithm for clipping polygons.

    Args:
        clip: the convex clipping polygon as iterable of vertices
        subject: the polygon to clip as an iterable of vertices
        ccw_check: check if the clipping polygon is in counter-clockwise
            orientation if ``True``, set to ``False`` if the ccw check is done
            by the caller

    Returns:
        the clipped subject as list of :class:`~ezdxf.math.Vec2`

    .. versionadded:: 0.16

    .. _Sutherland–Hodgman: https://de.wikipedia.org/wiki/Algorithmus_von_Sutherland-Hodgman

    """
    clipper = ClippingPolygon2d(Vec2.generate(clip), ccw_check)
    return clipper.clip_polygon(Vec2.generate(subject))


# Based on the paper "Efficient Clipping of Arbitrary Polygons" by
# Günther Greiner and Kai Hormann,
# ACM Transactions on Graphics 1998;17(2):71-83
# Available at: http://www.inf.usi.ch/hormann/papers/Greiner.1998.ECO.pdf


class _Node:
    def __init__(
        self,
        vtx: Union[Vec2, _Node],
        alpha: float = 0.0,
        intersect=False,
        entry=True,
        checked=False,
    ):
        self.vtx: Vec2
        if isinstance(vtx, _Node):
            self.vtx = vtx.vtx
        else:
            self.vtx = vtx

        # Reference to the next vertex of the polygon
        self.next: _Node = None  # type: ignore

        # Reference to the previous vertex of the polygon
        self.prev: _Node = None  # type: ignore

        # Reference to the corresponding intersection vertex in the other polygon
        self.neighbour: _Node = None  # type: ignore

        # True if intersection is an entry point, False if exit
        self.entry: bool = entry

        # Intersection point's relative distance from previous vertex
        self.alpha: float = alpha

        # True if vertex is an intersection
        self.intersect: bool = intersect

        # True if the vertex has been checked (last phase)
        self.checked: bool = checked

    def set_checked(self):
        self.checked = True
        if self.neighbour and not self.neighbour.checked:
            self.neighbour.set_checked()


class IntersectionError(Exception):
    pass


class GHPolygon:
    first: _Node = None  # type: ignore
    max_x: float = 1e6

    def add(self, node: _Node):
        """Add a polygon vertex node."""

        self.max_x = max(self.max_x, node.vtx.x)
        if self.first is None:
            self.first = node
            self.first.next = node
            self.first.prev = node
        else:  # insert as last node
            first = self.first
            last = first.prev
            first.prev = node
            node.next = first
            node.prev = last
            last.next = node

    @staticmethod
    def build(vertices: Iterable[UVec]) -> GHPolygon:
        """Build a new GHPolygon from an iterable of vertices."""
        polygon = GHPolygon()
        _vertices = Vec2.list(vertices)
        for v in _vertices:
            polygon.add(_Node(v))
        return polygon

    @staticmethod
    def insert(vertex: _Node, start: _Node, end: _Node):
        """Insert and sort an intersection node.

        This function inserts an intersection node between two other
        start- and end node of an edge. The start and end node cannot be
        an intersection node (that is, they must be actual vertex nodes of
        the original polygon). If there are multiple intersection nodes
        between the start- and end node, then the new node is inserted
        based on its alpha value.
        """
        curr = start
        while curr != end and curr.alpha < vertex.alpha:
            curr = curr.next

        vertex.next = curr
        prev = curr.prev
        vertex.prev = prev
        prev.next = vertex
        curr.prev = vertex

    def __iter__(self) -> Iterator[_Node]:
        assert self.first is not None
        s = self.first
        while True:
            yield s
            s = s.next
            if s is self.first:
                return

    @property
    def first_intersect(self) -> Optional[_Node]:
        for v in self:
            if v.intersect and not v.checked:
                return v
        return None

    @property
    def points(self) -> list[Vec2]:
        points = [v.vtx for v in self]
        if not points[0].isclose(points[-1]):
            points.append(points[0])
        return points

    def unprocessed(self):
        for v in self:
            if v.intersect and not v.checked:
                return True
        return False

    def union(self, clip: GHPolygon) -> list[list[Vec2]]:
        return self.clip(clip, False, False)

    def intersection(self, clip: GHPolygon) -> list[list[Vec2]]:
        return self.clip(clip, True, True)

    def difference(self, clip: GHPolygon) -> list[list[Vec2]]:
        return self.clip(clip, False, True)

    def clip(self, clip: GHPolygon, s_entry, c_entry) -> list[list[Vec2]]:
        """Clip this polygon using another one as a clipper.

        This is where the algorithm is executed. It allows you to make
        a UNION, INTERSECT or DIFFERENCE operation between two polygons.

        Given two polygons A, B the following operations may be performed:

        A|B ... A OR B  (Union of A and B)
        A&B ... A AND B (Intersection of A and B)
        A\\B ... A - B
        B\\A ... B - A

        The entry records store the direction the algorithm should take when
        it arrives at that entry point in an intersection. Depending on the
        operation requested, the direction is set as follows for entry points
        (f=forward, b=backward; exit points are always set to the opposite):

              Entry
              A   B
              -----
        A|B   b   b
        A&B   f   f
        A\\B  b   f
        B\\A  f   b

        f = True, b = False when stored in the entry record
        """
        # Phase 1: Find intersections
        for subject_vertex in self:
            if not subject_vertex.intersect:
                for clipper_vertex in clip:
                    if not clipper_vertex.intersect:
                        ip, us, uc = line_intersection(
                            subject_vertex.vtx,
                            next_vertex_node(subject_vertex.next).vtx,
                            clipper_vertex.vtx,
                            next_vertex_node(clipper_vertex.next).vtx,
                        )
                        if ip is None:
                            continue
                        subject_node = _Node(
                            ip, us, intersect=True, entry=False
                        )
                        clipper_node = _Node(
                            ip, uc, intersect=True, entry=False
                        )
                        subject_node.neighbour = clipper_node
                        clipper_node.neighbour = subject_node

                        self.insert(
                            subject_node,
                            subject_vertex,
                            next_vertex_node(subject_vertex.next),
                        )
                        clip.insert(
                            clipper_node,
                            clipper_vertex,
                            next_vertex_node(clipper_vertex.next),
                        )

        # Phase 2: Identify entry/exit points
        s_entry ^= is_inside_polygon(self.first.vtx, clip)
        for subject_vertex in self:
            if subject_vertex.intersect:
                subject_vertex.entry = s_entry
                s_entry = not s_entry

        c_entry ^= is_inside_polygon(clip.first.vtx, self)
        for clipper_vertex in clip:
            if clipper_vertex.intersect:
                clipper_vertex.entry = c_entry
                c_entry = not c_entry

        # Phase 3: Construct clipped polygons
        clipped_polygons: list[list[Vec2]] = []
        while self.unprocessed():
            current: _Node = self.first_intersect  # type: ignore
            clipped = GHPolygon()
            clipped.add(_Node(current))
            while True:
                current.set_checked()
                if current.entry:
                    while True:
                        current = current.next
                        clipped.add(_Node(current))
                        if current.intersect:
                            break
                else:
                    while True:
                        current = current.prev
                        clipped.add(_Node(current))
                        if current.intersect:
                            break

                current = current.neighbour
                if current.checked:
                    break

            clipped_polygons.append(clipped.points)
        return clipped_polygons


def next_vertex_node(v: _Node) -> _Node:
    """Return the next non-intersecting vertex after the one specified."""
    c = v
    while c.intersect:
        c = c.next
    return c


def is_inside_polygon(vertex: Vec2, polygon: GHPolygon) -> bool:
    """Returns ``True`` if  `vertex` is inside `polygon` (odd-even rule).

    This function calculates the "winding" number for a point, which
    represents the number of times a ray emitted from the point to
    infinity intersects any edge of the polygon.

    An even winding number means the point lies OUTSIDE the polygon;
    an odd number means it lies INSIDE it.
    """
    winding_number: int = 0
    infinity = Vec2(polygon.max_x * 2, vertex.y)
    for node in polygon:
        if not node.intersect:
            if (
                line_intersection(
                    vertex,
                    infinity,
                    node.vtx,
                    next_vertex_node(node.next).vtx,
                )[0]
                is not None
            ):
                winding_number += 1
    return bool(winding_number % 2)


_ERROR = None, 0, 0


def line_intersection(
    s1: Vec2, s2: Vec2, c1: Vec2, c2: Vec2, tol: float = TOLERANCE
) -> tuple[Optional[Vec2], float, float]:
    """Returns the intersection point between two lines.

    This special implementation excludes the line end points as intersection
    points!

    Algorithm based on: http://paulbourke.net/geometry/lineline2d/
    """
    den = (c2.y - c1.y) * (s2.x - s1.x) - (c2.x - c1.x) * (s2.y - s1.y)
    if abs(den) < tol:
        return _ERROR

    us = ((c2.x - c1.x) * (s1.y - c1.y) - (c2.y - c1.y) * (s1.x - c1.x)) / den
    uc = ((s2.x - s1.x) * (s1.y - c1.y) - (s2.y - s1.y) * (s1.x - c1.x)) / den

    lwr = 0.0 + tol
    upr = 1.0 - tol
    # Line end points are excluded as intersection points:
    # us =~ 0.0; us =~ 1.0
    # uc =~ 0.0; uc =~ 1.0
    if (lwr < us < upr) and (lwr < uc < upr):
        return (
            Vec2(s1.x + us * (s2.x - s1.x), s1.y + us * (s2.y - s1.y)),
            us,
            uc,
        )
    return _ERROR


class BooleanOperation(enum.Enum):
    UNION = "union"
    DIFFERENCE = "difference"
    INTERSECTION = "intersection"


def greiner_hormann_intersection(
    p1: Iterable[UVec], p2: Iterable[UVec]
) -> list[list[Vec2]]:
    """Returns the INTERSECTION of polygon `p1` &  polygon `p2`.
    This algorithm works only for polygons with real intersection points
    and line end points on face edges are not considered as such intersection
    points!

    .. versionadded:: 0.18

    """
    return greiner_hormann(p1, p2, BooleanOperation.INTERSECTION)


def greiner_hormann_difference(
    p1: Iterable[UVec], p2: Iterable[UVec]
) -> list[list[Vec2]]:
    """Returns the DIFFERENCE of polygon `p1` - polygon `p2`.
    This algorithm works only for polygons with real intersection points
    and line end points on face edges are not considered as such intersection
    points!

    .. versionadded:: 0.18

    """
    return greiner_hormann(p1, p2, BooleanOperation.DIFFERENCE)


def greiner_hormann_union(
    p1: Iterable[UVec], p2: Iterable[UVec]
) -> list[list[Vec2]]:
    """Returns the UNION of polygon `p1` | polygon `p2`.
    This algorithm works only for polygons with real intersection points
    and line end points on face edges are not considered as such intersection
    points!

    .. versionadded:: 0.18

    """
    return greiner_hormann(p1, p2, BooleanOperation.UNION)


def greiner_hormann(
    p1: Iterable[UVec], p2: Iterable[UVec], op: BooleanOperation
) -> list[list[Vec2]]:
    """Implements a 2d clipping function to perform 3 boolean operations:

    - UNION: p1 | p2 ... p1 OR p2
    - INTERSECTION: p1 & p2 ... p1 AND p2
    - DIFFERENCE: p1 \\ p2 ... p1 - p2

    Based on the paper "Efficient Clipping of Arbitrary Polygons" by
    Günther Greiner and Kai Hormann.
    This algorithm works only for polygons with real intersection points
    and line end points on face edges are not considered as such intersection
    points!

    .. versionadded:: 0.18

    """
    polygon1 = GHPolygon.build(p1)
    polygon2 = GHPolygon.build(p2)

    if op == BooleanOperation.UNION:
        return polygon1.union(polygon2)
    elif op == BooleanOperation.DIFFERENCE:
        return polygon1.difference(polygon2)
    elif op == BooleanOperation.INTERSECTION:
        return polygon1.intersection(polygon2)
    raise ValueError(f"unknown or unsupported boolean operation: {op}")


LEFT = 0x1
RIGHT = 0x2
BOTTOM = 0x4
TOP = 0x8


def cohen_sutherland_line_clipping_2d(
    w_min: Vec2, w_max: Vec2, p0: Vec2, p1: Vec2
) -> Sequence[Vec2]:
    """Cohen-Sutherland 2D line clipping algorithm, source:
    https://en.wikipedia.org/wiki/Cohen%E2%80%93Sutherland_algorithm

    Args:
        w_min: bottom-left corner of the clipping rectangle
        w_max: top-right corner of the clipping rectangle
        p0: start-point of the line to clip
        p1: end-point of the line to clip

    """

    def encode(x: float, y: float) -> int:
        code: int = 0
        if x < x_min:
            code |= LEFT
        elif x > x_max:
            code |= RIGHT
        if y < y_min:
            code |= BOTTOM
        elif y > y_max:
            code |= TOP
        return code

    x0, y0 = p0
    x1, y1 = p1
    x_min, y_min = w_min
    x_max, y_max = w_max
    code0 = encode(x0, y0)
    code1 = encode(x1, y1)
    x = x0
    y = y0
    while True:
        if not (code0 | code1):  # ACCEPT
            # bitwise OR is 0: both points inside window; trivially accept and
            # exit loop:
            return Vec2(x0, y0), Vec2(x1, y1)
        if code0 & code1:  # REJECT
            # bitwise AND is not 0: both points share an outside zone (LEFT,
            # RIGHT, TOP, or BOTTOM), so both must be outside window;
            # exit loop
            return tuple()

        # failed both tests, so calculate the line segment to clip
        # from an outside point to an intersection with clip edge
        # At least one endpoint is outside the clip rectangle; pick it
        code = code1 if code1 > code0 else code0

        # Now find the intersection point;
        # use formulas:
        # slope = (y1 - y0) / (x1 - x0)
        # x = x0 + (1 / slope) * (ym - y0), where ym is y_min or y_max
        # y = y0 + slope * (xm - x0), where xm is x_min or x_max
        # No need to worry about divide-by-zero because, in each case, the
        # code bit being tested guarantees the denominator is non-zero
        if code & TOP:  # point is above the clip window
            x = x0 + (x1 - x0) * (y_max - y0) / (y1 - y0)
            y = y_max
        elif code & BOTTOM:  # point is below the clip window
            x = x0 + (x1 - x0) * (y_min - y0) / (y1 - y0)
            y = y_min
        elif code & RIGHT:  # point is to the right of clip window
            y = y0 + (y1 - y0) * (x_max - x0) / (x1 - x0)
            x = x_max
        elif code & LEFT:  # point is to the left of clip window
            y = y0 + (y1 - y0) * (x_min - x0) / (x1 - x0)
            x = x_min

        if code == code0:
            x0 = x
            y0 = y
            code0 = encode(x0, y0)
        else:
            x1 = x
            y1 = y
            code1 = encode(x1, y1)
