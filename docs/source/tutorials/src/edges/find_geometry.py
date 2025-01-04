#  Copyright (c) 2025, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import pathlib

import random
import ezdxf
from ezdxf import edgeminer, edgesmith, colors

OUTBOX = pathlib.Path("~/Desktop/Outbox").expanduser()
CWD = pathlib.Path(__file__).parent


def new_doc():
    doc = ezdxf.new()
    doc.header["$LWDISPLAY"] = 1
    return doc, doc.modelspace()


def basics():
    # create a new doc
    doc, msp = new_doc()

    lwp = msp.add_lwpolyline(
        [(0, 0), (5, 0, -0.5), (5, 5), (0, 5)],
        format="xyb",
        close=True,
        dxfattribs={"color": colors.YELLOW, "lineweight": 30},
    )
    # explode into lines and arcs
    entities = lwp.explode()
    doc.saveas(OUTBOX / "src.dxf")

    # create a new doc
    doc, msp = new_doc()
    edges = list(edgesmith.edges_from_entities_2d(entities))
    chain = edgeminer.find_sequential_chain(edges)
    lwp2 = edgesmith.lwpolyline_from_chain(
        chain, dxfattribs={"color": colors.RED, "lineweight": 30}
    )
    msp.add_entity(lwp2)
    doc.saveas(OUTBOX / "result1.dxf")

    # create a new doc
    doc, msp = new_doc()

    # start again and shuffle the edges
    edges = list(edgesmith.edges_from_entities_2d(entities))
    random.shuffle(edges)

    # A deposit maintains a spatial search tree to optimize the search in heap of
    # unordered edges.
    deposit = edgeminer.Deposit(edges)
    start = edges[0]  # start at any arbitrary edge
    chain = edgeminer.find_simple_chain(deposit, start)
    lwp3 = edgesmith.lwpolyline_from_chain(
        chain, dxfattribs={"color": colors.RED, "lineweight": 30}
    )
    msp.add_entity(lwp3)
    doc.saveas(OUTBOX / "result2.dxf")

    # create a new doc
    doc, msp = new_doc()
    hatch = msp.add_hatch(color=2)
    boundary_path = edgesmith.polyline_path_from_chain(chain)
    hatch.paths.append(boundary_path)
    doc.saveas(OUTBOX / "hatch1.dxf")


def flatten_3d_entities():
    doc = ezdxf.readfile(CWD / "edges_3d.dxf")
    msp = doc.modelspace()

    # create edges and search index
    edges = list(edgesmith.edges_from_entities_2d(msp))
    deposit = edgeminer.Deposit(edges)
    # find a chain
    chain = edgeminer.find_simple_chain(deposit, edges[0])
    # add a hatch and add the boundary path
    hatch = msp.add_hatch(color=colors.BLUE)
    boundary_path = edgesmith.polyline_path_from_chain(chain, max_sagitta=0.01)
    hatch.paths.append(boundary_path)
    doc.saveas(OUTBOX / "flattened_hatch.dxf")


def find_all_simple_chains():
    doc = ezdxf.readfile(CWD / "junctions.dxf")
    msp = doc.modelspace()
    lines = msp.query("LINE")
    edges = list(edgesmith.edges_from_entities_2d(lines))
    deposit = edgeminer.Deposit(edges)
    chains = edgeminer.find_all_simple_chains(deposit)

    out = ezdxf.new()
    msp = out.modelspace()
    color = 1
    for chain in chains:
        polyline = edgesmith.lwpolyline_from_chain(chain, dxfattribs={"color": color})
        msp.add_entity(polyline)
        color += 1
    out.saveas(OUTBOX / "simple_chains.dxf")


def find_all_loops():
    doc = ezdxf.readfile(CWD / "junctions.dxf")
    msp = doc.modelspace()
    lines = msp.query("LINE")
    edges = list(edgesmith.edges_from_entities_2d(lines))
    deposit = edgeminer.Deposit(edges)
    print(deposit.degree_counter())
    loops = edgeminer.find_all_loops(deposit)
    print(f"Found {len(loops)} loops.")
    out = ezdxf.new()
    msp = out.modelspace()
    color = 1
    for loop in loops:
        layer = f"LOOP_{color}"
        polyline = edgesmith.lwpolyline_from_chain(
            loop, dxfattribs={"color": color, "layer": layer}
        )
        msp.add_entity(polyline)
        color += 1
    out.saveas(OUTBOX / "loops.dxf")


def find_loop_by_edge():
    doc = ezdxf.readfile(CWD / "junctions.dxf")
    msp = doc.modelspace()
    lines = msp.query("LINE")
    edges = list(edgesmith.edges_from_entities_2d(lines))
    deposit = edgeminer.Deposit(edges)

    start = edges[0]
    loop1 = edgeminer.find_loop_by_edge(deposit, start, clockwise=True)
    loop2 = edgeminer.find_loop_by_edge(deposit, start, clockwise=False)
    out = ezdxf.new()
    msp = out.modelspace()
    color = 1
    for loop in [loop1, loop2]:
        layer = f"LOOP_{color}"
        polyline = edgesmith.lwpolyline_from_chain(
            loop, dxfattribs={"color": color, "layer": layer}
        )
        msp.add_entity(polyline)
        color += 1
    out.saveas(OUTBOX / "find_loop_by_edge.dxf")


def find_loop_by_pick_point():
    doc = ezdxf.readfile(CWD / "junctions.dxf")
    msp = doc.modelspace()
    lines = msp.query("LINE")
    edges = list(edgesmith.edges_from_entities_2d(lines))
    pick_point = (110, 50)

    # 1. find a starting edge near the pick-point
    intersecting_edges = edgesmith.intersecting_edges_2d(edges, pick_point)
    if not len(intersecting_edges):
        print("no intersection found")
        return

    hatch = msp.add_hatch(color=2)
    msp.add_circle(pick_point, radius=0.5, dxfattribs={"color": 6})

    # take the closest edge as starting edge.
    start = intersecting_edges[0].edge

    # 2. find the best candidates
    deposit = edgeminer.Deposit(edges)
    candidates = [
        edgeminer.find_loop_by_edge(deposit, start, clockwise=True),
        edgeminer.find_loop_by_edge(deposit, start, clockwise=False),
    ]

    # 3. sort candidates by area
    candidates.sort(key=edgesmith.loop_area)
    for loop in candidates:
        # 4. take the smallest loop which contains the pick-point
        if edgesmith.is_inside_polygon_2d(loop, pick_point):
            hatch.paths.append(edgesmith.polyline_path_from_chain(loop))
            break
    else:
        print("no loop found")
        return
    doc.saveas(OUTBOX / "find_loop_by_pick_point.dxf")


if __name__ == "__main__":
    # basics()
    # flatten_3d_entities()
    # find_all_simple_chains()
    # find_all_loops()
    # find_loop_by_edge()
    find_loop_by_pick_point()
