# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Sequence
import pytest

from ezdxf import edgeminer as em
from ezdxf.math import Vec3


class TestEdge:
    def test_init(self):
        edge = em.Edge((0, 0), (1, 0), 1.0)
        assert edge.start == Vec3(0, 0)
        assert edge.end == Vec3(1, 0)
        assert edge.length == 1.0
        assert edge.is_reverse is False
        assert edge.payload is None

    def test_identity(self):
        edge0 = em.Edge((0, 0), (1, 0), 1.0)
        edge1 = em.Edge((0, 0), (1, 0), 1.0)
        assert edge0 == edge0
        assert edge0 != edge1, "each edge should have an unique identity"
        assert edge0 == edge0.reversed(), "reversed copies represent the same edge"

    def test_reversed_copy(self):
        edge = em.Edge((0, 0), (1, 0), 1.0)
        clone = edge.reversed()
        assert edge == clone
        assert edge.id == clone.id
        assert edge.start == clone.end
        assert edge.end == clone.start
        assert edge.length == clone.length
        assert edge.is_reverse is (not clone.is_reverse)
        assert edge.payload is clone.payload

    def test_edge_can_be_used_in_sets(self):
        A = em.Edge((0, 0), (1, 0))
        B = em.Edge((1, 0), (1, 1))
        C = em.Edge((1, 1), (0, 1))

        s1 = set([A, B])
        s2 = set([C, B])
        result = s1.intersection(s2)
        assert len(result) == 1
        assert B in result


class TestLoop:
    # +-C-+
    # |   |
    # D   B
    # |   |
    # +-A-+

    A = em.Edge((0, 0), (1, 0))
    B = em.Edge((1, 0), (1, 1))
    C = em.Edge((1, 1), (0, 1))
    D = em.Edge((0, 1), (0, 0))

    def test_loop_key(self):
        loop1 = (self.A, self.B, self.C)
        loop2 = (self.B, self.C, self.A)  # rotated edges, same loop

        assert em.loop_key(loop1) == em.loop_key(loop2)


def collect(chain: Sequence[em.Edge]):
    return ",".join(e.payload for e in chain)


def ordered_edges(edges: Sequence[em.Edge], reverse=False):
    """Returns the loop edges in key order."""
    edge_dict = {e.id: e for e in edges}
    return (edge_dict[eid] for eid in em.loop_key(edges, reverse))


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

    A = em.Edge((0, 0), (1, 0), payload="A")
    B = em.Edge((1, 0), (2, 0), payload="B")
    C = em.Edge((2, 0), (2, 1), payload="C")
    D = em.Edge((2, 1), (1, 1), payload="D")
    E = em.Edge((1, 1), (0, 1), payload="E")
    F = em.Edge((0, 1), (0, 0), payload="F")

    def test_is_forward_connected(self):
        assert em.is_forward_connected(self.A, self.B) is True
        assert em.is_forward_connected(self.A, self.F) is False

    def test_is_backwards_connected(self):
        assert em.is_backwards_connected(self.A, self.F) is True
        assert em.is_backwards_connected(self.A, self.B) is False
        assert em.is_backwards_connected(self.D, self.F) is False

    def test_find_sequential(self):
        edges = [self.A, self.B, self.C, self.D, self.E, self.F]
        result = em.find_sequential(edges)
        assert len(result) == 6
        assert result[0] is self.A
        assert result[-1] is self.F


class SimpleLoops:
    #   0   1   2
    # 1 +-C-+-G-+
    #   |   |   |
    #   D   B   F
    #   |   |   |
    # 0 +-A-+-E-+

    A = em.Edge((0, 0), (1, 0), length=0.5, payload="A")
    B = em.Edge((1, 0), (1, 1), payload="B")
    C = em.Edge((1, 1), (0, 1), payload="C")
    D = em.Edge((0, 1), (0, 0), payload="D")
    E = em.Edge((1, 0), (2, 0), payload="E")
    F = em.Edge((2, 0), (2, 1), payload="F")
    G = em.Edge((2, 1), (1, 1), payload="G")


