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
from typing import Any, Sequence, Iterator, Iterable, Dict, Tuple
from typing_extensions import Self, TypeAlias
from collections import defaultdict
import time

from ezdxf.math import UVec, Vec3, distance_point_line_3d
from ezdxf.math import rtree


__all__ = [
    "Edge",
    "EdgeDeposit",
    "find_all_loops_in_deposit",
    "find_all_loops",
    "find_first_loop_in_deposit",
    "find_first_loop",
    "is_backwards_connected",
    "is_chain",
    "is_forward_connected",
    "is_loop",
    "length",
    "longest_chain",
    "sequential_search_all",
    "sequential_search",
    "shortest_chain",
    "TimeoutError",
]
ABS_TOL = 1e-12
GAP_TOL = 1e-12
TIMEOUT = 60.0  # in seconds


class EdgeMinerException(Exception):
    pass


class TimeoutError(EdgeMinerException):
    pass



class Edge:
    """Represents an edge.

    The edge can represent any linear curve (line, arc, spline,...).
    Therefore, the length of the edge must be specified if the length calculation for
    a sequence of edges is to be possible.

    This class is immutable by design!

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

    def __repr__(self) -> str:
        if self.payload is None:
            content = str(self.id)
        else:
            content = str(self.payload)
        return f"Edge({content})"

    def __hash__(self) -> int:
        # edges can be used in sets and set-operations
        return self.id

    def reversed(self) -> Self:
        """Returns a reversed copy."""
        edge = self.__class__(self.end, self.start, self.length, self.payload)
        edge.reverse = not self.reverse
        edge.id = self.id  # reversed copies represent the same edge
        return edge


def isclose(a: Vec3, b: Vec3, gap_tol=GAP_TOL) -> bool:
    """This function should be used to test whether two vertices are close to each other
    to get consistent results.
    """
    return a.distance(b) <= gap_tol


def is_forward_connected(a: Edge, b: Edge, gap_tol=GAP_TOL) -> bool:
    """Returns ``True`` if the edges have a forward connection.
    
    Forward connection: a.end is connected to b.start

    Args:
        a: first edge
        b: second edge
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    return isclose(a.end, b.start, gap_tol)


def is_backwards_connected(a: Edge, b: Edge, gap_tol=GAP_TOL) -> bool:
    """Returns ``True`` if the edges have a backward connection.
    
    Backwards connection: a.start is connected to b.end

    Args:
        a: first edge
        b: second edge
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    return isclose(a.start, b.end, gap_tol)


def is_chain(edges: Sequence[Edge], gap_tol=GAP_TOL) -> bool:
    """Returns ``True`` if all edges are connected forward.
    
    Forward connection: edge[n].end is connected to edge[n+1].start

    Args:
        edges: sequence of edges
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    return all(is_forward_connected(a, b, gap_tol) for a, b in zip(edges, edges[1:]))


def is_loop(edges: Sequence[Edge], gap_tol=GAP_TOL, full=True) -> bool:
    """Return ``True`` if the sequence of edges is a closed forward loop.

    Forward connection: edge[n].end is connected to edge[n+1].start

    Args:
        edges: sequence of edges
        gap_tol: maximum vertex distance to consider two edges as connected
        full: does a full check if all edges are connected if ``True``, otherwise checks 
            only if the last edge is connected to the first edge.
    """
    if full and not is_chain(edges, gap_tol):
        return False
    return is_forward_connected(edges[-1], edges[0])


def length(edges: Sequence[Edge]) -> float:
    """Returns the length of a sequence of edges."""
    return sum(e.length for e in edges)


def shortest_chain(chains: Iterable[Sequence[Edge]]) -> Sequence[Edge]:
    """Returns the shortest chain of connected edges.

    .. Note::

        This function does not verify if the input sequences are connected edges!

    """
    sorted_chains = sorted(chains, key=length)
    if sorted_chains:
        return sorted_chains[0]
    return tuple()


