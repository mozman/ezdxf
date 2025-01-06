# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Sequence
import pytest

from ezdxf import edgeminer as em
from ezdxf.math import Vec3, rtree


class TestBasicRequirements:
    @pytest.fixture(params=[Vec3, em._Vertex], scope="class")
    def abc(self, request):
        cls = request.param
        a = cls((1, 2, 3))
        b = cls((1, 2, 3))
        c = cls((1, 2, 3))
        return a, b, c

    def test_vec3_requirements(self, abc):
        a, b, c = abc

        # Same locations have unique identities.
        # Maybe future me decides to return the same instance for same locations as
        # optimization, because Vec3 is immutable!
        assert a is not b
        assert a is not c
        assert b is not c

        # equality is EXACT same location and vice versa
        # floating point equality on bit-level!
        assert a == b
        assert a == c
        assert b == c

        # EXACT same location has same hash
        assert hash(a) == hash(b)
        assert hash(a) == hash(c)
        assert hash(b) == hash(c)

    def test_rtree_requirements(self, abc):
        rt = rtree.RTree(abc)
        assert len(rt) == 3, "expected multiple entries for the same location"
        result = list(rt.points_in_sphere(Vec3(1, 2, 3), radius=0.1))
        assert len(result) == 3, "expected multiple entries for the same location"
        assert set([id(v) for v in abc]) == set(
            [id(v) for v in result]
        ), "expected the identical instances"


class TestEdge:
    def test_init(self):
        edge = em.make_edge((0, 0), (1, 0))
        assert edge.start == Vec3(0, 0)
        assert edge.end == Vec3(1, 0)
        assert edge.length == 1.0
        assert edge.is_reverse is False
        assert edge.payload is None

    def test_edge_is_immutable(self):
        edge = em.make_edge((0, 0), (1, 0))
        with pytest.raises(AttributeError):
            edge.id = 0

    def test_identity(self):
        edge0 = em.make_edge((0, 0), (1, 0))
        edge1 = em.make_edge((0, 0), (1, 0))
        assert edge0 == edge0
        assert edge0 != edge1, "each edge should have an unique identity"
        assert edge0 == edge0.reversed(), "reversed copies represent the same edge"

    def test_reversed_copy(self):
        edge = em.make_edge((0, 0), (1, 0))
        clone = edge.reversed()
        assert edge == clone
        assert edge.id == clone.id
        assert edge.start == clone.end
        assert edge.end == clone.start
        assert edge.length == clone.length
        assert edge.is_reverse is (not clone.is_reverse)
        assert edge.payload is clone.payload

    def test_edge_can_be_used_in_sets(self):
        A = em.make_edge((0, 0), (1, 0))
        B = em.make_edge((1, 0), (1, 1))
        C = em.make_edge((1, 1), (0, 1))

        s1 = set([A, B])
        s2 = set([C, B])
        result = s1.intersection(s2)
        assert len(result) == 1
        assert B in result


class SimpleLoops:
    #   0   1   2
    # 1 +-C-+-G-+
    #   |   |   |
    #   D   B   F
    #   |   |   |
    # 0 +-A-+-E-+

    A = em.make_edge((0, 0), (1, 0), length=0.5, payload="A")
    B = em.make_edge((1, 0), (1, 1), payload="B")
    C = em.make_edge((1, 1), (0, 1), payload="C")
    D = em.make_edge((0, 1), (0, 0), payload="D")
    E = em.make_edge((1, 0), (2, 0), payload="E")
    F = em.make_edge((2, 0), (2, 1), payload="F")
    G = em.make_edge((2, 1), (1, 1), payload="G")