class TestLoopFinderSimple(SimpleLoops):

    @pytest.fixture(scope="class")
    def netAD(self):
        return em.EdgeDeposit([self.A, self.B, self.C, self.D])

    @pytest.fixture(scope="class")
    def netAG(self):
        return em.EdgeDeposit([self.A, self.B, self.C, self.D, self.E, self.F, self.G])
    
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


def simple_loops() -> Sequence[em.Edge]:
    #   0   1   2
    # 1 +-C-+-G-+
    #   |   |   |
    #   D   B   F
    #   |   |   |
    # 0 +-A-+-E-+
    return [
        em.Edge((0, 0), (1, 0), length=0.5, payload="A"),
        em.Edge((1, 0), (1, 1), payload="B"),
        em.Edge((1, 1), (0, 1), payload="C"),
        em.Edge((0, 1), (0, 0), payload="D"),
        em.Edge((1, 0), (2, 0), payload="E"),
        em.Edge((2, 0), (2, 1), payload="F"),
        em.Edge((2, 1), (1, 1), payload="G"),
    ]


def complex_loops() -> Sequence[em.Edge]:
    #   0   1   2   3
    # 1 +-C-+-I-+-G-+
    #   |   |   |   |
    #   D   B   H   F
    #   |   |   |   |
    # 0 +-A-+-J-+-E-+

    return [
        em.Edge((0, 0), (1, 0), payload="A"),
        em.Edge((1, 0), (1, 1), payload="B"),
        em.Edge((1, 1), (0, 1), payload="C"),
        em.Edge((0, 1), (0, 0), payload="D"),
        em.Edge((2, 0), (3, 0), payload="E"),
        em.Edge((3, 0), (3, 1), payload="F"),
        em.Edge((3, 1), (2, 1), payload="G"),
        em.Edge((2, 1), (2, 0), payload="H"),
        em.Edge((1, 1), (2, 1), payload="I"),
        em.Edge((1, 0), (2, 0), payload="J"),
    ]


def test_find_all_sequential():
    #   0   1   2   3
    # 1 +-C-+-I-+-G-+
    #   |   |   |   |
    #   D   B   H   F
    #   |   |   |   |
    # 0 +-A-+-J-+-E-+
    edges = complex_loops()
    result = list(em.find_all_sequential(edges))

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
        em.Edge((0, 0), (1, 0), payload="A"),
        em.Edge((1, 0), (2, 0), payload="B"),
        em.Edge((2, 0), (2, 1), payload="C"),
        em.Edge((2, 1), (2, 2), payload="D"),
        em.Edge((2, 2), (1, 2), payload="E"),
        em.Edge((1, 2), (0, 2), payload="F"),
        em.Edge((0, 2), (0, 1), payload="G"),
        em.Edge((0, 1), (0, 0), payload="H"),
        em.Edge((1, 0), (1, 1), payload="I"),
        em.Edge((1, 1), (1, 2), payload="J"),
        em.Edge((0, 1), (1, 1), payload="K"),
        em.Edge((1, 1), (2, 1), payload="L"),
    ]


def test_find_all_complex_loops():
    #   0   1   2
    # 2 +-F-+-E-+
    #   G   J   D
    # 1 +-K-+-L-+
    #   H   I   C
    # 0 +-A-+-B-+
    edges = grid()
    result = em.find_all_loops(edges)
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

    A = em.Edge((0, 0), (1, 0), payload="A")
    B = em.Edge((1, 0), (1, 1), payload="B")
    C = em.Edge((1, 1), (0, 1), payload="C")
    D = em.Edge((0, 1), (0, 0), payload="D")
    E = em.Edge((2, 0), (3, 0), payload="E")
    F = em.Edge((3, 0), (3, 1), payload="F")
    G = em.Edge((3, 1), (2, 1), payload="G")
    H = em.Edge((2, 1), (2, 0), payload="H")

    def test_find_all_loops(self):
        solutions = em.find_all_loops(
            (self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.H)
        )
        assert len(solutions) == 2
        solution_strings = [collect_ordered(s) for s in solutions]

        assert "A,B,C,D" in solution_strings
        assert "E,F,G,H" in solution_strings

    def test_find_all_shuffled_loops(self):
        solutions = em.find_all_loops(
            (self.H, self.B, self.F, self.D, self.E, self.C, self.G, self.A)
        )
        assert len(solutions) == 2
        solution_strings = [collect_ordered(s) for s in solutions]
        assert "A,B,C,D" in solution_strings
        assert "E,F,G,H" in solution_strings