def longest_chain(chains: Iterable[Sequence[Edge]]) -> Sequence[Edge]:
    """Returns the longest chain of connected edges.

    .. Note::

        This function does not verify if the input sequences are connected edges!

    """
    sorted_chains = sorted(chains, key=length)
    if sorted_chains:
        return sorted_chains[-1]
    return tuple()


def sequential_search(edges: Sequence[Edge], gap_tol=GAP_TOL) -> Sequence[Edge]:
    """Returns all consecutive connected edges starting from the first edge.

    The search stops at the first edge without a connection.

    Args:
        edges: edges to be examined
        gap_tol: maximum vertex distance to consider two edges as connected

    Raises:
        TypeError: invalid data in sequence `edges`
    """
    edges = type_check(edges)
    if len(edges) < 2:
        return edges
    chain = [edges[0]]
    for edge in edges[1:]:
        last = chain[-1]
        if is_forward_connected(last, edge, gap_tol):
            chain.append(edge)
            continue
        reversed_edge = edge.reversed()
        if is_forward_connected(last, reversed_edge, gap_tol):
            chain.append(reversed_edge)
            continue
        break
    return chain


def sequential_search_all(
    edges: Sequence[Edge], gap_tol=GAP_TOL
) -> Iterator[Sequence[Edge]]:
    """Yields all edge strings with consecutive connected edges starting from the first
    edge.  This search starts a new sequence at every edge without a connection to
    the previous sequence.  Each sequence has one or more edges, yields no empty sequences.

    Args:
        edges: edges to be examined
        gap_tol: maximum vertex distance to consider two edges as connected

    Raises:
        TypeError: invalid data in sequence `edges`
    """
    while edges:
        chain = sequential_search(edges, gap_tol)
        edges = edges[len(chain) :]
        yield chain


class Watchdog:
    def __init__(self, timeout=TIMEOUT) -> None:
        self.timeout: float = timeout
        self.start_time: float = time.perf_counter()

    def start(self, timeout: float):
        self.timeout = timeout
        self.start_time = time.perf_counter()

    @property
    def has_timed_out(self) -> bool:
        return time.perf_counter() - self.start_time > self.timeout


def find_first_loop(
    edges: Sequence[Edge], gap_tol=GAP_TOL, timeout=TIMEOUT
) -> Sequence[Edge]:
    """Returns the first closed loop found in `edges`.

    .. Note:: 
    
        Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edges: edges to be examined
        gap_tol: maximum vertex distance to consider two edges as connected
        timeout: timeout in seconds

    Raises:
        TimeoutError: search process has timed out
        TypeError: invalid data in sequence `edges`
    """
    deposit = EdgeDeposit(edges, gap_tol=gap_tol)
    if len(deposit.edges) < 2:
        return tuple()
    return find_first_loop_in_deposit(deposit, timeout=timeout)


def find_first_loop_in_deposit(deposit: EdgeDeposit, timeout=TIMEOUT) -> Sequence[Edge]:
    """Returns the first closed loop found in edge `deposit`.

    .. Note:: 
    
        Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        deposit: edge deposit
        timeout: timeout in seconds

    Raises:
        TimeoutError: search process has timed out
    """

    if len(deposit.edges) < 2:
        return tuple()
    networks = list(deposit.build_all_networks(timeout=timeout))
    for network in networks:
        finder = LoopFinder(network, timeout=timeout)
        loop = finder.find_any_loop()
        if loop:
            return loop
    return tuple()


def find_all_loops(
    edges: Sequence[Edge], gap_tol=GAP_TOL, timeout=TIMEOUT
) -> Sequence[Sequence[Edge]]:
    """Returns all unique closed loops and doesn't include reversed solutions.

    .. Note:: 
    
        Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edges: edges to be examined
        gap_tol: maximum vertex distance to consider two edges as connected
        timeout: timeout in seconds

    Raises:
        TimeoutError: search process has timed out
        TypeError: invalid data in sequence `edges`
    """
    deposit = EdgeDeposit(edges, gap_tol=gap_tol)
    if len(deposit.edges) < 2:
        return tuple()
    return find_all_loops_in_deposit(deposit, timeout=timeout)


