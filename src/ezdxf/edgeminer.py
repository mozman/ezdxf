# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
"""
EdgeMiner
=========

A module for detecting linked edges.

The complementary module ezdxf.edgesmith can create entities from the output of this 
module.

Terminology
-----------

I try to use the terminology of `Graph Theory`_ but there are differences where I think
a different term is better suited for this module like loop for cycle.

Edge (in this module)
    An edge has:
        - unique id
        - 3D start point (vertex)
        - 3D end point (vertex)
        - optional length
        - optional payload (arbitrary data)

    The geometry of an edge is not known.
    Intersection points of edges are not known and cannot be calculated.

Vertex
    A connection point of two or more edges. 
    The degree of a vertex is the number of connected edges.

Leaf
    A leaf is a vertex of degree 1.
    A leaf is a loose end of an edge, which is not connected to other edges.

Junction
    A junction is a vertex of degree > 2.
    A junction has more than two adjacent edges.
    A junction is an ambiguity when seaarching for open chains or closed loops.

Chain
    A chain has sequential connected edges. 
    The end point of an edge is connected to the start point of the following edge. 
    A chain has unique edges, each edge appears only once in the chain.
    A loop can contain vertices with a degree > 2.
    A solitary edge is also a chain.
    Chains are represented as Sequence[Edge].

Basic Chain
    A basic chain is a chain. 
    A basic chain contains only vertices of degree <= 2, but the end vertices may have 
    a higher degree.  These are the connected edges between vertices of degree != 2, 
    vertices with more than two adjacent edges or leafs.

Open Chain
    An open chain is a chain with at least one loose end (leaf). 
    A loose end is an edge point without a connection to other edges. 
    A solitary edge is also an open chain.

Loop
    A loop is a chain with two or more edges.
    The end point of the last edge is connected to the start point of the first edge.
    A loop can contain vertices with a degree > 2 like the number 8.
    A solitary edge is not a loop.

    .. Note:: 
    
        In `Graph Theory`_ this loop would be a cycle and a loop in Graph Theory is 
        something different.

Network
    A network has two or more edges that are directly and indirectly connected. 
    The edges in a network have no order.
    A network can contain vertices with a degree > 2, these are crossings with two or 
    more connected edges. (multiple adjacency)
    A solitary edge is not a network. 
    A chain with two or more edges is a network. 
    Networks are represented as Sequence[Edge].

    .. Note::
        
        In `Graph Theory`_   this is a multigraph, a network in Graph Theory 
        is something different.

Gap Tolerance
    Maximum vertex distance to consider two edges as connected

Forward Connection
    An edge is forward connected when the end point of the edge is connected to the 
    start point of the following edge.

Backwards Connection
    An edge is backwards connected when the start point of the edge is connected to the 
    end point of the previous edge.

.. versionadded:: 1.4

.. _Graph Theory: https://en.wikipedia.org/wiki/Glossary_of_graph_theory

"""
from __future__ import annotations
from typing import Any, Sequence, Iterator, Iterable, Dict, Tuple
from typing_extensions import Self, TypeAlias
from collections import Counter
import time

from ezdxf.math import UVec, Vec3, distance_point_line_3d
from ezdxf.math import rtree


__all__ = [
    "count_degrees",
    "Edge",
    "EdgeDeposit",
    "find_all_basic_chains",
    "find_all_loops",
    "find_all_sequential",
    "find_loop",
    "find_open_chains",
    "find_sequential",
    "flatten",
    "is_backwards_connected",
    "is_chain",
    "is_forward_connected",
    "is_loop",
    "is_wrapped_chain",
    "length",
    "longest_chain",
    "shortest_chain",
    "TimeoutError",
    "unique_chains",
    "unwrap_chain",
    "wrap_chain",
]
GAP_TOL = 1e-9
TIMEOUT = 60.0  # in seconds


class EdgeMinerException(Exception): ...


class InternalError(EdgeMinerException): ...


