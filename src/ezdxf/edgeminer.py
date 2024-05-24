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
from typing_extensions import Self
from collections import defaultdict
import time

from ezdxf.math import UVec, Vec3, distance_point_line_3d
from ezdxf.math import rtree

__all__ = [
    "find_all_loops",
    "find_first_loop",
    "find_shortest_loop",
    "find_longest_loop",
    "length",
    "filter_short_edges",
    "Edge",
]
ABS_TOL = 1e-12
GAP_TOL = 1e-12
TIMEOUT = 60.0  # in seconds


class EdgeMinerException(Exception):
    pass


class TimeoutError(EdgeMinerException):
    pass


class DuplicateEdgesError(EdgeMinerException):
    pass


class StopSearchException(EdgeMinerException):
    pass


class Edge:
    """Represents an edge.

    The edge can represent any linear curve (line, arc, spline,...).
    Therefore, the length of the edge must be specified if the length calculation for
    a sequence of edges is to be possible.

    Attributes:
        id: unique id as int
        start: start vertex as Vec3
        end: end vertex as Vec3
        reverse: flag to indicate that the edge is reversed compared to its initial state
        length: length of the edge, default is the distance between start- and end vertex
        payload: arbitrary data associated to the edge
    """

    __slots__ = ("id", "start", "end", "reverse", "length", "payload")
    _next_id = 1

    def __init__(
        self, start: UVec, end: UVec, length: float = -1.0, payload: Any = None
    ) -> None:
        self.id = Edge._next_id  # unique id but reversed copies have the same id
        Edge._next_id += 1
        self.start = Vec3(start)
        self.end = Vec3(end)
        self.reverse: bool = False
        if length < 0.0:
            length = self.start.distance(self.end)
        self.length = length
        self.payload = payload

    def __eq__(self, other) -> bool:
        """Return ``True`` if the ids of the edges are equal."""
        if isinstance(other, Edge):
            return self.id == other.id
        return False

    def reversed(self) -> Self:
        """Returns a reversed copy."""
        edge = self.__class__(self.end, self.start, self.length, self.payload)
        edge.reverse = not self.reverse
        edge.id = self.id  # reversed copies represent the same edge
        return edge


class Watchdog:
    def __init__(self, timeout=TIMEOUT) -> None:
        self.timeout: float = timeout
        self.start_time: float = time.perf_counter()

    def start(self, timeout: float):
        self.timeout = timeout
        self.start_time = time.perf_counter()

    def has_timed_out(self) -> bool:
        return time.perf_counter() - self.start_time > self.timeout

    def check_timeout(self, msg: str) -> None:
        if self.has_timed_out():
            raise TimeoutError(msg)


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
    finder = LoopFinderRBT(first=True, gap_tol=gap_tol)
    available = tuple(type_check(edges))
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
    finder = LoopFinderRBT(discard_reverse=True, gap_tol=gap_tol)
    _edges = list(type_check(edges))
    for _ in range(len(edges)):
        available = tuple(_edges)
        finder.search(available[0], available[1:])
        # Rotate the edges and start the search again to get an exhaustive result.
        first = _edges.pop(0)
        _edges.append(first)
        # It's not required to search for disconnected loops - by rotating and restarting,
        # every possible loop is taken into account.
    return tuple(finder)


def type_check(edges: Sequence[Edge]) -> Sequence[Edge]:
    for edge in edges:
        if not isinstance(edge, Edge):
            raise TypeError(f"expected type <Edge>, got {str(type(edge))}")
    return edges


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