class TestEdgeDeposit(SimpleLoops):
    #   0   1   2
    # 1 +-C-+-G-+
    #   |   |   |
    #   D   B   F
    #   |   |   |
    # 0 +-A-+-E-+
    @pytest.fixture
    def edges(self):
        return [self.A, self.B, self.C, self.D, self.E, self.F, self.G]

    def test_get_degree_of_vertex(self, edges: list[em.Edge]):
        deposit = em.Deposit(edges)
        assert deposit.degree((0, 0)) == 2
        assert deposit.degree((1, 0)) == 3
        assert deposit.degree((-1, -1)) == 0, "not in deposit"

    def test_get_degree_of_vertices(self, edges: list[em.Edge]):
        deposit = em.Deposit(edges)
        assert deposit.degrees([(0, 0), (1, 0), (-1, -1)]) == (2, 3, 0)
        assert deposit.degrees([]) == ()

    def test_degree_counter(self, edges: list[em.Edge]):
        deposit = em.Deposit(edges)
        counter = deposit.degree_counter()
        assert counter[1] == 0
        assert counter[2] == 4
        assert counter[3] == 2
        assert deposit.max_degree == 3

    def test_unique_vertices(self, edges: list[em.Edge]):
        deposit = em.Deposit(edges)
        assert len(deposit.unique_vertices()) == 6

    def test_find_edges_linked_to_vertex_A_D(self):
        deposit = em.Deposit([self.A, self.B, self.C, self.D])
        edges = deposit.edges_linked_to(self.A.start)
        ids = set(e.id for e in edges)
        assert len(ids) == 2
        assert self.A.id in ids
        assert self.D.id in ids

    def test_find_edges_linked_to_vertex_A_G(self, edges: list[em.Edge]):
        deposit = em.Deposit(edges)
        linked_edges = deposit.edges_linked_to(self.B.end)
        ids = set(e.id for e in linked_edges)
        assert len(ids) == 3
        assert self.B.id in ids
        assert self.C.id in ids
        assert self.G.id in ids

    def test_find_nearest_edge(self):
        deposit = em.Deposit([self.A, self.B, self.C, self.D])
        edge = deposit.find_nearest_edge((0.5, 0.6))
        assert edge is self.C

    def test_build_network_A_D(self):
        deposit = em.Deposit([self.A, self.B, self.C, self.D])
        # network of all edges connected directly or indirectly to A
        network = deposit.find_network(self.A)
        assert len(network) == 4
        assert self.B in network
        assert self.C in network
        assert self.D in network

    def test_solitary_edge_is_a_network(self):
        deposit = em.Deposit([self.A, self.C])
        network = deposit.find_network(self.A)
        assert len(network) == 0

    def test_build_network_A_G(self, edges: list[em.Edge]):
        deposit = em.Deposit(edges)
        # network of all edges connected directly or indirectly to B
        network = deposit.find_network(self.B)
        assert len(network) == 7

    def test_build_all_networks(self, edges: list[em.Edge]):
        deposit = em.Deposit(edges)
        assert len(deposit.find_all_networks()) == 1

    def test_build_all_disconnected_networks(self):
        #   0   1   2   3
        # 1 +-C-+   +-G-+
        #   |   |   |   |
        #   D   B   H   F
        #   |   |   |   |
        # 0 +-A-+   +-E-+
        E = em.make_edge((2, 0), (3, 0), payload="E")
        F = em.make_edge((3, 0), (3, 1), payload="F")
        G = em.make_edge((3, 1), (2, 1), payload="G")
        H = em.make_edge((2, 1), (2, 0), payload="H")

        deposit = em.Deposit([self.A, self.B, self.C, self.D, E, F, G, H])
        assert len(deposit.find_all_networks()) == 2

    def test_build_all_networks_solitary_edges(self):
        deposit = em.Deposit([self.A, self.C, self.F])
        assert len(deposit.find_all_networks()) == 0, "a single edge is not a network"

    def test_find_loose_ends(self):
        deposit = em.Deposit([self.A, self.E, self.B, self.C, self.G])
        edges = set(deposit.find_leafs())
        assert len(edges) == 4
        assert self.B not in edges

    def test_single_edge_is_a_loose_ends(self):
        deposit = em.Deposit([self.A])
        edges = list(deposit.find_leafs())
        assert len(edges) == 1

    def test_loops_do_not_have_loose_ends(self):
        deposit = em.Deposit([self.A, self.B, self.C, self.D])
        edges = set(deposit.find_leafs())
        assert len(edges) == 0