class TimeoutError(EdgeMinerException):
    def __init__(self, msg: str, solutions: Sequence[Sequence[Edge]] = tuple()) -> None:
        super().__init__(msg)
        self.solutions = solutions


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
        is_reverse: flag to indicate that the edge is reversed compared to its initial state
        length: length of the edge, default is the distance between start- and end vertex
        payload: arbitrary data associated to the edge
    """

    __slots__ = ("id", "start", "end", "is_reverse", "length", "payload")
    _next_id = 1

    def __init__(
        self, start: UVec, end: UVec, length: float = -1.0, payload: Any = None
    ) -> None:
        self.id = Edge._next_id  # unique id but reversed copies have the same id
        Edge._next_id += 1
        self.start = Vec3(start)
        self.end = Vec3(end)
        self.is_reverse: bool = False
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
        payload = self.payload
        if payload is None:
            content = str(self.id)
        elif isinstance(payload, EdgeWrapper):
            content = "[" + (",".join(repr(e) for e in payload.edges)) + "]"
        else:
            content = str(payload)
        return f"Edge({content})"

    def __hash__(self) -> int:
        # edges can be used in sets and set-operations
        return self.id

    def reversed(self) -> Self:
        """Returns a reversed copy."""
        edge = self.__class__(self.end, self.start, self.length, self.payload)
        edge.is_reverse = not self.is_reverse
        edge.id = self.id  # reversed copies represent the same edge
        return edge


def isclose(a: Vec3, b: Vec3, gap_tol=GAP_TOL) -> bool:
    """This function should be used to test whether two vertices are close to each other
    to get consistent results.
    """
    return a.distance(b) <= gap_tol


def is_forward_connected(a: Edge, b: Edge, gap_tol=GAP_TOL) -> bool:
    """Returns ``True`` if the edges have a forward connection.

    Forward connection: distance from a.end to b.start <= gap_tol

    Args:
        a: first edge
        b: second edge
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    return isclose(a.end, b.start, gap_tol)


def is_backwards_connected(a: Edge, b: Edge, gap_tol=GAP_TOL) -> bool:
    """Returns ``True`` if the edges have a backwards connection.

    Backwards connection: distance from b.end to a.start <= gap_tol

    Args:
        a: first edge
        b: second edge
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    return isclose(a.start, b.end, gap_tol)


def is_chain(edges: Sequence[Edge], gap_tol=GAP_TOL) -> bool:
    """Returns ``True`` if all edges have a forward connection.

    Args:
        edges: sequence of edges
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    return all(is_forward_connected(a, b, gap_tol) for a, b in zip(edges, edges[1:]))


def is_loop(edges: Sequence[Edge], gap_tol=GAP_TOL) -> bool:
    """Return ``True`` if the sequence of edges is a closed loop.

    Args:
        edges: sequence of edges
        gap_tol: maximum vertex distance to consider two edges as connected
    """
    if not is_chain(edges, gap_tol):
        return False
    return isclose(edges[-1].end, edges[0].start, gap_tol)


def is_loop_fast(edges: Sequence[Edge], gap_tol=GAP_TOL) -> bool:
    """Internal fast loop check."""
    return isclose(edges[-1].end, edges[0].start, gap_tol)


def length(edges: Sequence[Edge]) -> float:
    """Returns the length of a sequence of edges."""
    return sum(e.length for e in edges)


def shortest_chain(chains: Iterable[Sequence[Edge]]) -> Sequence[Edge]:
    """Returns the shortest chain of connected edges.

    .. note::

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


def find_sequential(edges: Sequence[Edge], gap_tol=GAP_TOL) -> Sequence[Edge]:
    """Returns all consecutive connected edges starting from the first edge.

    The search stops at the first edge without a forward connection from the previous
    edge. Edges are reversed if necessary to create a forward connection. This means
    that the :attr:`Edge.reverse` flag is ``True`` ad start and end vertices are swapped,
    the attached payload is not changed.

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