class TestEdgeDeposit(SimpleLoops):
    #   0   1   2
    # 1 +-C-+-G-+
    #   |   |   |
    #   D   B   F
    #   |   |   |
    # 0 +-A-+-E-+

    def test_degree_counter(self):
        deposit = em.EdgeDeposit(
            [self.A, self.B, self.C, self.D, self.E, self.F, self.G]
        )
        counter = deposit.count_degrees()
        assert counter[1] == 0
        assert counter[2] == 4
        assert counter[3] == 2
        assert deposit.max_degree() == 3

    def test_find_edges_linked_to_vertex_A_D(self):
        deposit = em.EdgeDeposit([self.A, self.B, self.C, self.D])
        edges = deposit.edges_linked_to(self.A.start)
        ids = set(e.id for e in edges)
        assert len(ids) == 2
        assert self.A.id in ids
        assert self.D.id in ids

    def test_find_edges_linked_to_vertex_A_G(self):
        deposit = em.EdgeDeposit(
            [self.A, self.B, self.C, self.D, self.E, self.F, self.G]
        )
        edges = deposit.edges_linked_to(self.B.end)
        ids = set(e.id for e in edges)
        assert len(ids) == 3
        assert self.B.id in ids
        assert self.C.id in ids
        assert self.G.id in ids

    def test_find_nearest_edge(self):
        deposit = em.EdgeDeposit([self.A, self.B, self.C, self.D])
        edge = deposit.find_nearest_edge((0.5, 0.6))
        assert edge is self.C

    def test_build_network_A_D(self):
        deposit = em.EdgeDeposit([self.A, self.B, self.C, self.D])
        # network of all edges connected directly or indirectly to A
        network = deposit.find_network(self.A)
        assert len(network) == 4
        assert self.B in network
        assert self.C in network
        assert self.D in network

    def test_solitary_edge_is_a_network(self):
        deposit = em.EdgeDeposit([self.A, self.C])
        network = deposit.find_network(self.A)
        assert len(network) == 0

    def test_build_network_A_G(self):
        deposit = em.EdgeDeposit(
            [self.A, self.B, self.C, self.D, self.E, self.F, self.G]
        )
        # network of all edges connected directly or indirectly to B
        network = deposit.find_network(self.B)
        assert len(network) == 7

    def test_build_all_networks(self):
        deposit = em.EdgeDeposit(
            [self.A, self.B, self.C, self.D, self.E, self.F, self.G]
        )
        assert len(deposit.find_all_networks()) == 1

    def test_build_all_disconnected_networks(self):
        #   0   1   2   3
        # 1 +-C-+   +-G-+
        #   |   |   |   |
        #   D   B   H   F
        #   |   |   |   |
        # 0 +-A-+   +-E-+
        E = em.Edge((2, 0), (3, 0), payload="E")
        F = em.Edge((3, 0), (3, 1), payload="F")
        G = em.Edge((3, 1), (2, 1), payload="G")
        H = em.Edge((2, 1), (2, 0), payload="H")

        deposit = em.EdgeDeposit([self.A, self.B, self.C, self.D, E, F, G, H])
        assert len(deposit.find_all_networks()) == 2

    def test_build_all_networks_solitary_edges(self):
        deposit = em.EdgeDeposit([self.A, self.C, self.F])
        assert len(deposit.find_all_networks()) == 0, "a single edge is not a network"

    def test_find_loose_ends(self):
        deposit = em.EdgeDeposit([self.A, self.E, self.B, self.C, self.G])
        edges = set(deposit.find_loose_ends())
        assert len(edges) == 4
        assert self.B not in edges

    def test_single_edge_is_a_loose_ends(self):
        deposit = em.EdgeDeposit([self.A])
        edges = list(deposit.find_loose_ends())
        assert len(edges) == 1

    def test_loops_do_not_have_loose_ends(self):
        deposit = em.EdgeDeposit([self.A, self.B, self.C, self.D])
        edges = set(deposit.find_loose_ends())
        assert len(edges) == 0


