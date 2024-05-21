# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Sequence
import pytest

from ezdxf import edgeminer as em
from ezdxf.math import Vec2


class TestEdge:
    def test_init(self):
        edge = em.Edge(Vec2(0, 0), Vec2(1, 0), 1.0)
        assert edge.start == Vec2(0, 0)
        assert edge.end == Vec2(1, 0)
        assert edge.length == 1.0
        assert edge.reverse is False
        assert edge.payload is None

    def test_identity(self):
        edge0 = em.Edge(Vec2(0, 0), Vec2(1, 0), 1.0)
        edge1 = em.Edge(Vec2(0, 0), Vec2(1, 0), 1.0)
        assert edge0 == edge0
        assert edge0 != edge1, "each edge should have an unique identity"
        assert edge0 == edge0.copy(), "copies represent the same edge"
        assert edge0 == edge0.reversed(), "reversed copies represent the same edge"

    def test_copy(self):
        edge = em.Edge(Vec2(0, 0), Vec2(1, 0), 1.0)
        clone = edge.copy()
        assert edge == clone
        assert edge.id == clone.id
        assert edge.start == clone.start
        assert edge.end == clone.end
        assert edge.length == clone.length
        assert edge.reverse is clone.reverse
        assert edge.payload is clone.payload

    def test_reversed_copy(self):
        edge = em.Edge(Vec2(0, 0), Vec2(1, 0), 1.0)
        clone = edge.reversed()
        assert edge == clone
        assert edge.id == clone.id
        assert edge.start == clone.end
        assert edge.end == clone.start
        assert edge.length == clone.length
        assert edge.reverse is (not clone.reverse)
        assert edge.payload is clone.payload


def test_filter_short_edges():
    A = em.Edge(Vec2(0, 0), Vec2(0, 0))
    B = em.Edge(Vec2(1, 0), Vec2(1, 1))
    result = em.filter_short_edges([A, B])
    assert len(result) == 1
    assert result[0] is B


class TestLoop:
    # +-C-+
    # |   |
    # D   B
    # |   |
    # +-A-+

    A = em.Edge(Vec2(0, 0), Vec2(1, 0))
    B = em.Edge(Vec2(1, 0), Vec2(1, 1))
    C = em.Edge(Vec2(1, 1), Vec2(0, 1))
    D = em.Edge(Vec2(0, 1), Vec2(0, 0))

    def test_is_connected(self):
        loop = em.Loop((self.A,))
        assert loop.is_connected(self.B) is True

    def test_is_not_connected(self):
        loop = em.Loop((self.A,))
        assert loop.is_connected(self.C) is False
        assert (
            loop.is_connected(self.D) is False
        ), "should not check reverse connected edges"

    def test_is_closed_loop(self):
        loop = em.Loop((self.A, self.B, self.C, self.D))
        assert loop.is_closed_loop() is True

    def test_is_not_closed_loop(self):
        loop = em.Loop((self.A, self.B))
        assert loop.is_closed_loop() is False

    def test_key(self):
        loop1 = em.Loop((self.A, self.B, self.C))
        loop2 = em.Loop((self.B, self.C, self.A))  # rotated edges, same loop

        assert loop1.key() == loop2.key()


def collect_payload(edges: Sequence[em.Edge]) -> str:
    return ",".join([e.payload for e in edges])


class SimpleLoops:
    #   0   1   2
    # 1 +-C-+-G-+
    #   |   |   |
    #   D   B   F
    #   |   |   |
    # 0 +-A-+-E-+

    A = em.Edge(Vec2(0, 0), Vec2(1, 0), payload="A")
    B = em.Edge(Vec2(1, 0), Vec2(1, 1), payload="B")
    C = em.Edge(Vec2(1, 1), Vec2(0, 1), payload="C")
    D = em.Edge(Vec2(0, 1), Vec2(0, 0), payload="D")
    E = em.Edge(Vec2(1, 0), Vec2(2, 0), payload="E")
    F = em.Edge(Vec2(2, 0), Vec2(2, 1), payload="F")
    G = em.Edge(Vec2(2, 1), Vec2(1, 1), payload="G")


class TestLoopFinderSimple(SimpleLoops):
    def test_unique_available_edges_required(self):
        finder = em.LoopFinder()
        with pytest.raises(ValueError):
            finder.search(self.A, available=(self.B, self.B, self.B))

    def test_start_edge_not_in_available_edges(self):
        finder = em.LoopFinder()
        with pytest.raises(ValueError):
            finder.search(self.A, available=(self.A, self.C, self.D))

    def test_loop_A_B_C_D(self):
        finder = em.LoopFinder()
        finder.search(self.A, (self.B, self.C, self.D))
        solutions = list(finder)
        assert len(solutions) == 1
        assert collect_payload(solutions[0]) == "A,B,C,D"

    def test_loop_D_A_B_C(self):
        finder = em.LoopFinder()
        finder.search(self.D, (self.A, self.B, self.C))
        solutions = list(finder)
        assert len(solutions) == 1
        assert collect_payload(solutions[0]) == "D,A,B,C"

    def test_loop_A_to_D_unique_solutions(self):
        finder = em.LoopFinder()
        finder.search(self.A, (self.B, self.C, self.D))
        # rotated edges, same loop
        finder.search(self.D, (self.A, self.B, self.C))
        solutions = list(finder)
        assert len(solutions) == 1

    def test_loops_A_to_G(self):
        finder = em.LoopFinder()
        finder.search(self.A, (self.B, self.C, self.D, self.E, self.F, self.G))
        solutions = list(finder)
        assert len(solutions) == 2
        assert collect_payload(solutions[0]) == "A,B,C,D"
        assert collect_payload(solutions[1]) == "A,E,F,G,C,D"

    def test_stop_at_first_solution(self):
        finder = em.LoopFinder(first=True)
        finder.search(self.A, (self.B, self.C, self.D, self.E, self.F, self.G))
        solutions = list(finder)
        assert len(solutions) == 1


class TestAPIFunction(SimpleLoops):
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
        solution = em.find_shortest_loop(
            (self.A, self.B, self.C, self.D, self.E, self.F, self.G)
        )
        assert len(solution) == 4
        assert collect_payload(solution) == "A,B,C,D"

    def test_find_longest_loop(self):
        solution = em.find_longest_loop(
            (self.A, self.B, self.C, self.D, self.E, self.F, self.G)
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

    A = em.Edge(Vec2(0, 0), Vec2(1, 0), payload="A")
    B = em.Edge(Vec2(1, 0), Vec2(1, 1), payload="B")
    C = em.Edge(Vec2(1, 1), Vec2(0, 1), payload="C")
    D = em.Edge(Vec2(0, 1), Vec2(0, 0), payload="D")
    E = em.Edge(Vec2(2, 0), Vec2(3, 0), payload="E")
    F = em.Edge(Vec2(3, 0), Vec2(3, 1), payload="F")
    G = em.Edge(Vec2(3, 1), Vec2(2, 1), payload="G")
    H = em.Edge(Vec2(2, 1), Vec2(2, 0), payload="H")

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
        assert "B,C,D,A" in solution_strings
        assert "H,E,F,G" in solution_strings


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

    def test_build_network_A_G(self):
        deposit = em.EdgeDeposit(
            [self.A, self.B, self.C, self.D, self.E, self.F, self.G]
        )
        # network of all edges connected directly or indirectly to B
        network = deposit.build_network(self.B)
        assert len(network) == 7
        # all edges connected directly to B
        edges = network.edges_linked_to(self.B)
        assert len(edges) == 4


if __name__ == "__main__":
    pytest.main([__file__])