def find_all_sequential(
    edges: Sequence[Edge], gap_tol=GAP_TOL
) -> Iterator[Sequence[Edge]]:
    """Yields all edge chains with consecutive connected edges starting from the first
    edge. This search starts a new sequence at every edge without a forward connection
    from the previous sequence. Each sequence has always one or more edges.

    Args:
        edges: sequence of edges
        gap_tol: maximum vertex distance to consider two edges as connected

    Raises:
        TypeError: invalid data in sequence `edges`
    """
    while edges:
        chain = find_sequential(edges, gap_tol)
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


def find_loop(
    edges: Sequence[Edge], gap_tol=GAP_TOL, timeout=TIMEOUT
) -> Sequence[Edge]:
    """Returns the first closed loop found in `edges`.

    Returns only simple loops, where all vertices have only two adjacent edges.

    .. note::

        Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edges: sequence of edges
        gap_tol: maximum vertex distance to consider two edges as connected
        timeout: timeout in seconds

    Raises:
        TimeoutError: search process has timed out
        TypeError: invalid data in sequence `edges`
    """
    chains = find_all_basic_chains(edges, gap_tol)
    if not chains:
        return tuple()

    packed_edges: list[Edge] = []
    for chain in chains:
        if len(chain) > 1:
            if is_loop_fast(chain, gap_tol):
                return chain
            packed_edges.append(_wrap_chain(chain))
        else:
            packed_edges.append(chain[0])
    deposit = EdgeDeposit(packed_edges, gap_tol)
    if len(deposit.edges) < 2:
        return tuple()
    return tuple(flatten(find_loop_in_deposit(deposit, timeout=timeout)))


def find_loop_in_deposit(deposit: EdgeDeposit, timeout=TIMEOUT) -> Sequence[Edge]:
    """Returns the first closed loop found in edge `deposit`.

    Returns only simple loops, where all vertices have only two adjacent edges.

    .. note::

        Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        deposit: edge deposit
        timeout: timeout in seconds

    Raises:
        TimeoutError: search process has timed out
    """

    if len(deposit.edges) < 2:
        return tuple()

    finder = LoopFinder(deposit, timeout=timeout)
    loop = finder.find_any_loop()
    if loop:
        return loop
    return tuple()


def find_all_loops(
    edges: Sequence[Edge], gap_tol=GAP_TOL, timeout=TIMEOUT
) -> Sequence[Sequence[Edge]]:
    """Returns all closed loops and doesn't include reversed solutions.

    Returns only simple loops, where all vertices have only two adjacent edges. 
    All vertices have a degree of 2.

    .. note::

        Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edges: sequence of edges
        gap_tol: maximum vertex distance to consider two edges as connected
        timeout: timeout in seconds

    Raises:
        TimeoutError: search process has timed out
        TypeError: invalid data in sequence `edges`
    """
    chains = find_all_basic_chains(edges, gap_tol)
    if not chains:
        return tuple()

    solutions: list[Sequence[Edge]] = []
    packed_edges: list[Edge] = []
    for chain in chains:
        if len(chain) > 1:
            if is_loop_fast(chain, gap_tol):
                # these loops have no ambiguities (junctions)
                solutions.append(chain)
            else:
                packed_edges.append(_wrap_chain(chain))
        else:
            packed_edges.append(chain[0])

    if not packed_edges:
        return solutions

    deposit = EdgeDeposit(packed_edges, gap_tol)
    if len(deposit.edges) < 2:
        return tuple()
    try:
        result = find_all_loops_in_deposit(deposit, timeout=timeout)
    except TimeoutError as err:
        if err.solutions:
            solutions.extend(err.solutions)
            err.solutions = solutions
        raise
    solutions.extend(result)
    return _unwrap_chains(solutions)