class TestChainFinder:
    #    0   1   2   3   4   5
    #  2         G
    #  1         F
    #  0 +-A-+-B-+-C-+-D-+-E-+
    # -1         I
    # -2         J

    A = em.Edge((0, 0), (1, 0), payload="A")
    B = em.Edge((1, 0), (2, 0), payload="B")
    C = em.Edge((2, 0), (3, 0), payload="C")
    D = em.Edge((3, 0), (4, 0), payload="D")
    E = em.Edge((4, 0), (5, 0), payload="E")

    F = em.Edge((2, 0), (2, 1), payload="F")
    G = em.Edge((2, 1), (2, 2), payload="G")
    I = em.Edge((2, 0), (2, -1), payload="I")
    J = em.Edge((2, -1), (2, -2), payload="J")

    def test_find_chain(self):
        edges = [self.A, self.B, self.C, self.D, self.E]
        deposit = em.EdgeDeposit(edges)
        for edge in edges:
            result = em.find_chain_in_deposit(deposit, edge)
            assert collect_ordered(result) == "A,B,C,D,E"

    def test_find_all(self):
        edges = [self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.I, self.J]
        result = em.find_all_chains_in_deposit(em.EdgeDeposit(edges))
        assert len(result) == 4

    def test_closed_loop(self):
        # 1 +-C-+
        #   |   |
        #   D   B
        #   |   |
        # 0 +-A-+
        A = em.Edge((0, 0), (1, 0), payload="A")
        B = em.Edge((1, 0), (1, 1), payload="B")
        C = em.Edge((1, 1), (0, 1), payload="C")
        D = em.Edge((0, 1), (0, 0), payload="D")
        deposit = em.EdgeDeposit([A, B, C, D])
        for edge in [A, B, C, D]:
            result = em.find_chain_in_deposit(deposit, edge)
            assert collect_ordered(result) == "A,B,C,D"