class TestLoop:
    # +-C-+
    # |   |
    # D   B
    # |   |
    # +-A-+

    A = em.make_edge((0, 0), (1, 0))
    B = em.make_edge((1, 0), (1, 1))
    C = em.make_edge((1, 1), (0, 1))
    D = em.make_edge((0, 1), (0, 0))

    def test_loop_key(self):
        loop1 = (self.A, self.B, self.C)
        loop2 = (self.B, self.C, self.A)  # rotated edges, same loop

        assert em.loop_key(loop1) == em.loop_key(loop2)


def collect(chain: Sequence[em.Edge]):
    return ",".join(e.payload for e in chain)


def ordered_edges(edges: Sequence[em.Edge], reverse=False):
    """Returns the loop edges in key order."""
    edge_dict = {e.id: e for e in edges}
    return (edge_dict[eid] for eid in em.loop_key(edges, reverse=reverse))


def collect_ordered(chain: Sequence[em.Edge]) -> str:
    """Returns the payload as strings in key order.

    Key order:
        Loop starts with the edge with the smallest id.
    """
    if len(chain) == 0:
        return ""
    elif len(chain) == 1:
        return chain[0].payload  # type: ignore
    return ",".join([e.payload for e in ordered_edges(chain)])


class TestFindSequential:
    #   0   1   2
    # 1 +-E-+-D-+
    #   |       |
    #   F       C
    #   |       |
    # 0 +-A-+-B-+

    A = em.make_edge((0, 0), (1, 0), payload="A")
    B = em.make_edge((1, 0), (2, 0), payload="B")
    C = em.make_edge((2, 0), (2, 1), payload="C")
    D = em.make_edge((2, 1), (1, 1), payload="D")
    E = em.make_edge((1, 1), (0, 1), payload="E")
    F = em.make_edge((0, 1), (0, 0), payload="F")

    def test_is_forward_connected(self):
        assert em.is_forward_connected(self.A, self.B) is True
        assert em.is_forward_connected(self.A, self.F) is False

    def test_find_sequential(self):
        edges = [self.A, self.B, self.C, self.D, self.E, self.F]
        result = em.find_sequential_chain(edges)
        assert len(result) == 6
        assert result[0] is self.A
        assert result[-1] is self.F


class TestLoopFinderSimple(SimpleLoops):

    @pytest.fixture(scope="class")
    def netAD(self):
        return em.Deposit([self.A, self.B, self.C, self.D])

    @pytest.fixture(scope="class")
    def netAG(self):
        return em.Deposit([self.A, self.B, self.C, self.D, self.E, self.F, self.G])

    def test_find_any_loop(self, netAG):
        finder = em.LoopFinder(netAG)
        loop = finder.find_any_loop(start=self.A)
        assert len(loop) > 3

    def test_loop_A_B_C_D(self, netAD):
        finder = em.LoopFinder(netAD)
        finder.search(self.A)
        solutions = list(finder)
        assert len(solutions) == 1
        assert collect_ordered(solutions[0]) == "A,B,C,D"

    def test_loop_D_A_B_C(self, netAD):
        finder = em.LoopFinder(netAD)
        finder.search(self.D)
        solutions = list(finder)
        assert len(solutions) == 1
        assert collect_ordered(solutions[0]) == "A,B,C,D"

    def test_loop_A_to_D_unique_solutions(self, netAD):
        finder = em.LoopFinder(netAD)
        finder.search(self.A)
        # rotated edges, same loop
        finder.search(self.D)
        solutions = list(finder)
        assert len(solutions) == 1

    def test_loops_A_to_G(self, netAG):
        finder = em.LoopFinder(netAG, timeout=10)
        finder.search(self.A)
        solutions = list(finder)
        assert len(solutions) == 2
        expected = {"A,B,C,D", "A,E,F,G,C,D"}
        assert collect_ordered(solutions[0]) in expected
        assert collect_ordered(solutions[1]) in expected