def find_all_loops_in_deposit(
    deposit: EdgeDeposit, timeout=TIMEOUT
) -> Sequence[Sequence[Edge]]:
    """Returns all closed loops in found in the edge `deposit` and doesn't include 
    reversed solutions.

    Returns only simple loops, where all vertices have only two adjacent edges. 
    All vertices have a degree of 2.

    .. note::

        Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        deposit: edge deposit
        timeout: timeout in seconds

    Raises:
        TimeoutError: search process has timed out
    """
    solutions: list[Sequence[Edge]] = []
    finder = LoopFinder(deposit, timeout=timeout)
    for edge in deposit.edges:
        finder.search(edge)
    solutions.extend(finder)
    return solutions


def unique_chains(chains: Sequence[Sequence[Edge]]) -> Iterator[Sequence[Edge]]:
    """Filter duplicate chains and yields only unique chains.

    Yields the first chain for chains which have the same set of edges. The order of the
    edges is not important.
    """
    seen: set[frozenset[int]] = set()
    for chain in chains:
        key = frozenset(edge.id for edge in chain)
        if not key in seen:
            yield chain
            seen.add(key)


def type_check(edges: Sequence[Edge]) -> Sequence[Edge]:
    for edge in edges:
        if not isinstance(edge, Edge):
            raise TypeError(f"expected type <Edge>, got {str(type(edge))}")
    return edges


class EdgeVertex(Vec3):
    # for unknown reasons super().__init__(location) doesn't work, therefor no
    # EdgeVertex.__init__(self, location: Vec3, edge: Edge) constructor
    edge: Edge


def make_edge_vertex(location: Vec3, edge: Edge) -> EdgeVertex:
    edge_vertex = EdgeVertex(location)
    edge_vertex.edge = edge
    return edge_vertex


class SpatialSearchIndex:
    """Spatial search index of all edge vertices.

    (internal class)
    """

    def __init__(self, edges: Sequence[Edge]) -> None:
        vertices: list[EdgeVertex] = []
        for edge in edges:
            vertices.append(make_edge_vertex(edge.start, edge))
            vertices.append(make_edge_vertex(edge.end, edge))
        self._search_tree = rtree.RTree(vertices)

    def vertices_in_sphere(self, center: Vec3, radius: float) -> Sequence[EdgeVertex]:
        """Returns all vertices located around `center` with a max. distance of `radius`."""
        return tuple(self._search_tree.points_in_sphere(center, radius))

    def nearest_vertex(self, location: Vec3) -> EdgeVertex:
        """Returns the nearest vertex to the given location."""
        vertex, _ = self._search_tree.nearest_neighbor(location)
        return vertex


