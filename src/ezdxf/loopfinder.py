# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Any, Sequence, Iterator
import math

from ezdxf.entities import (
    DXFEntity,
    Circle,
    Arc,
    Ellipse,
    Spline,
    LWPolyline,
    Polyline,
    Line,
)
from ezdxf.math import arc_angle_span_deg, ellipse_param_span, Vec2, Vec3

__all__ = [
    "find_all_loops",
    "find_first_loop",
    "find_shortest_loop",
    "find_longest_loop",
    "is_closed_entity",
    "edge_from_entity",
    "loop_length",
    "Edge",
]

ABS_TOL = 1e-12
GAP_TOL = 1e-12  # maximum distance to consider two points as coincident


def is_closed_entity(entity: DXFEntity) -> bool:
    """Returns ``True`` if the given entity represents a closed loop."""
    if isinstance(entity, Arc):  # Arc inherits from Circle!
        radius = abs(entity.dxf.radius)
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        angle_span = arc_angle_span_deg(start_angle, end_angle)
        return abs(radius) > ABS_TOL and math.isclose(
            angle_span, 360.0, abs_tol=ABS_TOL
        )
    if isinstance(entity, Circle):
        return abs(entity.dxf.radius) > ABS_TOL

    if isinstance(entity, Ellipse):
        start_param = entity.dxf.start_param
        end_param = entity.dxf.end_param
        span = ellipse_param_span(start_param, end_param)
        if not math.isclose(span, math.tau, abs_tol=ABS_TOL):
            return False
        return True

    if isinstance(entity, Spline):
        try:
            bspline = entity.construction_tool()
        except ValueError:
            return False
        control_points = bspline.control_points
        if len(control_points) < 3:
            return False
        start = control_points[0]
        end = control_points[-1]
        return start.isclose(end, abs_tol=ABS_TOL)

    if isinstance(entity, LWPolyline):
        if len(entity) < 1:
            return False
        if entity.closed is True:
            return True
        start = Vec2(entity.lwpoints[0][:2])
        end = Vec2(entity.lwpoints[-1][:2])
        return start.isclose(end, abs_tol=ABS_TOL)

    if isinstance(entity, Polyline):
        if entity.is_2d_polyline or entity.is_3d_polyline:
            # Note: does not check if all vertices of a 3D polyline are placed on a
            # common plane.
            vertices = entity.vertices
            if len(vertices) < 2:
                return False
            if entity.is_closed:
                return True
            p0: Vec3 = vertices[0].dxf.location  # type: ignore
            p1: Vec3 = vertices[-1].dxf.location  # type: ignore
            if p0.isclose(p1, abs_tol=ABS_TOL):
                return True
        return False
    return False


def edge_from_entity(entity: DXFEntity) -> Edge | None:
    """Makes an :class:`Edge` instance for the DXF entity types LINE, ARC, ELLIPSE and
    SPLINE if the entity is an open linear curve.  Returns ``None`` if the entity
    is a closed curve or cannot represent an edge.
    """
    # TODO: for now I assume all entities are located in the xy-plane of then WCS
    edge: Edge | None = None

    if isinstance(entity, Line):
        start = Vec2(entity.dxf.start)
        end = Vec2(entity.dxf.end)
        length = start.distance(end)
        edge = Edge(start, end, length, entity)
    elif isinstance(entity, Arc) and not is_closed_entity(entity):
        try:
            ct0 = entity.construction_tool()
        except ValueError:
            return None
        radius = abs(ct0.radius)
        if radius < ABS_TOL:
            return None
        span_deg = arc_angle_span_deg(ct0.start_angle, ct0.end_angle)
        length = radius * span_deg / 180.0 * math.pi
        edge = Edge(ct0.start_point, ct0.end_point, length, entity)
    elif isinstance(entity, Ellipse) and not is_closed_entity(entity):
        try:
            ct1 = entity.construction_tool()
        except ValueError:
            return None
        if ct1.major_axis.magnitude < ABS_TOL or ct1.minor_axis.magnitude < ABS_TOL:
            return None
        span = ellipse_param_span(ct1.start_param, ct1.end_param)
        num = max(3, round(span / 0.1745))  #  resolution of ~1 deg
        points = list(ct1.vertices(ct1.params(num)))  # approximation
        length = sum(a.distance(b) for a, b in zip(points, points[1:]))
        edge = Edge(Vec2(points[0]), Vec2(points[-1]), length, entity)
    elif isinstance(entity, Spline) and not is_closed_entity(entity):
        try:
            ct2 = entity.construction_tool()
        except ValueError:
            return None
        start = Vec2(ct2.control_points[0])
        end = Vec2(ct2.control_points[-1])
        points = list(ct2.control_points)  # rough approximation
        length = sum(a.distance(b) for a, b in zip(points, points[1:]))
        edge = Edge(start, end, length, entity)

    if isinstance(edge, Edge):
        if edge.start.isclose(edge.end, abs_tol=ABS_TOL):
            return None
        if edge.length < ABS_TOL:
            return None
    return edge