def find_all_loops_in_deposit(
    deposit: EdgeDeposit, timeout=TIMEOUT
) -> Sequence[Sequence[Edge]]:
    """Returns all unique closed loops in found in the edge `deposit` and doesn't
    include reversed solutions.

    .. Note:: 
    
        Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        deposit: edge deposit
        timeout: timeout in seconds

    Raises:
        TimeoutError: search process has timed out
    """
    gap_tol = deposit.gap_tol
    solutions: list[Sequence[Edge]] = []
    for network in deposit.build_all_networks(timeout=timeout):
        finder = LoopFinder(network, gap_tol=gap_tol, timeout=timeout)
        for edge in network:
            finder.search(edge)
        solutions.extend(finder)
    return solutions


def type_check(edges: Sequence[Edge]) -> Sequence[Edge]:
    for edge in edges:
        if not isinstance(edge, Edge):
            raise TypeError(f"expected type <Edge>, got {str(type(edge))}")
    return edges


class Loop:
    """Represents connected edges.

    Each end vertex of an edge is connected to the start vertex of the following edge.
    It is a closed loop when the first edge is connected to the last edge.

    (internal helper class)
    """

    def __init__(self, edges: tuple[Edge, ...]) -> None:
        self.edges: tuple[Edge, ...] = edges

    def __repr__(self) -> str:
        content = ",".join(str(e) for e in self.edges)
        return f"Loop([{content}])"

    def __len__(self) -> int:
        return len(self.edges)

    def is_connected(self, edge: Edge, gap_tol=GAP_TOL) -> bool:
        """Returns ``True`` if the last edge of the loop is connected to the given edge.

        Args:
            edge: edge to be examined
            gap_tol: maximum vertex distance to consider two edges as connected
        """
        if self.edges:
            return isclose(self.edges[-1].end, edge.start, gap_tol)
        return False

    def is_closed_loop(self, gap_tol=GAP_TOL) -> bool:
        """Returns ``True`` if the first edge is connected to the last edge.

        Args:
            gap_tol: maximum vertex distance to consider two edges as connected
        """

        if len(self.edges) > 1:
            return isclose(self.edges[0].start, self.edges[-1].end, gap_tol)
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

    def ordered(self, reverse=False) -> Iterator[Edge]:
        """Returns the loop edges in key order."""
        edges = {e.id: e for e in self.edges}
        return (edges[eid] for eid in self.key(reverse))


SearchSolutions: TypeAlias = Dict[Tuple[int, ...], Tuple[Edge, ...]]


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


class SpatialSearchIndex:
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
    """The edge deposit stores all available edges for further searches."""

    def __init__(self, edges: Sequence[Edge], gap_tol=GAP_TOL) -> None:
        self.gap_tol = gap_tol
        self.edges = type_check(tuple(edges))
        self.edge_index = EdgeVertexIndex(self.edges)
        self.search_index = SpatialSearchIndex(self.edges)

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
            linked_edges = discard_ids(linked_edges, ids=done)
            if linked_edges:
                network.add_connections(edge, linked_edges)
                todo.extend(linked_edges)

        network = Network()
        done: set[int] = set()
        todo: list[Edge] = [edge]
        watchdog = Watchdog(timeout)

        while todo:
            if watchdog.has_timed_out:
                raise TimeoutError("build process has timed out")
            edge = todo.pop()
            done.add(edge.id)
            process(edge.start)
            process(edge.end)

        return network

    def build_all_networks(self, timeout=TIMEOUT) -> Sequence[Network]:
        """Returns all separated networks in this deposit in ascending order of edge
        count.

        Raises:
            TimeoutError: build process has timed out
        """
        watchdog = Watchdog(timeout)
        edges = set(self.edges)
        networks: list[Network] = []
        while edges:
            if watchdog.has_timed_out:
                raise TimeoutError("search process has timed out")
            edge = edges.pop()
            network = self.build_network(edge, timeout=timeout)
            if len(network):
                networks.append(network)
                edges -= set(network)
            else:  # solitary edge
                edges.discard(edge)

        networks.sort(key=lambda n: len(n))
        return networks