class EdgeDeposit:
    """The edge deposit stores all available edges for further searches."""

    def __init__(self, edges: Sequence[Edge], gap_tol=GAP_TOL) -> None:
        self.gap_tol = gap_tol
        self.edges = type_check(tuple(edges))
        self.search_index = SpatialSearchIndex(self.edges)

    def count_degrees(self) -> Counter[int]:
        """Returns a degree counter for all vertices."""
        counter: Counter[int] = Counter()
        search = self.search_index.vertices_in_sphere
        gap_tol = self.gap_tol
        for edge in self.edges:
            counter[len(search(edge.start, gap_tol))] += 1
            counter[len(search(edge.end, gap_tol))] += 1
        return Counter({k: v // k for k, v in counter.items()})

    def max_degree(self) -> int:
        """Returns the maximum degree of all vertices."""
        return max(self.count_degrees().keys())

    def edges_linked_to(self, vertex: UVec, radius: float = -1) -> Sequence[Edge]:
        """Returns all edges linked to `vertex` in range of `radius`.

        Default radius is :attr:`self.gap_tol`.
        """
        if radius < 0:
            radius = self.gap_tol
        vertices = self.search_index.vertices_in_sphere(Vec3(vertex), radius)
        return tuple(v.edge for v in vertices)

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

    def find_network(self, edge: Edge) -> set[Edge]:
        """Returns the network of all edges that are directly and indirectly linked to
        `edge`.  A network has two or more edges, a solitary edge is not a network.
        """

        def process(vertex: Vec3) -> None:
            linked_edges = set(self.edges_linked_to(vertex)) - network
            if linked_edges:
                network.update(linked_edges)
                todo.extend(linked_edges)

        todo: list[Edge] = [edge]
        network: set[Edge] = set(todo)
        while todo:
            edge = todo.pop()
            process(edge.start)
            process(edge.end)
        if len(network) > 1:  # a network requires two or more edges
            return network
        return set()

    def find_all_networks(self) -> Sequence[set[Edge]]:
        """Returns all separated networks in this deposit in ascending order of edge
        count.
        """
        edges = set(self.edges)
        networks: list[set[Edge]] = []
        while edges:
            edge = edges.pop()
            network = self.find_network(edge)
            if len(network):
                networks.append(network)
                edges -= network
            else:  # solitary edge
                edges.discard(edge)

        networks.sort(key=lambda n: len(n))
        return networks

    def find_leafs(self) -> Iterator[Edge]:
        """Yields all edges that have at least one end point without connection to other
        edges.
        """
        for edge in self.edges:
            if len(self.edges_linked_to(edge.start)) == 1:
                yield edge
            elif len(self.edges_linked_to(edge.end)) == 1:
                yield edge


def count_degrees(edges: Sequence[Edge], gap_tol=GAP_TOL) -> Counter[int]:
    """Returns a degree counter for all edge vertices."""
    return EdgeDeposit(edges, gap_tol).count_degrees()


SearchSolutions: TypeAlias = Dict[Tuple[int, ...], Sequence[Edge]]


class LoopFinder:
    """Find closed loops in an EdgeDeposit by a recursive backtracking algorithm.

    Finds only simple loops, where all vertices have only two adjacent edges.

    (internal class)
    """

    def __init__(self, deposit: EdgeDeposit, timeout=TIMEOUT) -> None:
        if len(deposit.edges) < 2:
            raise ValueError("two or more edges required")
        self._deposit = deposit
        self._timeout = timeout
        self._solutions: SearchSolutions = {}

    @property
    def gap_tol(self) -> float:
        return self._deposit.gap_tol

    def __iter__(self) -> Iterator[Sequence[Edge]]:
        return iter(self._solutions.values())

    def __len__(self) -> int:
        return len(self._solutions)

    def find_any_loop(self, start: Edge | None = None) -> Sequence[Edge]:
        """Returns the first loop found beginning with the given start edge or an
        arbitrary edge if `start` is None.
        """
        if start is None:
            start = self._deposit.edges[0]

        self.search(start, stop_at_first_loop=True)
        try:
            return next(iter(self._solutions.values()))
        except StopIteration:
            return tuple()

    def search(self, start: Edge, stop_at_first_loop: bool = False) -> None:
        """Searches for all loops that begin at the given start edge and contain
        only vertices of degree 2.

        These are not all possible loops in the edge deposit!

        Raises:
            TimeoutError: search process has timed out, intermediate results are attached
                TimeoutError.data

        """
        deposit = self._deposit
        gap_tol = self.gap_tol
        start_point = start.start
        watchdog = Watchdog(self._timeout)
        todo: list[tuple[Edge, ...]] = [(start,)]  # "unlimited" recursion stack
        while todo:
            if watchdog.has_timed_out:
                raise TimeoutError(
                    "search process has timed out",
                    solutions=tuple(self._solutions.values()),
                )
            chain = todo.pop()
            last_edge = chain[-1]
            end_point = last_edge.end
            candidates = deposit.edges_linked_to(end_point, radius=gap_tol)
            # edges must be unique in a loop
            survivers = set(candidates) - set(chain)
            for edge in survivers:
                if isclose(end_point, edge.start, gap_tol):
                    next_edge = edge
                else:
                    next_edge = edge.reversed()
                last_point = next_edge.end
                if isclose(last_point, start_point, gap_tol):
                    self.add_solution(chain + (next_edge,))
                    if stop_at_first_loop:
                        return
                # Add only chains to the stack that have vertices of max degree 2.
                # If the new end point is in the chain, a vertex of degree 3 would be
                # created. (loop check is done)
                elif not any(last_point.distance(e.end) < gap_tol for e in chain):
                    todo.append(chain + (next_edge,))

    def add_solution(self, loop: Sequence[Edge]) -> None:
        solutions = self._solutions
        key = loop_key(loop)
        if key in solutions or loop_key(loop, reverse=True) in solutions:
            return
        solutions[key] = loop


def loop_key(edges: Sequence[Edge], reverse=False) -> tuple[int, ...]:
    """Returns a normalized key.

    The key is rotated to begin with the smallest edge id.
    """
    if reverse:
        ids = tuple(edge.id for edge in reversed(edges))
    else:
        ids = tuple(edge.id for edge in edges)
    index = ids.index(min(ids))
    if index:
        ids = ids[index:] + ids[:index]
    return ids


def find_all_basic_chains(
    edges: Sequence[Edge], gap_tol=GAP_TOL
) -> Sequence[Sequence[Edge]]:
    """Returns all basic chains and doesn't include reversed solutions.

    Basic chains are broken at junctions (vertices with more than 2 edges, degree > 2), 
    which means that all sequences have a linear progression without ambiguities.

    Args:
        edges: sequence of edges
        gap_tol: maximum vertex distance to consider two edges as connected

    Raises:
        TypeError: invalid data in sequence `edges`
    """
    deposit = EdgeDeposit(edges, gap_tol=gap_tol)
    if len(deposit.edges) < 1:
        return tuple()
    return find_all_basic_chains_in_deposit(deposit)


def find_all_basic_chains_in_deposit(deposit: EdgeDeposit) -> Sequence[Sequence[Edge]]:
    """Returns all sequences of connected edges in the edge `deposit` and doesn't
    include reversed solutions.

    The chains are broken at junctions (vertices with more than 2 edges, degree > 2), 
    which means that all sequences have a linear progression without ambiguities.
    """
    if len(deposit.edges) < 1:
        return tuple()
    solutions: list[Sequence[Edge]] = []
    edges = set(deposit.edges)
    while edges:
        chain = find_chain_in_deposit(deposit, edges.pop())
        solutions.append(chain)
        edges -= set(chain)
    return solutions


def find_chain_in_deposit(deposit: EdgeDeposit, start: Edge) -> Sequence[Edge]:
    """Returns the chain containing the `start` edge."""
    forward_chain = _find_forward_chain(deposit, start)
    if is_loop_fast(forward_chain, deposit.gap_tol):
        return forward_chain
    backwards_chain = _find_forward_chain(deposit, start.reversed())
    if len(backwards_chain) == 1:
        return forward_chain
    backwards_chain.reverse()
    backwards_chain.pop()  # reversed start
    return [edge.reversed() for edge in backwards_chain] + forward_chain


def _find_forward_chain(deposit: EdgeDeposit, edge: Edge) -> list[Edge]:
    gap_tol = deposit.gap_tol
    chain = [edge]
    while True:
        last = chain[-1]
        linked = deposit.edges_linked_to(last.end, gap_tol)
        if len(linked) != 2:  # no junctions allowed!
            return chain
        if linked[0] == last:
            edge = linked[1]
        else:
            edge = linked[0]
        if isclose(last.end, edge.start, gap_tol):
            chain.append(edge)
        else:
            chain.append(edge.reversed())
        if is_loop_fast(chain, gap_tol):
            return chain


def is_wrapped_chain(edge: Edge) -> bool:
    """Returns ``True`` if `edge` is a wrapper for linked edges."""
    return isinstance(edge.payload, EdgeWrapper)


def wrap_chain(chain: Sequence[Edge], gap_tol=GAP_TOL) -> Edge:
    """Wraps a sequence of linked edges into a single edge.

    Two or more linked edges required. Closed loops cannot be wrapped into a single
    edge.

    Raises:
        ValueError: less than two edges; not a chain; chain is a closed loop

    """
    if len(chain) < 2:
        raise ValueError("two or more linked edges required")
    if is_chain(chain, gap_tol):
        if is_loop_fast(chain, gap_tol):
            raise ValueError("closed loop cannot be wrapped into a single edge")
        return _wrap_chain(chain)
    raise ValueError("edges are not connected")


def unwrap_chain(edge: Edge) -> Sequence[Edge]:
    """Unwraps linked edges which are wrapped into a single edge."""
    if isinstance(edge.payload, EdgeWrapper):
        return _unwrap_chain(edge)
    return (edge,)


class EdgeWrapper:
    """Internal class to wrap a sequence of linked edges."""

    __slots__ = ("edges",)

    def __init__(self, edges: Sequence[Edge]) -> None:
        self.edges: Sequence[Edge] = tuple(edges)


def _wrap_chain(edges: Sequence[Edge]) -> Edge:
    return Edge(
        edges[0].start, edges[-1].end, length(edges), payload=EdgeWrapper(edges)
    )


def _unwrap_chain(edge: Edge) -> Sequence[Edge]:
    wrapper = edge.payload
    assert isinstance(wrapper, EdgeWrapper)
    if edge.is_reverse:
        return tuple(e.reversed() for e in reversed(wrapper.edges))
    else:
        return wrapper.edges


def _unwrap_chains(chains: Iterable[Iterable[Edge]]) -> Sequence[Sequence[Edge]]:
    return tuple(tuple(flatten(chain)) for chain in chains)


def flatten(edges: Edge | Iterable[Edge]) -> Iterator[Edge]:
    """Yields all edges from any nested structure of edges as a flat stream of edges."""
    edge: Edge
    if not isinstance(edges, Edge):
        for edge in edges:
            yield from flatten(edge)
    else:
        edge = edges
        if is_wrapped_chain(edge):
            yield from flatten(_unwrap_chain(edge))
        else:
            yield edge


def find_open_chains(
    edges: Sequence[Edge], gap_tol=GAP_TOL, timeout=TIMEOUT
) -> Sequence[Sequence[Edge]]:
    """Returns all combinations of edges which create open chains with at least one
    loose end (leafs).  Returns only simple chains, where all vertices have only two or 
    less adjacent edges (degree <= 2).

    A loose end (leaf) is an edge end-point without further connections.  
    The result does not include reversed solutions and closed loops.

    .. note::

        Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edges: sequence of edges
        gap_tol: maximum vertex distance to consider two edges as connected
        timeout: timeout in seconds

    Raises:
        TypeError: invalid data in sequence `edges`
        TimeoutError: search process has timed out
    """
    return find_open_chains_in_deposit(EdgeDeposit(edges, gap_tol=gap_tol), timeout)


def chain_key(edges: Sequence[Edge], reverse=False) -> tuple[int, ...]:
    """Returns a normalized key."""
    if reverse:
        return tuple(edge.id for edge in reversed(edges))
    else:
        return tuple(edge.id for edge in edges)


def find_open_chains_in_deposit(
    deposit: EdgeDeposit, timeout=TIMEOUT
) -> Sequence[Sequence[Edge]]:
    """Returns all combinations of edges in deposit which create open chains with at
    least one loose end (leafs).  Returns only simple chains, where all vertices have 
    only two or less adjacent edges (degree <= 2).

    A loose end (leaf) is an edge end-point without further connections.  
    The result does not include reversed solutions and closed loops.

    .. note::

        Recursive backtracking algorithm with time complexity of O(n!).

    Args:
        edosit: EdgeDeposit
        timeout: timeout in seconds

    Raises:
        TimeoutError: search process has timed out
    """

    finder = OpenChainFinder(deposit, timeout)
    for edge in deposit.find_leafs():
        finder.search(edge)
    solutions = finder.solutions
    solutions.sort(key=lambda x: len(x))
    return solutions


class OpenChainFinder:
    def __init__(self, deposit: EdgeDeposit, timeout=TIMEOUT):
        self.deposit = deposit
        self.solution_keys: set[tuple[int, ...]] = set()
        self.solutions: list[Sequence[Edge]] = []
        self.watchdog = Watchdog(timeout)

    def search(self, edge: Edge) -> None:
        forward_chains = self.forward_search(edge)
        self.reverse_search(forward_chains)

    def forward_search(self, edge: Edge) -> list[tuple[Edge, ...]]:
        deposit = self.deposit
        gap_tol = deposit.gap_tol
        watchdog = self.watchdog

        forward_chains: list[tuple[Edge, ...]] = []
        todo: list[tuple[Edge, ...]] = [(edge,)]
        while todo:
            if watchdog.has_timed_out:
                raise TimeoutError("search has timed out")
            chain = todo.pop()
            start_point = chain[-1].end
            candidates = deposit.edges_linked_to(start_point)
            backwards_edges = set(candidates) - set(chain)
            if backwards_edges:
                for edge in backwards_edges:
                    if not isclose(start_point, edge.start, gap_tol):
                        edge = edge.reversed()
                    # Add only chains to the stack that have vertices of max degree 2.
                    # If the new end point is in the chain, a vertex of degree 3 would be
                    # created. (loop check is done)
                    last_point = edge.end
                    if not any(last_point.distance(e.end) < gap_tol for e in chain):
                        todo.append(chain + (edge,))

            else:
                forward_chains.append(chain)
        return forward_chains

    def reverse_search(self, forward_chains: list[tuple[Edge, ...]]) -> None:
        deposit = self.deposit
        gap_tol = deposit.gap_tol
        watchdog = self.watchdog
        todo = forward_chains
        while todo:
            if watchdog.has_timed_out:
                raise TimeoutError("search has timed out", solutions=self.solutions)
            chain = todo.pop()
            start_point = chain[0].start
            candidates = deposit.edges_linked_to(start_point)
            backwards_edges = set(candidates) - set(chain)
            if backwards_edges:
                for edge in backwards_edges:
                    if not isclose(start_point, edge.end, gap_tol):
                        edge = edge.reversed()
                    # Add only chains to the stack that have vertices of max degree 2.
                    # If the new end point is in the chain, a vertex of degree 3 would be
                    # created.
                    new_start_point = edge.start
                    if not any(
                        new_start_point.distance(e.end) < gap_tol for e in chain
                    ):
                        todo.append((edge,) + chain)
            else:
                self.add_solution(chain)

    def add_solution(self, solution: Sequence[Edge]) -> None:
        keys = self.solution_keys
        key = chain_key(solution)
        if key in keys:
            return
        keys.add(key)
        key = chain_key(solution, reverse=True)
        if key in keys:
            return
        keys.add(key)
        self.solutions.append(solution)


def find_closest_loop(
    edges: Sequence[Edge], pick: UVec, gap_tol=GAP_TOL, timeout=TIMEOUT
) -> Sequence[Edge]:
    """Returns the first loop found closest to the pick point."""
    return find_closest_loop_in_deposit(EdgeDeposit(edges, gap_tol), pick, timeout)


def find_closest_loop_in_deposit(
    deposit: EdgeDeposit, pick: UVec, timeout=TIMEOUT
) -> Sequence[Edge]:
    """Returns the first loop found closest to the pick point."""
    if len(deposit.edges) < 2:
        return tuple()

    gap_tol = deposit.gap_tol
    start = deposit.find_nearest_edge(pick)
    assert start is not None
    start_point = start.start
    loop = (start,)
    watchdog = Watchdog(timeout)
    while True:
        if watchdog.has_timed_out:
            raise TimeoutError("search has timed out")
        last_edge = loop[-1]
        end_point = last_edge.end
        if isclose(start_point, end_point, gap_tol):
            return loop
        candidates = set(deposit.edges_linked_to(end_point))
        for edge in candidates - set(loop):
            pass
