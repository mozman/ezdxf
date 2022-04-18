#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
from typing import (
    Iterable,
    List,
    Optional,
    Iterator,
    Union,
    Tuple,
)

from ezdxf.math import (
    Vec2,
    intersection_line_line_2d,
    has_clockwise_orientation,
    point_to_line_relation,
    TOLERANCE,
    Vertex,
)
import enum

__all__ = [
    "clip_polygon_2d",
    "greiner_hormann_union",
    "greiner_hormann_difference",
    "greiner_hormann_intersection",
]


def clip_polygon_2d(
    clip: Iterable[Vertex],
    subject: Iterable[Vertex],
    ccw_check: bool = True,
) -> List[Vec2]:
    """Clip the `subject` polygon by the **convex** clipping polygon `clip`.

    Implements the `Sutherland–Hodgman`_ algorithm for clipping polygons.

    Args:
        clip: the convex clipping polygon as iterable of vertices
        subject: the polygon to clip as a iterable of vertices
        ccw_check: check if the clipping polygon is in counter clockwise
            orientation if ``True``, set to ``False`` if the ccw check is done
            by the caller

    Returns:
        the clipped subject as list of :class:`~ezdxf.math.Vec2`

    .. versionadded:: 0.16

    .. _Sutherland–Hodgman: https://de.wikipedia.org/wiki/Algorithmus_von_Sutherland-Hodgman

    """

    def polygon(vertices: Iterable[Vertex]) -> List[Vec2]:
        _vertices = Vec2.list(vertices)
        if len(_vertices) > 1:
            if _vertices[0].isclose(_vertices[-1]):
                _vertices.pop()
        return _vertices

    def is_inside(point: Vec2) -> bool:
        return (
            point_to_line_relation(point, clip_start, clip_end) == -1
        )  # left of line

    def edge_intersection() -> Vec2:
        return intersection_line_line_2d(
            (edge_start, edge_end), (clip_start, clip_end)
        )

    clipping_polygon = polygon(clip)
    if ccw_check and has_clockwise_orientation(clipping_polygon):
        clipping_polygon.reverse()
    if len(clipping_polygon) > 2:
        clip_start = clipping_polygon[-1]
    else:
        raise ValueError("invalid clipping polygon")
    clipped = polygon(subject)

    for clip_end in clipping_polygon:
        # next clipping edge to test: clip_start -> clip_end
        if not clipped:  # no subject vertices left to test
            break
        vertices = list(clipped)
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


# Efficient Clipping of Arbitrary Polygons
#
# Based on the paper "Efficient Clipping of Arbitrary Polygons" by Günther
# Greiner (greiner[at]informatik.uni-erlangen.de) and Kai Hormann
# (hormann[at]informatik.tu-clausthal.de), ACM Transactions on Graphics
# 1998;17(2):71-83.
#
# Available at: http://www.inf.usi.ch/hormann/papers/Greiner.1998.ECO.pdf