class Network:
    """The all edges in a network are reachable from every other edge."""

    def __init__(self) -> None:
        self._edges: dict[int, Edge] = {}
        self._connections: dict[int, set[int]] = defaultdict(set)

    def __repr__(self) -> str:
        content = ",".join(str(e) for e in self)
        return f"Network([{content}])"

    def __len__(self) -> int:
        return len(self._edges)

    def __iter__(self) -> Iterator[Edge]:
        return iter(self._edges.values())

    def __contains__(self, edge: Edge) -> bool:
        return edge.id in self._edges

    def add_connection(self, base: Edge, target: Edge) -> None:
        if base.id == target.id:
            return
        self._edges[base.id] = base
        self._edges[target.id] = target
        self._connections[base.id].add(target.id)
        self._connections[target.id].add(base.id)

    def add_connections(self, base: Edge, targets: Iterable[Edge]) -> None:
        for target in targets:
            self.add_connection(base, target)

    def edges_linked_to(self, edge: Edge) -> Sequence[Edge]:
        return tuple(self._edges[eid] for eid in self._connections[edge.id])


class LoopFinder:
    def __init__(
        self, network: Network, discard_reverse=True, gap_tol=GAP_TOL, timeout=TIMEOUT
    ) -> None:
        if len(network) < 2:
            raise ValueError("two or more network nodes required")
        self._network = network
        self._discard_reverse_solutions = discard_reverse
        self._gap_tol = gap_tol
        self._timeout = timeout
        self._solutions: SearchSolutions = {}

    def __iter__(self) -> Iterator[Sequence[Edge]]:
        return iter(self._solutions.values())

    def __len__(self) -> int:
        return len(self._solutions)

    def find_any_loop(self, start: Edge | None = None) -> Sequence[Edge]:
        """Returns the first loop found beginning with the given start edge or an
        arbitrary edge if `start` is None.
        """
        if start is None:
            start = next(iter(self._network))

        self.search(start, stop_at_first_loop=True)
        try:
            return next(iter(self._solutions.values()))
        except StopIteration:
            return tuple()

    def search(self, start: Edge, stop_at_first_loop: bool = False) -> None:
        """Searches for all loops that begin at the given start edge.

        These are not all possible loops in a network!
        """
        if start not in self._network:
            raise ValueError("start edge not in network")
        network = self._network
        gap_tol = self._gap_tol
        solutions = self._solutions

        watchdog = Watchdog(self._timeout)
        todo: list[Loop] = [Loop((start,))]  # "unlimited" recursion stack
        while todo:
            if watchdog.has_timed_out:
                raise TimeoutError("search process has timed out")
            loop = todo.pop()
            linked_edges = network.edges_linked_to(loop.edges[-1])
            # edges must be unique in a loop
            for edge in set(linked_edges) - set(loop.edges):
                extended_loop: Loop | None = None
                if loop.is_connected(edge):
                    extended_loop = Loop(loop.edges + (edge,))
                else:
                    reversed_edge = edge.reversed()
                    if loop.is_connected(reversed_edge):
                        extended_loop = Loop(loop.edges + (reversed_edge,))
                if extended_loop is None:
                    continue
                if extended_loop.is_closed_loop(gap_tol):
                    add_search_solution(
                        solutions, extended_loop, self._discard_reverse_solutions
                    )
                    if stop_at_first_loop:
                        return
                else:
                    todo.append(extended_loop)


def add_search_solution(
    solutions: SearchSolutions, loop: Loop, discard_reversed_loops: bool
) -> None:
    key = loop.key()
    if key in solutions:
        return
    if discard_reversed_loops and loop.key(reverse=True) in solutions:
        return
    solutions[key] = loop.edges
