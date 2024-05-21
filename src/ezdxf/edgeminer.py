# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
"""
EdgeMiner
=========

A module for detecting shapes build of linked edges.

The complementary module ezdxf.edgesmith can create entities from the output of this 
module.

.. versionadded:: 1.4

"""
from __future__ import annotations
from typing import Any, Sequence, Iterator, Iterable
import math

from ezdxf.entities import DXFEntity, Arc, Ellipse, Spline, Line
from ezdxf.math import (
    UVec,
    Vec2,
    arc_angle_span_deg,
    ellipse_param_span,
    distance_point_line_2d,
)
from ezdxf.math import rtree

__all__ = [
    "find_all_loops",
    "find_first_loop",
    "find_shortest_loop",
    "find_longest_loop",
    "edge_from_entity",
    "length",
    "filter_short_edges",
    "Edge",
]
ABS_TOL = 1e-12
GAP_TOL = 1e-12


def edge_from_entity(entity: DXFEntity, gap_tol=GAP_TOL) -> Edge | None:
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
    elif isinstance(entity, Arc):
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
    elif isinstance(entity, Ellipse):
        try:
            ct1 = entity.construction_tool()
        except ValueError:
            return None
        if ct1.major_axis.magnitude < ABS_TOL or ct1.minor_axis.magnitude < ABS_TOL:
            return None
        span = ellipse_param_span(ct1.start_param, ct1.end_param)
        num = max(3, round(span / 0.1745))  #  resolution of ~1 deg
        # length of elliptic arc is an approximation:
        points = list(ct1.vertices(ct1.params(num)))
        length = sum(a.distance(b) for a, b in zip(points, points[1:]))
        edge = Edge(Vec2(points[0]), Vec2(points[-1]), length, entity)
    elif isinstance(entity, Spline):
        try:
            ct2 = entity.construction_tool()
        except ValueError:
            return None
        start = Vec2(ct2.control_points[0])
        end = Vec2(ct2.control_points[-1])
        points = list(ct2.control_points)
        # length of B-spline is a very rough approximation:
        length = sum(a.distance(b) for a, b in zip(points, points[1:]))
        edge = Edge(start, end, length, entity)

    if isinstance(edge, Edge):
        if edge.start.distance(edge.end) < gap_tol:
            return None
        if edge.length < gap_tol:
            return None
    return edge


def length(edges: Sequence[Edge]) -> float:
    """Returns the length of a sequence of edges."""
    return sum(e.length for e in edges)


def find_shortest_loop(edges: Sequence[Edge], gap_tol=GAP_TOL) -> Sequence[Edge]:
    """Returns the shortest closed loop found.

    Note: Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edges: edges to be examined
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    solutions = sorted(find_all_loops(edges, gap_tol=gap_tol), key=length)
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
    solutions = sorted(find_all_loops(edges, gap_tol=gap_tol), key=length)
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


def filter_short_edges(edges: Iterable[Edge], gap_tol=GAP_TOL) -> tuple[Edge, ...]:
    """Removes all edges where the start vertex is very close to the end vertex.

    These edges represent very short curves or maybe closed curves like circles and
    ellipses.
    """
    return tuple(e for e in edges if e.start.distance(e.end) >= gap_tol)


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

        self._search(Loop((start,)), tuple(available))

    def _search(self, loop: Loop, available: tuple[Edge, ...]):
        """Recursive backtracking with a time complexity of O(n!)."""
        if len(available) == 0:
            return

        for next_edge in available:
            edge = next_edge
            extended_loop: Loop | None = None
            if loop.is_connected(edge, self._gap_tol):
                extended_loop = Loop(loop.edges + (edge,))
            else:
                edge = next_edge.reversed()
                if loop.is_connected(edge, self._gap_tol):
                    extended_loop = Loop(loop.edges + (edge,))

            if extended_loop is None:
                continue

            if extended_loop.is_closed_loop(self._gap_tol):
                self._append_solution(extended_loop)
            else:  # depth search
                _id = edge.id
                self._search(extended_loop, tuple(e for e in available if e.id != _id))

            if self._stop_at_first_solution and self._solutions:
                return

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


class EdgeVertexIndex:
    """Index of edges referenced by the id of their start- and end vertices.

    .. important::

        The id of the vertices is indexed not the location!

    """

    def __init__(self, edges: Sequence[Edge]) -> None:
        index: dict[int, Edge] = {}
        for edge in edges:
            index[id(edge.start)] = edge
            index[id(edge.end)] = edge
        self._index = index

    def find_edges(self, vertices: Iterable[Vec2]) -> Sequence[Edge]:
        """Returns all edges referenced by the id of given vertices."""
        index = self._index
        edges: list[Edge] = []
        for vertex in vertices:
            edge = index.get(id(vertex))
            if edge:
                edges.append(edge)
        return edges


class SearchIndex:
    """Spatial search index of all edge vertices."""

    def __init__(self, edges: Sequence[Edge]) -> None:
        vertices: list[Edge] = []
        for edge in edges:
            vertices.append(edge.start)
            vertices.append(edge.end)
        self._search_tree = rtree.RTree(vertices)

    def vertices_in_circle(self, center: Vec2, radius: float) -> Sequence[Vec2]:
        """Returns all vertices located around center with a max. distance of `radius`."""
        return tuple(self._search_tree.points_in_sphere(center, radius))  # type: ignore

    def nearest_vertex(self, location: Vec2) -> Vec2:
        """Returns the nearest vertex to the given location."""
        vertex, _ = self._search_tree.nearest_neighbor(location)
        return vertex  # type: ignore


def discard_edges(edges: Iterable[Edge], discard: Iterable[Edge]) -> Sequence[Edge]:
    ids = set(e.id for e in discard)
    return tuple(e for e in edges if e.id not in ids)


class EdgeDeposit:
    def __init__(self, edges: Iterable[Edge], gap_tol=GAP_TOL) -> None:
        self.edges = tuple(edges)
        self.gap_tol = gap_tol
        self.edge_index = EdgeVertexIndex(self.edges)
        self.search_index = SearchIndex(self.edges)

    def direct_linked_edges(self, vertex: UVec, radius: float = -1) -> Sequence[Edge]:
        """Returns all edges directly linked to `vertex` in range of `radius`.

        Default radius is :attr:`self.gap_tol`.
        """
        if radius < 0:
            radius = self.gap_tol
        vertices = self.search_index.vertices_in_circle(Vec2(vertex), radius)
        if not vertices:
            return []
        return self.edge_index.find_edges(vertices)

    def find_nearest_edge(self, location: UVec) -> Edge | None:
        """Return the nearest edge to the given location.

        The distance is measured to the connection line from start to end of the edge.
        This is not correct for edges that represent arcs or splines.
        """

        def distance(edge: Edge) -> float:
            return distance_point_line_2d(location, edge.start, edge.end)
        
        si = self.search_index
        nearest_vertex = si.nearest_vertex(Vec2(location))
        edges = self.direct_linked_edges(nearest_vertex)
        if not edges:
            return None
        return min(edges, key=distance)

    def find_all_linked_edges(self, edge: Edge) -> Sequence[Edge]:
        """Returns all edges directly and indirectly linked to `edge`.

        The edges are in no particular order.
        """

        def process(vertex: Vec2) -> None:
            linked_edges = self.direct_linked_edges(vertex)
            linked_edges = discard_edges(linked_edges, discard=found)
            found.extend(linked_edges)
            todo.extend(linked_edges)

        found: list[Edge] = [edge]
        todo: list[Edge] = [edge]

        while todo:
            edge = todo.pop(0)
            process(edge.start)
            process(edge.end)
        return tuple(found)