class _Node:
    """Node in a circular doubly linked list.

    This class is almost exactly as described in the paper by Günther/Greiner.
    """

    def __init__(
        self,
        vtx: Union[Vec2, "_Node"],
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


class _Polygon:
    """Manages a circular doubly linked list of Vertex objects that represents
    a polygon.
    """

    first: _Node = None  # type: ignore

    def add(self, vertex: _Node):
        """Add a vertex object to the polygon (vertex is added at the 'end' of
        the list").
        """
        if self.first is None:
            self.first = vertex
            self.first.next = vertex
            self.first.prev = vertex
        else:
            _next = self.first
            assert isinstance(_next, _Node)
            prev = _next.prev
            assert isinstance(prev, _Node)
            _next.prev = vertex
            vertex.next = _next
            vertex.prev = prev
            prev.next = vertex

    @staticmethod
    def insert(vertex: _Node, start: _Node, end: _Node):
        """Insert and sort a vertex between a specified pair of vertices.

        This function inserts a vertex (most likely an intersection point)
        between two other vertices (start and end). These other vertices
        cannot be intersections (that is, they must be actual vertices of
        the original polygon). If there are multiple intersection points
        between the two vertices, then the new vertex is inserted based on
        its alpha value.
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
        """Return the first unchecked intersection point in the polygon."""
        for v in self:
            if v.intersect and not v.checked:
                return v
        return None

    @property
    def points(self) -> List[Vec2]:
        points = [v.vtx for v in self]
        if not points[0].isclose(points[-1]):
            points.append(points[0])
        return list(filter_coincident_vertices(points))

    def unprocessed(self):
        """Check if any unchecked intersections remain in the polygon."""
        for v in self:
            if v.intersect and not v.checked:
                return True
        return False

    def union(self, clip: "_Polygon") -> List[List[Vec2]]:
        return self.clip(clip, False, False)

    def intersection(self, clip: "_Polygon") -> List[List[Vec2]]:
        return self.clip(clip, True, True)

    def difference(self, clip: "_Polygon") -> List[List[Vec2]]:
        return self.clip(clip, False, True)

    def clip(self, clip: "_Polygon", s_entry, c_entry) -> List[List[Vec2]]:
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
                        try:
                            intersection_point, alphaS, alphaC = line_intersection(
                                subject_vertex.vtx,
                                next_non_intersection_node(
                                    subject_vertex.next
                                ).vtx,
                                clipper_vertex.vtx,
                                next_non_intersection_node(
                                    clipper_vertex.next
                                ).vtx,
                            )
                        except IntersectionError:
                            continue
                        subject_node = _Node(
                            intersection_point,
                            alphaS,
                            intersect=True,
                            entry=False,
                        )
                        clipper_node = _Node(
                            intersection_point,
                            alphaC,
                            intersect=True,
                            entry=False,
                        )
                        subject_node.neighbour = clipper_node
                        clipper_node.neighbour = subject_node

                        self.insert(
                            subject_node,
                            subject_vertex,
                            next_non_intersection_node(subject_vertex.next),
                        )
                        clip.insert(
                            clipper_node,
                            clipper_vertex,
                            next_non_intersection_node(clipper_vertex.next),
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
        clipped_polygons: List[List[Vec2]] = []
        while self.unprocessed():
            current: _Node = self.first_intersect  # type: ignore
            clipped = _Polygon()
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

        if len(clipped_polygons) == 0:
            clipped_polygons.append(self.points)

        return clipped_polygons


def filter_coincident_vertices(vertices: Iterable[Vec2]) -> Iterator[Vec2]:
    prev = None
    for v in vertices:
        if prev is not None and v.isclose(prev):
            continue
        yield v
        prev = v


def next_non_intersection_node(v: _Node) -> _Node:
    """Return the next non intersecting vertex after the one specified."""
    c = v
    while c.intersect:
        c = c.next
    return c


def is_inside_polygon(vertex: Vec2, polygon: "_Polygon") -> bool:
    """Returns ``True`´ if  `vertex` is inside `polygon` (odd-even rule).

    This function calculates the "winding" number for a point, which
    represents the number of times a ray emitted from the point to
    infinity intersects any edge of the polygon.

    An even winding number means the point lies OUTSIDE the polygon;
    an odd number means it lies INSIDE it.
    """
    winding_number: int = 0
    infinity = Vec2(1e6, vertex.y)
    for node in polygon:
        if not node.intersect:
            try:
                line_intersection(
                    vertex,
                    infinity,
                    node.vtx,
                    next_non_intersection_node(node.next).vtx,
                )
                winding_number += 1
            except IntersectionError:
                pass
    return bool(winding_number % 2)


def line_intersection(
    s1: Vec2, s2: Vec2, c1: Vec2, c2: Vec2, tol: float = TOLERANCE
) -> Tuple[Vec2, float, float]:
    """Returns the intersection point between two lines.

    Algorithm based on: http://paulbourke.net/geometry/lineline2d/
    """
    den: float = (c2.y - c1.y) * (s2.x - s1.x) - (c2.x - c1.x) * (s2.y - s1.y)

    if abs(den) < tol:
        raise IntersectionError

    us: float = (
        (c2.x - c1.x) * (s1.y - c1.y) - (c2.y - c1.y) * (s1.x - c1.x)
    ) / den
    uc: float = (
        (s2.x - s1.x) * (s1.y - c1.y) - (s2.y - s1.y) * (s1.x - c1.x)
    ) / den
    lwr = 0.0
    upr = 1.0
    if (lwr <= us <= upr) and (lwr <= uc <= upr):
        return (
            Vec2(s1.x + us * (s2.x - s1.x), s1.y + us * (s2.y - s1.y)),
            us,
            uc,
        )
    raise IntersectionError


class BooleanOperation(enum.Enum):
    UNION = "union"
    DIFFERENCE = "difference"
    INTERSECTION = "intersection"


def greiner_hormann_intersection(
    p1: Iterable[Vertex], p2: Iterable[Vertex]
) -> List[List[Vec2]]:
    """Returns the INTERSECTION of polygon `p1` &  polygon `p2`."""
    return greiner_hormann(p1, p2, BooleanOperation.INTERSECTION)


def greiner_hormann_difference(
    p1: Iterable[Vertex], p2: Iterable[Vertex]
) -> List[List[Vec2]]:
    """Returns the DIFFERENCE of polygon `p1` - polygon `p2`."""
    return greiner_hormann(p1, p2, BooleanOperation.DIFFERENCE)


def greiner_hormann_union(
    p1: Iterable[Vertex], p2: Iterable[Vertex]
) -> List[List[Vec2]]:
    """Returns the UNION of polygon `p1` | polygon `p2`."""
    return greiner_hormann(p1, p2, BooleanOperation.UNION)


def greiner_hormann(
    p1: Iterable[Vertex], p2: Iterable[Vertex], op: BooleanOperation
) -> List[List[Vec2]]:
    """Implements a 2d clipping function to perform 3 boolean operations:

    - UNION: p1 | p2 ... p1 OR p2
    - INTERSECTION: p1 & p2 ... p1 AND p2
    - DIFFERENCE: p1 \\ p2 ... p1 - p2

    Based on the paper "Efficient Clipping of Arbitrary Polygons" by
    Günther Greiner and Kai Hormann.

    """

    def build(vertices) -> _Polygon:
        polygon = _Polygon()
        _vertices = Vec2.list(vertices)
        for v in _vertices:
            polygon.add(_Node(v))
        return polygon

    polygon1 = build(p1)
    polygon2 = build(p2)

    if op == BooleanOperation.UNION:
        return polygon1.union(polygon2)
    elif op == BooleanOperation.DIFFERENCE:
        return polygon1.difference(polygon2)
    elif op == BooleanOperation.INTERSECTION:
        return polygon1.intersection(polygon2)
    raise ValueError(f"unknown or unsupported boolean operation: {op}")
