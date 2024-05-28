# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Sequence
import pytest

import ezdxf
from ezdxf import edgeminer as em
from ezdxf.math import Vec3


class TestEdge:
    def test_init(self):
        edge = em.Edge((0, 0), (1, 0), 1.0)
        assert edge.start == Vec3(0, 0)
        assert edge.end == Vec3(1, 0)
        assert edge.length == 1.0
        assert edge.reverse is False
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
        assert edge.reverse is (not clone.reverse)
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


def ordered_edges(edges: Sequence[em.Edge], reverse=False):
    """Returns the loop edges in key order."""
    edge_dict = {e.id: e for e in edges}
    return (edge_dict[eid] for eid in em.loop_key(edges, reverse))


def collect_payload(edges: Sequence[em.Edge]) -> str:
    """Returns the payload as strings in key order.

    Key order:
        Loop starts with the edge with the smallest id.
    """
    if len(edges) == 0:
        return ""
    elif len(edges) == 1:
        return edges[0].payload  # type: ignore
    return ",".join([e.payload for e in ordered_edges(edges)])


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


def test_find_all_sequential():
    #   0   1   2   3
    # 1 +-C-+-I-+-G-+
    #   |   |   |   |
    #   D   B   H   F
    #   |   |   |   |
    # 0 +-A-+-J-+-E-+

    A = em.Edge((0, 0), (1, 0), payload="A")
    B = em.Edge((1, 0), (1, 1), payload="B")
    C = em.Edge((1, 1), (0, 1), payload="C")
    D = em.Edge((0, 1), (0, 0), payload="D")
    E = em.Edge((2, 0), (3, 0), payload="E")
    F = em.Edge((3, 0), (3, 1), payload="F")
    G = em.Edge((3, 1), (2, 1), payload="G")
    H = em.Edge((2, 1), (2, 0), payload="H")
    I = em.Edge((1, 1), (2, 1), payload="I")
    J = em.Edge((1, 0), (2, 0), payload="J")

    edges = [A, B, C, D, E, F, G, H, I, J]
    result = list(em.find_all_sequential(edges))
    assert len(result) == 4
    assert collect_payload(result[0]) == "A,B,C,D"
    assert collect_payload(result[1]) == "E,F,G,H"
    assert collect_payload(result[2]) == "I"
    assert collect_payload(result[3]) == "J"


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
        deposit = em.EdgeDeposit([self.A, self.B, self.C, self.D])
        return deposit.build_network(self.A)

    @pytest.fixture(scope="class")
    def netAG(self):
        deposit = em.EdgeDeposit(
            [self.A, self.B, self.C, self.D, self.E, self.F, self.G]
        )
        return deposit.build_network(self.A)

    def test_find_any_loop(self, netAG):
        finder = em.LoopFinder(netAG)
        loop = finder.find_any_loop(start=self.A)
        assert len(loop) > 3

    def test_loop_A_B_C_D(self, netAD):
        finder = em.LoopFinder(netAD)
        finder.search(self.A)
        solutions = list(finder)
        assert len(solutions) == 1
        assert collect_payload(solutions[0]) == "A,B,C,D"

    def test_loop_D_A_B_C(self, netAD):
        finder = em.LoopFinder(netAD)
        finder.search(self.D)
        solutions = list(finder)
        assert len(solutions) == 1
        assert collect_payload(solutions[0]) == "A,B,C,D"

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
        assert collect_payload(solutions[0]) in expected
        assert collect_payload(solutions[1]) in expected


