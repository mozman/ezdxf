# Copyright (c) 2025, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Sequence
import random
import math
from pathlib import Path
from time import perf_counter

import ezdxf
from ezdxf.layouts import Modelspace
from ezdxf.render import forms
from ezdxf.math import Vec2, is_point_in_polygon_2d
from ezdxf import edgeminer as em
from ezdxf import edgesmith as es

CWD = Path(__file__).parent
OUTBOX = Path("~/Desktop/Outbox").expanduser()


def circle(count: int, radius: float) -> list[em.Edge]:
    vertices = list(forms.circle(count, radius, close=True))
    return [em.make_edge(a, b) for a, b in zip(vertices, vertices[1:])]


def with_fringes(edges: list[em.Edge], count: int, length: float) -> list[em.Edge]:
    fringes: list[em.Edge] = []
    for _ in range(count):
        edge = random.choice(edges)
        start = edge.end
        fringe = Vec2.from_angle(random.random() * math.tau, length=length)
        fringes.append(em.make_edge(start, start + fringe))

    return edges + fringes


def mark_edges(msp: Modelspace, edges: Sequence[em.Edge]):
    radius = 0.1
    for edge in edges:
        if edge.is_reverse:
            dxfattribs = {"color": 1}
        else:
            dxfattribs = {"color": 3}
        msp.add_circle(edge.start, radius, dxfattribs=dxfattribs)
        msp.add_circle(edge.end, radius * 2, dxfattribs=dxfattribs)


def grid(size: tuple[int, int], length: float) -> list[em.Edge]:
    edges: list[em.Edge] = []
    m, n = size
    for row in range(m + 1):
        y = row * length
        for col in range(n + 1):
            x = col * length
            if col < n:
                edges.append(em.make_edge((x, y), (x + length, y)))
            if row < m:
                edges.append(em.make_edge((x, y), (x, y + length)))
    return edges


def open_grid(size: tuple[int, int], length: float) -> list[em.Edge]:
    edges: list[em.Edge] = []
    m, n = size
    for row in range(m):
        y = row * length
        for col in range(n):
            x = col * length
            if row > 0:
                edges.append(em.make_edge((x, y), (x + length, y)))
            if col > 0:
                edges.append(em.make_edge((x, y), (x, y + length)))
    return edges


def square(start: Vec2, length: float) -> Sequence[em.Edge]:
    p1 = start + (length, 0)
    p2 = start + (length, length)
    p3 = start + (0, length)
    return (
        em.make_edge(start, p1),
        em.make_edge(p1, p2),
        em.make_edge(p2, p3),
        em.make_edge(p3, start),
    )


def grid_of_squares(size: tuple[int, int], length: float) -> list[em.Edge]:
    edges: list[em.Edge] = []
    m, n = size
    for row in range(m):
        y = row * length
        for col in range(n):
            x = col * length
            edges.extend(square(Vec2(x, y), length))
    return edges


def grid_of_jiggled_squares(size: tuple[int, int], length: float) -> list[em.Edge]:
    edges: list[em.Edge] = []
    m, n = size
    for row in range(m):
        y = row * length
        for col in range(n):
            x = col * length
            jiggle = Vec2.from_angle(
                random.random() * math.tau, length=length * random.random() / 10.0
            )
            edges.extend(square(Vec2(x, y) + jiggle, length))
    return edges


def load(filename: str) -> list[em.Edge]:
    doc = ezdxf.readfile(CWD / filename)
    msp = doc.modelspace()
    edges = list(es.edges_from_entities_2d(msp))
    print(f"found {len(edges)} edges in '{filename}'")
    return edges


def export_chains(
    filename: str, chains: Sequence[Sequence[em.Edge]], gap_tol=em.GAP_TOL
):
    doc = ezdxf.new()
    msp = doc.modelspace()
    for index, chain in enumerate(chains):
        is_loop = em.is_loop_fast(chain, gap_tol=gap_tol)
        layer = f"L{index}" if is_loop else f"C{index}"
        color = (index % 6) + 1
        msp.add_lwpolyline(
            es.chain_vertices(chain),
            close=is_loop,
            dxfattribs={"layer": layer, "color": color},
        )
    try:
        doc.saveas(OUTBOX / filename)
        print(f"'{filename}' exported")
    except IOError as e:
        print(f"\n****** IOERROR *****\n{str(e)}\n****** IOERROR *****")


def export_edges(filename: str, edges: Sequence[em.Edge]):
    doc = ezdxf.new()
    msp = doc.modelspace()
    for index, edge in enumerate(edges):
        color = (index % 6) + 1
        msp.add_line(edge.start, edge.end, dxfattribs={"layer": "EDGE", "color": color})
    try:
        doc.saveas(OUTBOX / filename)
        print(f"'{filename}' exported")
    except IOError as e:
        print(f"\n****** IOERROR *****\n{str(e)}\n****** IOERROR *****")


