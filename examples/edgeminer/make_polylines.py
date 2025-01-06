# Copyright (c) 2025, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from pathlib import Path

import ezdxf

from ezdxf import colors
from ezdxf import edgeminer as em
from ezdxf import edgesmith as es

CWD = Path(__file__).parent
OUTBOX = Path("~/Desktop/Outbox").expanduser()


def load(filename: str) -> list[em.Edge]:
    doc = ezdxf.readfile(CWD / filename)
    msp = doc.modelspace()
    edges = list(es.edges_from_entities_2d(msp))
    return edges


def make_polyline_with_arcs(edges: list[em.Edge], outname: str) -> None:
    doc = ezdxf.new()
    doc.layers.add("LWPOLYLINE", color=colors.RED)
    msp = doc.modelspace()
    dxfattribs = {"layer": "LWPOLYLINE"}
    deposit = em.Deposit(edges)
    for loop in em.find_all_simple_chains(deposit):
        polyline = es.lwpolyline_from_chain(loop, dxfattribs=dxfattribs, max_sagitta=.1)
        msp.add_entity(polyline)
    doc.saveas(OUTBOX / outname)


def make_polyline_without_arcs(edges: list[em.Edge], outname: str) -> None:
    doc = ezdxf.new()
    doc.layers.add("LWPOLYLINE", color=colors.RED)
    msp = doc.modelspace()
    dxfattribs = {"layer": "LWPOLYLINE"}
    deposit = em.Deposit(edges)
    for loop in em.find_all_simple_chains(deposit):
        # 2D path as intermediate_step:
        path2d = es.path2d_from_chain(loop)
        # flatten everything:
        msp.add_lwpolyline(path2d.flattening(distance=0.1), dxfattribs=dxfattribs)
    doc.saveas(OUTBOX / outname)


FILE_6 = "6_closed_loop_with_arcs.dxf"


def main():
    edges = load(FILE_6)
    make_polyline_with_arcs(edges, "make_polyline_with_arcs.dxf")
    make_polyline_without_arcs(edges, "make_polyline_without_arcs.dxf")


if __name__ == "__main__":
    main()