def simple_loops() -> em.Deposit:
    #   0   1   2
    # 1 +-C-+-G-+
    #   |   |   |
    #   D   B   F
    #   |   |   |
    # 0 +-A-+-E-+
    return em.Deposit(
        [
            em.make_edge((0, 0), (1, 0), length=0.5, payload="A"),
            em.make_edge((1, 0), (1, 1), payload="B"),
            em.make_edge((1, 1), (0, 1), payload="C"),
            em.make_edge((0, 1), (0, 0), payload="D"),
            em.make_edge((1, 0), (2, 0), payload="E"),
            em.make_edge((2, 0), (2, 1), payload="F"),
            em.make_edge((2, 1), (1, 1), payload="G"),
        ]
    )


def complex_loops() -> Sequence[em.Edge]:
    #   0   1   2   3
    # 1 +-C-+-I-+-G-+
    #   |   |   |   |
    #   D   B   H   F
    #   |   |   |   |
    # 0 +-A-+-J-+-E-+

    return [
        em.make_edge((0, 0), (1, 0), payload="A"),
        em.make_edge((1, 0), (1, 1), payload="B"),
        em.make_edge((1, 1), (0, 1), payload="C"),
        em.make_edge((0, 1), (0, 0), payload="D"),
        em.make_edge((2, 0), (3, 0), payload="E"),
        em.make_edge((3, 0), (3, 1), payload="F"),
        em.make_edge((3, 1), (2, 1), payload="G"),
        em.make_edge((2, 1), (2, 0), payload="H"),
        em.make_edge((1, 1), (2, 1), payload="I"),
        em.make_edge((1, 0), (2, 0), payload="J"),
    ]


def test_find_all_sequential():
    #   0   1   2   3
    # 1 +-C-+-I-+-G-+
    #   |   |   |   |
    #   D   B   H   F
    #   |   |   |   |
    # 0 +-A-+-J-+-E-+
    edges = complex_loops()
    result = list(em.find_all_sequential_chains(edges))

    assert len(result) == 4
    assert collect_ordered(result[0]) == "A,B,C,D"
    assert collect_ordered(result[1]) == "E,F,G,H"
    assert collect_ordered(result[2]) == "I"
    assert collect_ordered(result[3]) == "J"


def grid() -> Sequence[em.Edge]:
    #   0   1   2
    # 2 +-F-+-E-+
    #   G   J   D
    # 1 +-K-+-L-+
    #   H   I   C
    # 0 +-A-+-B-+
    return [
        em.make_edge((0, 0), (1, 0), payload="A"),
        em.make_edge((1, 0), (2, 0), payload="B"),
        em.make_edge((2, 0), (2, 1), payload="C"),
        em.make_edge((2, 1), (2, 2), payload="D"),
        em.make_edge((2, 2), (1, 2), payload="E"),
        em.make_edge((1, 2), (0, 2), payload="F"),
        em.make_edge((0, 2), (0, 1), payload="G"),
        em.make_edge((0, 1), (0, 0), payload="H"),
        em.make_edge((1, 0), (1, 1), payload="I"),
        em.make_edge((1, 1), (1, 2), payload="J"),
        em.make_edge((0, 1), (1, 1), payload="K"),
        em.make_edge((1, 1), (2, 1), payload="L"),
    ]


def test_find_all_complex_loops():
    #   0   1   2
    # 2 +-F-+-E-+
    #   G   J   D
    # 1 +-K-+-L-+
    #   H   I   C
    # 0 +-A-+-B-+
    edges = grid()
    result = em.find_all_loops(em.Deposit(edges))
    assert len(result) == 13

    unique_loops = list(em.unique_chains(result))
    assert len(unique_loops) == 13