def loop_length(edges: Sequence[Edge]) -> float:
    """Returns the length of a sequence of edges."""
    return sum(e.length for e in edges)


def find_shortest_loop(edges: Sequence[Edge], gap_tol=GAP_TOL) -> Sequence[Edge]:
    """Returns the shortest closed loop found.

    Note: Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edges: edges to be examined
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    solutions = sorted(find_all_loops(edges, gap_tol=gap_tol), key=loop_length)
    if solutions:
        return solutions[0]
    return []


def find_longest_loop(edges: Sequence[Edge], gap_tol=GAP_TOL) -> Sequence[Edge]:
    """Returns the longest closed loop found.

    Note: Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edges: edges to be examined
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    solutions = sorted(find_all_loops(edges, gap_tol=gap_tol), key=loop_length)
    if solutions:
        return solutions[-1]
    return []


def find_first_loop(edges: Sequence[Edge], gap_tol=GAP_TOL) -> Sequence[Edge]:
    """Returns the first closed loop found.

    Note: Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edges: edges to be examined
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    finder = LoopFinder(first=True, gap_tol=gap_tol)
    available = tuple(edges)
    if len(available) < 2:
        return []
    finder.search(available[0], available[1:])
    solutions = list(finder)
    if solutions:
        return solutions[0]
    return []


def find_all_loops(edges: Sequence[Edge], gap_tol=GAP_TOL) -> Sequence[Sequence[Edge]]:
    """Returns all unique closed loops and doesn't include reversed solutions.

    Note: Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edges: edges to be examined
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    finder = LoopFinder(discard_reverse=True, gap_tol=gap_tol)
    _edges = list(edges)
    for _ in range(len(edges)):
        available = tuple(_edges)
        finder.search(available[0], available[1:])
        # Rotate the edges and start the search again to get an exhaustive result.
        first = _edges.pop(0)
        _edges.append(first)
        # It's not required to search for disconnected loops - by rotating and restarting,
        # every possible loop is taken into account.
    return tuple(finder)


class Edge:
    """Represents an edge. 
    
    The edge can represent any linear curve (line, arc, spline,...). 
    Therefore, the length of the edge must be specified if the length calculation for 
    loops is to be possible.

    Attributes:
        id: unique id as int
        start: start vertex as Vec2
        end: end vertex as Vec2
        reverse: flag to indicate that the edge is reversed compared to its initial state
        length: length of the edge, default is the distance between start- and end vertex
        payload: arbitrary data associated to the edge

    """

    __slots__ = ("id", "start", "end", "reverse", "length", "payload")
    _next_id = 1

    def __init__(
        self, start: Vec2, end: Vec2, length: float = -1.0, payload: Any = None
    ) -> None:
        self.id = Edge._next_id  # unique id but (reversed) copies have the same id
        Edge._next_id += 1
        self.start: Vec2 = start
        self.end: Vec2 = end
        self.reverse: bool = False
        if length < 0.0:
            length = start.distance(end)
        self.length = length
        self.payload = payload

    def __eq__(self, other) -> bool:
        """Return ``True`` if the ids of the edges are equal."""
        if isinstance(other, Edge):
            return self.id == other.id
        return False

    def copy(self) -> Edge:
        """Returns a copy."""
        edge = Edge(self.start, self.end, self.length, self.payload)
        edge.reverse = self.reverse
        edge.id = self.id  # copies represent the same edge
        return edge

    def reversed(self) -> Edge:
        """Returns a reversed copy."""
        edge = Edge(self.end, self.start, self.length, self.payload)
        edge.reverse = not self.reverse
        edge.id = self.id  # reversed copies represent the same edge
        return edge


