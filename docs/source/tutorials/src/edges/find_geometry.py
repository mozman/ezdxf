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
    doc.saveas(OUTBOX/"flattened_hatch.dxf")


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


if __name__ == "__main__":
    # basics()
    flatten_3d_entities()