class TestAPIFunction:
    #   0   1   2
    # 1 +-C-+-G-+
    #   |   |   |
    #   D   B   F
    #   |   |   |
    # 0 +-A-+-E-+
    def test_find_all_loop(self):
        solutions = em.find_all_loops(simple_loops())
        assert len(solutions) == 3
        solution_strings = set(collect_ordered(s) for s in solutions)
        valid_solutions = {
            "A,B,C,D",  # forward
            "A,D,C,B",  # reverse
            "B,E,F,G",  # forward
            "B,G,F,E",  # reverse
            "A,E,F,G,C,D",  # forward
            "A,D,C,G,F,E",  # reverse
        }
        assert len(solution_strings.intersection(valid_solutions)) == 3

    def test_find_first_loop(self):
        solution = em.find_loop(simple_loops())
        assert len(solution) >= 4  # any loop is a valid solution

    def test_find_shortest_loop(self):
        solution = em.shortest_chain(em.find_all_loops(simple_loops()))
        assert len(solution) == 4
        assert collect_ordered(solution) == "A,B,C,D"

    def test_find_longest_loop(self):
        solution = em.longest_chain(em.find_all_loops(simple_loops()))
        assert len(solution) == 6
        assert collect_ordered(solution) == "A,E,F,G,C,D"


class TestFindAllDisconnectedLoops:
    #   0   1   2   3
    # 1 +-C-+   +-G-+
    #   |   |   |   |
    #   D   B   H   F
    #   |   |   |   |
    # 0 +-A-+   +-E-+

    A = em.make_edge((0, 0), (1, 0), payload="A")
    B = em.make_edge((1, 0), (1, 1), payload="B")
    C = em.make_edge((1, 1), (0, 1), payload="C")
    D = em.make_edge((0, 1), (0, 0), payload="D")
    E = em.make_edge((2, 0), (3, 0), payload="E")
    F = em.make_edge((3, 0), (3, 1), payload="F")
    G = em.make_edge((3, 1), (2, 1), payload="G")
    H = em.make_edge((2, 1), (2, 0), payload="H")

    def test_find_all_loops(self):
        solutions = em.find_all_loops(
            em.Deposit((self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.H))
        )
        assert len(solutions) == 2
        solution_strings = [collect_ordered(s) for s in solutions]

        assert "A,B,C,D" in solution_strings
        assert "E,F,G,H" in solution_strings

    def test_find_all_shuffled_loops(self):
        solutions = em.find_all_loops(
            em.Deposit((self.H, self.B, self.F, self.D, self.E, self.C, self.G, self.A))
        )
        assert len(solutions) == 2
        solution_strings = [collect_ordered(s) for s in solutions]
        assert "A,B,C,D" in solution_strings
        assert "E,F,G,H" in solution_strings


class TestChainFinder:
    #    0   1   2   3   4   5
    #  2         G
    #  1         F
    #  0 +-A-+-B-+-C-+-D-+-E-+
    # -1         I
    # -2         J

    A = em.make_edge((0, 0), (1, 0), payload="A")
    B = em.make_edge((1, 0), (2, 0), payload="B")
    C = em.make_edge((2, 0), (3, 0), payload="C")
    D = em.make_edge((3, 0), (4, 0), payload="D")
    E = em.make_edge((4, 0), (5, 0), payload="E")

    F = em.make_edge((2, 0), (2, 1), payload="F")
    G = em.make_edge((2, 1), (2, 2), payload="G")
    I = em.make_edge((2, 0), (2, -1), payload="I")
    J = em.make_edge((2, -1), (2, -2), payload="J")

    def test_find_simple_chain(self):
        edges = [self.A, self.B, self.C, self.D, self.E]
        deposit = em.Deposit(edges)
        for edge in edges:
            result = em.find_simple_chain(deposit, edge)
            assert collect_ordered(result) == "A,B,C,D,E"

    def test_find_all_simple_chains(self):
        edges = [self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.I, self.J]
        result = em.find_all_simple_chains(em.Deposit(edges))
        assert len(result) == 4

    def test_closed_loop(self):
        # 1 +-C-+
        #   |   |
        #   D   B
        #   |   |
        # 0 +-A-+
        A = em.make_edge((0, 0), (1, 0), payload="A")
        B = em.make_edge((1, 0), (1, 1), payload="B")
        C = em.make_edge((1, 1), (0, 1), payload="C")
        D = em.make_edge((0, 1), (0, 0), payload="D")
        deposit = em.Deposit([A, B, C, D])
        for edge in [A, B, C, D]:
            result = em.find_simple_chain(deposit, edge)
            assert collect_ordered(result) == "A,B,C,D"