class Loop:
    """Represents connected edges.

    Each end vertex of an edge is connected to the start vertex of the following edge.
    It is a closed loop when the first edge is connected to the last edge.

    (internal helper class)
    """

    def __init__(self, edges: tuple[Edge, ...]) -> None:
        self.edges: tuple[Edge, ...] = edges

    def is_connected(self, edge: Edge, gap_tol=GAP_TOL) -> bool:
        """Returns ``True`` if the last edge of the loop is connected to the given edge.

        Args:
            edge: edge to be examined
            gap_tol: maximum vertex distance to consider two edges as connected
        """
        if self.edges:
            return self.edges[-1].end.distance(edge.start) < gap_tol
        return False

    def is_closed_loop(self, gap_tol=GAP_TOL) -> bool:
        """Returns ``True`` if the first edge is connected to the last edge.

        Args:
            gap_tol: maximum vertex distance to consider two edges as connected
        """

        if len(self.edges) > 1:
            return self.edges[0].start.distance(self.edges[-1].end) < gap_tol
        return False

    def connect(self, edge: Edge) -> Loop:
        """Appends the edge to the loop. The edge must be connected to the last edge
        in the loop.  That is not checked here!
        """
        return Loop(self.edges + (edge,))

    def key(self, reverse=False) -> tuple[int, ...]:
        """Returns a normalized key.

        The key is rotated to begin with the smallest edge id.
        """
        if len(self.edges) < 2:
            raise ValueError("too few edges")
        if reverse:
            ids = tuple(edge.id for edge in reversed(self.edges))
        else:
            ids = tuple(edge.id for edge in self.edges)
        index = ids.index(min(ids))
        if index:
            ids = ids[index:] + ids[:index]
        return ids


class LoopFinder:
    """Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        first: flag to stop the search at the first loop found
        discard_reverse: discard loops that are identical to found loops but in reverse order
        gap_tol: maximum vertex distance to consider two edges as connected

    """

    def __init__(self, first=False, discard_reverse=True, gap_tol=GAP_TOL) -> None:
        self._solutions: dict[tuple[int, ...], tuple[Edge, ...]] = {}
        self._stop_at_first_solution = first
        self._discard_reverse_solutions = discard_reverse
        self._gap_tol = gap_tol

    def __iter__(self) -> Iterator[tuple[Edge, ...]]:
        """Yields all found loops as sequences of edges."""
        return iter(self._solutions.values())

    def search(self, start: Edge, available: Sequence[Edge]):
        """Searches for closed loops in the available edges, starting from the given
        start edge.

        The starting edge cannot exist in the available edges and the
        avalibale edges cannot have duplicate edges.

        Args:
            start: staring edge
            available: available edges

        Raises:
            ValueError: duplicate edges or starting edge in available edges

        """
        ids = [e.id for e in available]
        unique_ids = set(ids)
        if len(ids) != len(unique_ids):
            raise ValueError("available edges cannot have duplicate edges")
        if start.id in unique_ids:
            raise ValueError("starting edge cannot exist in available edges")
        self._search(Loop((start,)), available)

    def _search(self, loop: Loop, available: Sequence[Edge]):
        """Recursive backtracking with a time complexity of O(n!)."""
        if len(available) == 0:
            return
        if self._stop_at_first_solution and self._solutions:
            return

        for next_edge in tuple(available):
            edge = next_edge
            loop_ext: Loop | None = None
            if loop.is_connected(edge, self._gap_tol):
                loop_ext = loop.connect(edge)
            else:
                edge = next_edge.reversed()
                if loop.is_connected(edge, self._gap_tol):
                    loop_ext = loop.connect(edge)

            if loop_ext is None:
                continue

            if loop_ext.is_closed_loop(gap_tol=GAP_TOL):
                self._append_solution(loop_ext)
            else:  # depth search
                _id = edge.id
                self._search(loop_ext, tuple(e for e in available if e.id != _id))

    def _append_solution(self, loop: Loop) -> None:
        """Add loop to solutions."""
        key = loop.key()
        if key in self._solutions:
            return
        if (
            self._discard_reverse_solutions
            and loop.key(reverse=True) in self._solutions
        ):
            return
        self._solutions[key] = loop.edges