def find_consecutive_edges(edges: list[em.Edge]):

    t0 = perf_counter()
    seq_edges = em.find_sequential_chain(edges)
    t1 = perf_counter()
    print(
        f"sequential search found {len(seq_edges)} connected edges in {t1-t0:.4f} seconds"
    )
    print(f"is loop: {em.is_loop(seq_edges)}\n")

    deposit = em.Deposit(edges)
    t0 = perf_counter()
    chains = em.find_all_simple_chains(deposit)
    t1 = perf_counter()
    print(f"find_all_chains() found {len(chains)} chain(s) in {t1-t0:.4f} seconds")
    for index, chain in enumerate(chains):
        is_loop = em.is_loop(chain)
        print(f"{index+1}. chain has {len(chain)} edges, is loop: {is_loop}")

    print("\nsearching first loop with backtracking in modelspace order...")
    t0 = perf_counter()
    loop = em.find_loop(deposit)
    t1 = perf_counter()
    print(f"found first loop with {len(loop)} edges in {t1-t0:.2f} seconds\n")

    print("shuffling edges...\n")
    random.shuffle(edges)
    deposit = em.Deposit(edges)

    print("searching first loop with backtracking in random order...")
    t0 = perf_counter()
    loop = em.find_loop(deposit)
    t1 = perf_counter()
    print(f"found first loop with {len(loop)} edges in {t1-t0:.2f} seconds\n")


def find_all_chains(edges: list[em.Edge], name: str):
    #  sequential searches are fast and work well for ordered entities
    print("find_all_chains_sequential(): ordered")
    t0 = perf_counter()
    chains = list(em.find_all_sequential_chains(edges))
    t1 = perf_counter()
    print(f"found {len(chains)} chains in {t1-t0:.4f} seconds")
    export_chains(name + "_sequential.dxf", chains)

    deposit = em.Deposit(edges)
    print("\nfind_all_chains(): ordered")
    t0 = perf_counter()
    chains = list(em.find_all_simple_chains(deposit))
    t1 = perf_counter()
    print(f"found {len(chains)} chains in {t1-t0:.4f} seconds")
    export_chains(name + "_backtracking.dxf", chains)

    # sequential searches fall apart as soon the entities are not ordered
    print("\nshuffling edges...\n")
    random.shuffle(edges)
    deposit = em.Deposit(edges)

    print("find_all_chains_sequential(): shuffled")
    t0 = perf_counter()
    chains = list(em.find_all_sequential_chains(edges))
    t1 = perf_counter()
    print(f"found {len(chains)} chains in {t1-t0:.4f} seconds")
    export_chains(name + "_shuffled_sequential.dxf", chains)

    print("\nfind_all_simple_chains(): shuffled")
    t0 = perf_counter()
    chains = list(em.find_all_simple_chains(deposit))
    t1 = perf_counter()
    print(f"found {len(chains)} chains in {t1-t0:.4f} seconds")
    export_chains(name + "_shuffled_backtracking.dxf", chains)


def find_all_loops(edges: Sequence[em.Edge], export_dxf):
    print("\nfind_all_loops():")
    gap_tol = 1e-4
    deposit = em.Deposit(edges, gap_tol=gap_tol)
    t0 = perf_counter()
    try:
        loops = em.find_all_loops(deposit, timeout=10)
    except em.TimeoutError as err:
        print(str(err))
        loops = err.solutions
    t1 = perf_counter()
    print(f"found {len(loops)} loops in {t1-t0:.4f} seconds")
    unique_loops = list(em.unique_chains(loops))
    print(f"... {len(unique_loops)} are unique loops")
    export_chains(export_dxf, unique_loops, gap_tol)


def find_all_squares_sequential(edges: Sequence[em.Edge], export_dxf):
    print("\nfind_all_sequential():")
    t0 = perf_counter()
    loops = list(em.find_all_sequential_chains(edges))
    t1 = perf_counter()
    found = sum(em.is_loop(l) for l in loops)
    print(f"found {found} loops in {t1-t0:.4f} seconds")
    export_chains(export_dxf, loops)


def find_open_chains(edges: Sequence[em.Edge], export_dxf):
    print("\nfind_all_open_chains():")
    deposit = em.Deposit(edges)
    t0 = perf_counter()
    try:
        chains = em.find_all_open_chains(deposit, timeout=10)
    except em.TimeoutError as err:
        print(str(err))
        chains = err.solutions
    t1 = perf_counter()
    print(f"found {len(chains)} open chains in {t1-t0:.4f} seconds")
    unique_chains = list(em.unique_chains(chains))
    print(f"... {len(unique_chains)} are unique open chains")
    export_chains(export_dxf, unique_chains)