class TestWrappingChains:
    #    0   1   2   3   4   5
    #  0 +-A-+-B-+-C-+-D-+-E-+
    A = em.make_edge((0, 0), (1, 0), payload="A")
    B = em.make_edge((1, 0), (2, 0), payload="B")
    C = em.make_edge((2, 0), (3, 0), payload="C")
    D = em.make_edge((3, 0), (4, 0), payload="D")
    E = em.make_edge((4, 0), (5, 0), payload="E")

    @pytest.fixture(scope="class")
    def edges(self):
        return (self.A, self.B, self.C, self.D, self.E)

    def test_wrap_chain(self, edges: list[em.Edge]):
        wrapped_chain = em.wrap_simple_chain(edges)
        wrapper = wrapped_chain.payload
        assert isinstance(wrapper, em.EdgeWrapper)
        assert wrapper.edges == edges

    def test_is_wrapped_chain(self, edges: list[em.Edge]):
        wrapped_chain = em.wrap_simple_chain(edges)
        assert em.is_wrapped_chain(wrapped_chain) is True
        assert em.is_wrapped_chain(self.A) is False

    def test_wrapping_empty_chain_raises_exception(self):
        with pytest.raises(ValueError):
            em.wrap_simple_chain([])

    def test_wrapping_single_edge_raises_exception(self):
        with pytest.raises(ValueError):
            em.wrap_simple_chain([self.A])

    def test_wrapping_unlinked_edges_raises_exception(self):
        with pytest.raises(ValueError):
            em.wrap_simple_chain([self.A, self.C])

    def test_wrapping_loop_raises_exception(self):
        with pytest.raises(ValueError):
            em.wrap_simple_chain([self.A, self.A.reversed()])

    def test_unwrap_chain(self, edges: list[em.Edge]):
        wrapped_chain = em.wrap_simple_chain(edges)
        chain = em.unwrap_simple_chain(wrapped_chain)
        assert len(chain) == 5
        assert chain == edges

    def test_unwrap_reversed_chain(self, edges: list[em.Edge]):
        wrapped_chain = em.wrap_simple_chain(edges)
        reversed_edge = wrapped_chain.reversed()
        chain = em.unwrap_simple_chain(reversed_edge)
        assert len(chain) == 5
        assert chain[0].start == reversed_edge.start
        assert chain[-1].end == reversed_edge.end

        assert chain[0] == edges[-1]
        assert chain[0].is_reverse is not edges[-1].is_reverse
        assert chain[-1] == edges[0]
        assert chain[-1].is_reverse is not edges[0].is_reverse

    def test_unwrapping_single_edge(self):
        edges = em.unwrap_simple_chain(self.A)
        assert len(edges) == 1
        assert edges[0] == self.A

    def test_flatten_nested_edges(self):
        de = em.wrap_simple_chain([self.D, self.E])
        ab = em.wrap_simple_chain([self.A, self.B])
        cde = em.wrap_simple_chain([self.C, de])
        abcde = em.wrap_simple_chain([ab, cde])
        assert collect_ordered(list(em.flatten(abcde))) == "A,B,C,D,E"

    def test_flatten_empty_sequence(self):
        assert len(list(em.flatten([]))) == 0


