# Copyright (c) 2025, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from pathlib import Path

import ezdxf

from ezdxf import edgeminer as em
from ezdxf import edgesmith as es

CWD = Path(__file__).parent
OUTBOX = Path("~/Desktop/Outbox").expanduser()


def load(filename: str) -> list[em.Edge]:
    doc = ezdxf.readfile(CWD / filename)
    msp = doc.modelspace()
    edges = list(es.edges_from_entities_2d(msp))
    return edges


def make_hatch_with_polyline_path(edges: list[em.Edge], outname: str) -> None:
    doc = ezdxf.new()
    msp = doc.modelspace()
    dxfattribs = {"layer": "HATCH"}
    deposit = em.Deposit(edges)
    for loop in em.find_all_simple_chains(deposit):
        hatch = msp.add_hatch(color=2, dxfattribs=dxfattribs)
        polyline_path = es.polyline_path_from_chain(loop, max_sagitta=0.1)
        hatch.paths.append(polyline_path)
    doc.saveas(OUTBOX / outname)


def make_hatch_without_arcs(edges: list[em.Edge], outname: str) -> None:
    doc = ezdxf.new()
    msp = doc.modelspace()
    dxfattribs = {"layer": "HATCH"}
    deposit = em.Deposit(edges)
    for loop in em.find_all_simple_chains(deposit):
        hatch = msp.add_hatch(color=2, dxfattribs=dxfattribs)
        # 2D path as intermediate_step:
        path2d = es.path2d_from_chain(loop)
        # flatten everything:
        hatch.paths.add_polyline_path(path2d.flattening(distance=0.1))
    doc.saveas(OUTBOX / outname)


def make_hatch_with_edge_path(edges: list[em.Edge], outname: str) -> None:
    doc = ezdxf.new()
    msp = doc.modelspace()
    dxfattribs = {"layer": "HATCH"}
    deposit = em.Deposit(edges)
    for loop in em.find_all_simple_chains(deposit):
        hatch = msp.add_hatch(color=2, dxfattribs=dxfattribs)
        edge_path = es.edge_path_from_chain(loop, max_sagitta=0.1)
        hatch.paths.append(edge_path)
    doc.saveas(OUTBOX / outname)


FILE_6 = "6_closed_loop_with_arcs.dxf"


def main():
    doc = load(FILE_6)
    make_hatch_with_polyline_path(doc, "make_hatch_with_polyline_path.dxf")
    make_hatch_without_arcs(doc, "make_hatch_without_arcs.dxf")
    make_hatch_with_edge_path(doc, "make_hatch_with_edge_path.dxf")


if __name__ == "__main__":
    main()