def chain_type(edges: Sequence[em.Edge]) -> str:
    return "loop" if em.is_loop(edges) else "open chain"


def export_loops(filename: str, loops: list[Sequence[em.Edge]]):
    doc = ezdxf.new()
    msp = doc.modelspace()
    index = 0
    for loop in loops:
        index += 1
        layer = f"LOOP_{index}"
        msp.add_lwpolyline(
            es.chain_vertices(list(em.flatten(loop))),
            dxfattribs={"layer": layer, "color": (index % 6) + 1},
        )
    try:
        doc.saveas(OUTBOX / filename)
        print(f"'{filename}' exported")
    except IOError as e:
        print(f"\n****** IOERROR *****\n{str(e)}\n****** IOERROR *****")


def inside_checker(point: Vec2):
    def is_inside(edges: Sequence[em.Edge]) -> bool:
        if len(edges) < 3:
            return False
        vertices = Vec2.list([e.start for e in edges])
        return is_point_in_polygon_2d(point, vertices) >= 0

    return is_inside


def pack_simple_chains(
    deposit: em.Deposit,
) -> tuple[list[Sequence[em.Edge]], list[em.Edge]]:
    chains = em.find_all_simple_chains(deposit)
    if not chains:
        return [], []

    gap_tol = deposit.gap_tol
    loops: list[Sequence[em.Edge]] = []
    packed_edges: list[em.Edge] = []
    for chain in chains:
        if len(chain) > 1:
            if em.is_loop_fast(chain, gap_tol=gap_tol):
                # these loops have no ambiguities (junctions)
                loops.append(chain)
            else:
                packed_edges.append(em.wrap_simple_chain(chain, gap_tol=gap_tol))
        else:
            packed_edges.append(chain[0])
    return loops, packed_edges


def find_loops_by_edge(deposit: em.Deposit):
    print("pick_near_loop():")
    t0 = perf_counter()
    loops, packed_edges = pack_simple_chains(deposit)
    deposit = em.Deposit(packed_edges, gap_tol=deposit.gap_tol)
    print(f"found {len(loops)} simple loops.")
    print(f"remaining packed edges {len(packed_edges)}.")
    print(deposit.degree_counter())

    todo = set(packed_edges)
    while todo:
        start_edge = todo.pop()
        loop = em.find_loop_by_edge(deposit, start_edge, clockwise=False)
        if loop:
            loops.append(loop)
            todo -= set(loop)

    print(f"found {len(loops)} loops in {perf_counter() - t0:.2f} seconds")
    export_loops("find_loops_by_edge.dxf", loops)


# simple geometry, no ambiguity, no junctions
FILE_1 = "1_polylines.dxf"

# one same as FILE_1 but with added lines to create ambiguity
FILE_2 = "2_polylines.dxf"

# one big loop with 10052 edges, precise drawing
FILE_3 = "3_us_main.dxf"

# world map with one junction, many design inaccuracies
FILE_4 = "4_world.dxf"

# us state borders, congruent lines at common borders between states,
# many design inaccuracies
FILE_5 = "5_us_states.dxf"


def main():
    circle_with_fringes = with_fringes(circle(10_000, 300), count=100, length=10)
    find_all_chains(circle_with_fringes, name="find_all_chains")
    find_all_loops(circle_with_fringes, "find_circle_with_backtracking.dxf")

    grid_of_edges = grid((5, 3), length=10)
    find_all_loops(grid_of_edges, "find_all_loops_in_grid_with_backtracking.dxf")

    squares = grid_of_squares((20, 20), length=10)
    random.shuffle(squares)
    find_all_squares_sequential(squares, "find_all_squares_sequential.dxf")

    squares = grid_of_jiggled_squares((20, 20), length=10)
    random.shuffle(squares)
    find_all_loops(squares, "find_all_jiggled_squares_with_backtracking.dxf")

    print(f"degree counter for {FILE_3}: {em.Deposit(load(FILE_3)).degree_counter()}")

    edges = open_grid(size=(3, 3), length=10)
    random.shuffle(edges)
    # export_edges("open_grid_10x10.dxf", edges=edges)

    edges = open_grid(size=(3, 3), length=10)
    random.shuffle(edges)
    find_open_chains(edges, "find_open_chains_shuffled_backtracking.dxf")

    deposit = em.Deposit(load(FILE_5), gap_tol=0.001)
    edges = em.filter_coincident_edges(deposit, eq_fn=em.line_checker(0.001))
    print(f"{len(edges)} edges are non-congruent edges")

    deposit = em.Deposit(edges)
    print(deposit.degree_counter())
    find_loops_by_edge(deposit)


if __name__ == "__main__":
    main()