class LoopFinderRBT:
    """Recursive backtracking algorithm to find closed loops with time complexity of O(n!).

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
        self.watchdog = Watchdog()

    def __iter__(self) -> Iterator[tuple[Edge, ...]]:
        """Yields all loops found as sequences of edges."""
        return iter(self._solutions.values())

    def __len__(self) -> int:
        """Returns the count of loops found."""
        return len(self._solutions)

    def search(self, start: Edge, available: Sequence[Edge], timeout=TIMEOUT):
        """Searches for closed loops in the available edges, starting from the given
        start edge.

        The starting edge cannot exist in the available edges and the
        avalibale edges cannot have duplicate edges.

        Args:
            start: staring edge
            available: available edges

        Raises:
            DuplicateEdgesError: duplicate edges or starting edge in available edges
            TimeoutError: search process has timed out
            RecursionError: search exceeded Python's recursion limit
        """
        ids = [e.id for e in available]
        unique_ids = set(ids)
        if len(ids) != len(unique_ids):
            raise DuplicateEdgesError("available edges cannot have duplicate edges")
        if start.id in unique_ids:
            raise DuplicateEdgesError("starting edge cannot exist in available edges")
        self.watchdog.start(timeout)
        try:
            self._search(Loop((start,)), tuple(available))
        except StopSearchException:
            pass

    def _search(self, loop: Loop, available: tuple[Edge, ...]):
        for next_edge in available:
            # raises TimeoutError:
            self.watchdog.check_timeout("search process has timed out")  
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
                if self._stop_at_first_solution:
                    raise StopSearchException
            else:  # depth search, may raise RecursionError
                _id = edge.id
                self._search(extended_loop, tuple(e for e in available if e.id != _id))

    def _append_solution(self, loop: Loop) -> None:
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

    def find_edges(self, vertices: Iterable[Vec3]) -> Sequence[Edge]:
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
        vertices: list[Vec3] = []
        for edge in edges:
            vertices.append(edge.start)
            vertices.append(edge.end)
        self._search_tree = rtree.RTree(vertices)

    def vertices_in_sphere(self, center: Vec3, radius: float) -> Sequence[Vec3]:
        """Returns all vertices located around `center` with a max. distance of `radius`."""
        return tuple(self._search_tree.points_in_sphere(center, radius))  # type: ignore

    def nearest_vertex(self, location: Vec3) -> Vec3:
        """Returns the nearest vertex to the given location."""
        vertex, _ = self._search_tree.nearest_neighbor(location)
        return vertex  # type: ignore


def discard_edges(edges: Iterable[Edge], discard: Iterable[Edge]) -> Sequence[Edge]:
    return discard_ids(edges, ids=set(e.id for e in discard))


def discard_ids(edges: Iterable[Edge], ids: set[int]) -> Sequence[Edge]:
    return tuple(e for e in edges if e.id not in ids)


class EdgeDeposit:
    def __init__(self, edges: Sequence[Edge], gap_tol=GAP_TOL) -> None:
        self.gap_tol = gap_tol
        self.edge_index = EdgeVertexIndex(edges)
        self.search_index = SearchIndex(edges)

    def edges_linked_to(self, vertex: UVec, radius: float = -1) -> Sequence[Edge]:
        """Returns all edges linked to `vertex` in range of `radius`.

        Default radius is :attr:`self.gap_tol`.
        """
        if radius < 0:
            radius = self.gap_tol
        vertices = self.search_index.vertices_in_sphere(Vec3(vertex), radius)
        if not vertices:
            return tuple()
        return self.edge_index.find_edges(vertices)

    def find_nearest_edge(self, vertex: UVec) -> Edge | None:
        """Return the nearest edge to the given vertex.

        The distance is measured to the connection line from start to end of the edge.
        This is not correct for edges that represent arcs or splines.
        """

        def distance(edge: Edge) -> float:
            return distance_point_line_3d(vertex, edge.start, edge.end)

        vertex = Vec3(vertex)
        si = self.search_index
        nearest_vertex = si.nearest_vertex(vertex)
        edges = self.edges_linked_to(nearest_vertex)
        if edges:
            return min(edges, key=distance)
        return None

    def build_network(self, edge: Edge, timeout=TIMEOUT) -> Network:
        """Returns the network of all edges that are directly and indirectly linked to
        `edge`.

        Raises:
            TimeoutError: build process has timed out
        """

        def process(vertex: Vec3) -> None:
            linked_edges = self.edges_linked_to(vertex)
            linked_edges = discard_ids(linked_edges, ids=found)
            if linked_edges:
                found.update(e.id for e in linked_edges)
                network.add_connections(edge, linked_edges)
                todo.extend(linked_edges)

        network = Network()
        found = set([edge.id])
        todo: list[Edge] = [edge]
        watchdog = Watchdog(timeout)

        while todo:
            watchdog.check_timeout("build process has timed out")
            edge = todo.pop()
            process(edge.start)
            process(edge.end)

        return network


class Network:
    def __init__(self) -> None:
        self._edges: dict[int, Edge] = {}
        self._connections: dict[int, set[int]] = defaultdict(set)

    def __len__(self) -> int:
        return len(self._edges)

    def __iter__(self) -> Iterator[Edge]:
        return iter(self._edges.values())

    def __contains__(self, edge: Edge) -> bool:
        return edge.id in self._edges

    def add_connection(self, base: Edge, target: Edge) -> None:
        self._edges[base.id] = base
        self._edges[target.id] = target
        self._connections[base.id].add(target.id)
        self._connections[target.id].add(base.id)

    def add_connections(self, base: Edge, targets: Iterable[Edge]) -> None:
        for target in targets:
            self.add_connection(base, target)

    def edges_linked_to(self, edge: Edge) -> Sequence[Edge]:
        return tuple(self._edges[eid] for eid in self._connections[edge.id])