class TestOpenChainFinder:

    def test_find_all_open_chains(self):
        #   0   1   2   3   4
        # 3 +---+---+-E-+-F-+
        #   |   |   D   |   |
        # 2 +-A-+-B-+-C-+---+
        #   |   G   |   |   |
        # 1 +---+-H-+---+---+
        #   |   |   I   |   |
        # 0 +---+---+---+---+
        # all end to end connections:
        # - 3 ABC or CBA
        # - 4 AGHI
        # - 4 C..F
        # - 5 A...F
        # - 5 C...I
        # - 7 I.....F

        A = em.make_edge((0, 2), (1, 2), payload="A")
        B = em.make_edge((1, 2), (2, 2), payload="B")
        C = em.make_edge((2, 2), (3, 2), payload="C")
        D = em.make_edge((2, 2), (2, 3), payload="D")
        E = em.make_edge((2, 3), (3, 3), payload="E")
        F = em.make_edge((3, 3), (4, 3), payload="F")
        G = em.make_edge((1, 2), (1, 1), payload="G")
        H = em.make_edge((1, 1), (2, 1), payload="H")
        I = em.make_edge((2, 1), (2, 0), payload="I")
        edges = (H, C, E, D, B, G, F, A, I)
        combinations = em.find_all_open_chains(em.Deposit(edges))
        assert len(combinations) == 6
        assert len(combinations[0]) == 3
        assert collect(combinations[0]) in ("A,B,C", "C,B,A")
        assert len(combinations[-1]) == 7
        assert collect(combinations[-1]) in ("I,H,G,B,D,E,F", "F,E,D,B,G,H,I")

    def test_does_not_detect_closed_loops(self):
        # 1 +-C-+
        #   |   |
        #   D   B
        #   |   |
        # 0 +-A-+
        A = em.make_edge((0, 0), (1, 0))
        B = em.make_edge((1, 0), (1, 1))
        C = em.make_edge((1, 1), (0, 1))
        D = em.make_edge((0, 1), (0, 0))
        deposit = em.Deposit([A, B, C, D])
        assert len(em.find_all_open_chains(deposit)) == 0

    def test_not_does_detect_indirect_loops(self):
        # 1 +-C-+
        #   |   |
        #   D   B
        #   |   |
        # 0 +-A-+-E-+
        A = em.make_edge((0, 0), (1, 0), payload="A")
        B = em.make_edge((1, 0), (1, 1), payload="B")
        C = em.make_edge((1, 1), (0, 1), payload="C")
        D = em.make_edge((0, 1), (0, 0), payload="D")
        E = em.make_edge((1, 0), (2, 0), payload="E")
        deposit = em.Deposit([A, B, C, D, E])
        result = set(collect(s) for s in em.find_all_open_chains(deposit))
        assert len(result) == 0


class TestFindLoopByEdge:
    #   0   1   2
    # 2 +-F-+-E-+
    #   G   J   D
    # 1 +-K-+-L-+
    #   H   I   C
    # 0 +-A-+-B-+
    edges = grid()

    def edge(self, payload: str):
        for edge in self.edges:
            if edge.payload == payload:
                return edge
        raise ValueError(f"edge {payload} does not exist")

    def test_search_continuation_clockwise(self):
        loop = em.find_loop_by_edge(
            em.Deposit(self.edges), self.edge("A"), clockwise=True
        )
        assert len(loop) == 4
        assert collect(loop) == "A,I,K,H"

    def test_search_continuation_counter_clockwise(self):
        loop = em.find_loop_by_edge(
            em.Deposit(self.edges), self.edge("A"), clockwise=False
        )
        assert len(loop) == 8
        assert collect(loop) == "A,B,C,D,E,F,G,H"


def test_filter_coincident_edges():
    edges = list(grid())
    edges.extend(grid())  # 2x the same edges
    assert len(em.filter_coincident_edges(em.Deposit(edges))) == 12