class TestWrappingChains:
    #    0   1   2   3   4   5
    #  0 +-A-+-B-+-C-+-D-+-E-+
    A = em.Edge((0, 0), (1, 0), payload="A")
    B = em.Edge((1, 0), (2, 0), payload="B")
    C = em.Edge((2, 0), (3, 0), payload="C")
    D = em.Edge((3, 0), (4, 0), payload="D")
    E = em.Edge((4, 0), (5, 0), payload="E")

    @pytest.fixture(scope="class")
    def edges(self):
        return (self.A, self.B, self.C, self.D, self.E)

    def test_wrap_chain(self, edges: list[em.Edge]):
        wrapped_chain = em.wrap_chain(edges)
        wrapper = wrapped_chain.payload
        assert isinstance(wrapper, em.EdgeWrapper)
        assert wrapper.edges == edges

    def test_is_wrapped_chain(self, edges: list[em.Edge]):
        wrapped_chain = em.wrap_chain(edges)
        assert em.is_wrapped_chain(wrapped_chain) is True
        assert em.is_wrapped_chain(self.A) is False

    def test_wrapping_empty_chain_raises_exception(self):
        with pytest.raises(ValueError):
            em.wrap_chain([])

    def test_wrapping_single_edge_raises_exception(self):
        with pytest.raises(ValueError):
            em.wrap_chain([self.A])

    def test_wrapping_unlinked_edges_raises_exception(self):
        with pytest.raises(ValueError):
            em.wrap_chain([self.A, self.C])

    def test_wrapping_loop_raises_exception(self):
        with pytest.raises(ValueError):
            em.wrap_chain([self.A, self.A.reversed()])

    def test_unwrap_chain(self, edges: list[em.Edge]):
        wrapped_chain = em.wrap_chain(edges)
        chain = em.unwrap_chain(wrapped_chain)
        assert len(chain) == 5
        assert chain == edges

    def test_unwrap_reversed_chain(self, edges: list[em.Edge]):
        wrapped_chain = em.wrap_chain(edges)
        reversed_edge = wrapped_chain.reversed()
        chain = em.unwrap_chain(reversed_edge)
        assert len(chain) == 5
        assert chain[0].start == reversed_edge.start
        assert chain[-1].end == reversed_edge.end

        assert chain[0] == edges[-1]
        assert chain[0].is_reverse is not edges[-1].is_reverse
        assert chain[-1] == edges[0]
        assert chain[-1].is_reverse is not edges[0].is_reverse

    def test_unwrapping_single_edge(self):
        edges = em.unwrap_chain(self.A)
        assert len(edges) == 1
        assert edges[0] == self.A

    def test_flatten_nested_edges(self):
        de = em.wrap_chain([self.D, self.E])
        ab = em.wrap_chain([self.A, self.B])
        cde = em.wrap_chain([self.C, de])
        abcde = em.wrap_chain([ab, cde])
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

        A = em.Edge((0, 2), (1, 2), payload="A")
        B = em.Edge((1, 2), (2, 2), payload="B")
        C = em.Edge((2, 2), (3, 2), payload="C")
        D = em.Edge((2, 2), (2, 3), payload="D")
        E = em.Edge((2, 3), (3, 3), payload="E")
        F = em.Edge((3, 3), (4, 3), payload="F")
        G = em.Edge((1, 2), (1, 1), payload="G")
        H = em.Edge((1, 1), (2, 1), payload="H")
        I = em.Edge((2, 1), (2, 0), payload="I")
        edges = (H, C, E, D, B, G, F, A, I)
        combinations = em.find_open_chains(edges)
        assert len(combinations) == 6
        assert len(combinations[0]) == 3
        assert collect(combinations[0]) in ("A,B,C", "C,B,A")
        assert len(combinations[-1]) == 7
        assert collect(combinations[-1]) in ("I,H,G,B,D,E,F", "F,E,D,B,G,H,I")

    def test_does_not_detect_isolated_loops(self):
        # 1 +-C-+
        #   |   |
        #   D   B
        #   |   |
        # 0 +-A-+
        A = em.Edge((0, 0), (1, 0))
        B = em.Edge((1, 0), (1, 1))
        C = em.Edge((1, 1), (0, 1))
        D = em.Edge((0, 1), (0, 0))
        assert len(em.find_open_chains([A, B, C, D])) == 0

    def test_does_detect_extended_loops(self):
        # 1 +-C-+
        #   |   |
        #   D   B
        #   |   |
        # 0 +-A-+-E-+
        A = em.Edge((0, 0), (1, 0), payload="A")
        B = em.Edge((1, 0), (1, 1), payload="B")
        C = em.Edge((1, 1), (0, 1), payload="C")
        D = em.Edge((0, 1), (0, 0), payload="D")
        E = em.Edge((1, 0), (2, 0), payload="E")
        results = set(collect(s) for s in em.find_open_chains([A, B, C, D, E]))
        assert "A,D,C,B,E" in results
        assert "B,C,D,A,E" in results


def xest_closest_loop():
    #   0   1   2
    # 2 +-F-+-E-+
    #   G   J   D
    # 1 +-K-+-L-+
    #   H   I   C
    # 0 +-A-+-B-+
    loop = em.find_closest_loop(grid(), pick=(0.5, 0.5), timeout=1)

    assert collect(loop) in {"A,I,K,H", "H,K,I,A"}


if __name__ == "__main__":
    pytest.main([__file__])