class TestAPIFunction(SimpleLoops):
    @pytest.mark.skipif(ezdxf.PYPY is True, reason="has different search order?")
    def test_find_all_loop(self):
        solutions = em.find_all_loops(
            (self.A, self.B, self.C, self.D, self.E, self.F, self.G)
        )
        assert len(solutions) == 3
        solution_strings = [collect_payload(s) for s in solutions]
        assert "A,B,C,D" in solution_strings
        assert "B,G,F,E" in solution_strings
        assert "A,E,F,G,C,D" in solution_strings

    def test_find_first_loop(self):
        solution = em.find_first_loop(
            (self.A, self.B, self.C, self.D, self.E, self.F, self.G)
        )
        assert len(solution) >= 4  # any loop is a valid solution

    def test_find_shortest_loop(self):
        solution = em.shortest_chain(
            em.find_all_loops((self.A, self.B, self.C, self.D, self.E, self.F, self.G))
        )
        assert len(solution) == 4
        assert collect_payload(solution) == "A,B,C,D"

    def test_find_longest_loop(self):
        solution = em.longest_chain(
            em.find_all_loops((self.A, self.B, self.C, self.D, self.E, self.F, self.G))
        )
        assert len(solution) == 6
        assert collect_payload(solution) == "A,E,F,G,C,D"


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
        solution_strings = [collect_payload(s) for s in solutions]

        assert "A,B,C,D" in solution_strings
        assert "E,F,G,H" in solution_strings

    def test_find_all_shuffled_loops(self):
        solutions = em.find_all_loops(
            (self.H, self.B, self.F, self.D, self.E, self.C, self.G, self.A)
        )
        assert len(solutions) == 2
        solution_strings = [collect_payload(s) for s in solutions]
        assert "A,B,C,D" in solution_strings
        assert "E,F,G,H" in solution_strings


class TestEdgeDeposit(SimpleLoops):
    #   0   1   2
    # 1 +-C-+-G-+
    #   |   |   |
    #   D   B   F
    #   |   |   |
    # 0 +-A-+-E-+

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
        network = deposit.build_network(self.A)
        assert len(network) == 4
        assert self.B in network
        assert self.C in network
        assert self.D in network

        # all edges connected directly to A
        edges = network.edges_linked_to(self.A)
        assert len(edges) == 2

    def test_solitary_edge_is_not_a_network(self):
        deposit = em.EdgeDeposit([self.A, self.C])
        network = deposit.build_network(self.A)
        assert len(network) == 0

    def test_build_network_A_G(self):
        deposit = em.EdgeDeposit(
            [self.A, self.B, self.C, self.D, self.E, self.F, self.G]
        )
        # network of all edges connected directly or indirectly to B
        network = deposit.build_network(self.B)
        assert len(network) == 7

        # all edges connected directly to A
        edges = network.edges_linked_to(self.A)
        assert len(edges) == 3

        edges = network.edges_linked_to(self.B)
        assert len(edges) == 4

        edges = network.edges_linked_to(self.C)
        assert len(edges) == 3

        edges = network.edges_linked_to(self.D)
        assert len(edges) == 2

        edges = network.edges_linked_to(self.E)
        assert len(edges) == 3

        edges = network.edges_linked_to(self.F)
        assert len(edges) == 2

        edges = network.edges_linked_to(self.G)
        assert len(edges) == 3

    def test_build_all_networks(self):
        deposit = em.EdgeDeposit(
            [self.A, self.B, self.C, self.D, self.E, self.F, self.G]
        )
        assert len(deposit.build_all_networks()) == 1

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
        assert len(deposit.build_all_networks()) == 2

    def test_build_all_networks_solitary_edges(self):
        deposit = em.EdgeDeposit([self.A, self.C, self.F])
        assert len(deposit.build_all_networks()) == 0


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
        finder = em.ChainFinder(deposit)
        for edge in edges:
            result = finder.find_chain(edge)
            assert collect_payload(result) == "A,B,C,D,E"

    def test_find_all(self):
        edges = [self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.I, self.J]
        finder = em.ChainFinder(em.EdgeDeposit(edges))
        result = finder.find_all()
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
        finder = em.ChainFinder(deposit)
        for edge in [A, B, C, D]:
            result = finder.find_chain(edge)
            assert collect_payload(result) == "A,B,C,D"


if __name__ == "__main__":
    pytest.main([__file__])