class TestFilterCloseVertices:
    def test_coincident_vertices(self):
        vertices = Vec3.list([(0, 0), (0, 0), (1, 1), (1, 1)])
        rt = rtree.RTree(vertices)
        result = em.filter_close_vertices(rt, gap_tol=1e-9)
        # You don't know which vertices were removed!
        assert len(result) == 2

    def test_chain_of_close_vertices(self):
        vertices = Vec3.list([(0, 0), (1, 0), (2, 0), (3, 0)])
        rt = rtree.RTree(vertices)
        result = em.filter_close_vertices(rt, gap_tol=1)
        # You don't know which vertices were removed!
        assert len(result) == 2

    def test_grid_of_close_vertices(self):
        # fmt: off
        vertices = Vec3.list([
            (0, 0), (1, 0), (2, 0), (3, 0),
            (0, 1), (1, 1), (2, 1), (3, 1),
            (0, 2), (1, 2), (2, 2), (3, 2),
            (0, 3), (1, 3), (2, 3), (3, 3)
        ])
        # fmt: on
        rt = rtree.RTree(vertices)
        result = em.filter_close_vertices(rt, gap_tol=1)
        # You don't know which vertices were removed!
        assert len(result) == 8


class TestSortEdgesByAngle:
    #   0   1   2
    # 2 +---+---+
    #   |\  |  /|
    #   | D C B |
    #   |  \|/  |
    # 1 +-E-+-A-+
    #   |  /|\  |
    #   | F G H |
    #   |/  |  \|
    # 0 +---+---+
    A = em.make_edge((1, 1), (2, 1), payload="A")
    B = em.make_edge((1, 1), (2, 2), payload="B")
    C = em.make_edge((1, 1), (1, 2), payload="C")
    D = em.make_edge((1, 1), (0, 2), payload="D")
    E = em.make_edge((1, 1), (0, 1), payload="E")
    F = em.make_edge((1, 1), (0, 0), payload="F")
    G = em.make_edge((1, 1), (1, 0), payload="G")
    H = em.make_edge((1, 1), (2, 0), payload="H")

    def test_edges_B_C_base_A(self):
        edges = [self.C, self.B]
        base = self.A.reversed()
        result = em.sort_edges_to_base(edges, base)
        assert result[0] is self.B
        assert result[1] is self.C

    def test_edges_G_H_base_A(self):
        edges = [self.G, self.H]
        base = self.A.reversed()
        result = em.sort_edges_to_base(edges, base)
        assert result[0] is self.G
        assert result[1] is self.H

    def test_edges_B_H_base_A(self):
        edges = [self.H, self.B]
        base = self.A.reversed()
        result = em.sort_edges_to_base(edges, base)
        assert result[0] is self.B
        assert result[1] is self.H

    def test_edges_A_B_base_C(self):
        edges = [self.A, self.B]
        base = self.C.reversed()
        result = em.sort_edges_to_base(edges, base)
        assert result[0] is self.A
        assert result[1] is self.B

    def test_edges_D_E_base_C(self):
        edges = [self.D, self.E]
        base = self.C.reversed()
        result = em.sort_edges_to_base(edges, base)
        assert result[0] is self.D
        assert result[1] is self.E

    def test_edges_B_D_base_C(self):
        edges = [self.B, self.D]
        base = self.C.reversed()
        result = em.sort_edges_to_base(edges, base)
        assert result[0] is self.D
        assert result[1] is self.B


class TestSubtractEdges:
    def test_subtract_nothing(self):
        edges = list(grid())
        result = em.subtract_edges(edges, [])
        assert len(result) == len(edges)

    def test_subtract_from_nothing(self):
        edges = list(grid())
        result = em.subtract_edges([], edges)
        assert len(result) == 0

    def test_subtract_one_edge(self):
        edges = list(grid())
        first = edges[0]
        result = em.subtract_edges(edges, [first])
        assert len(result) == len(edges) - 1
        assert first not in result

    def test_subtract_two_edges(self):
        edges = list(grid())
        two = edges[:2]
        result = em.subtract_edges(edges, two)
        assert len(result) == len(edges) - 2
        assert two[0] not in result
        assert two[1] not in result


if __name__ == "__main__":
    pytest.main([__file__])
