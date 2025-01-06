# Copyright (c) 2025, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Sequence
from pathlib import Path


import ezdxf
from ezdxf.document import Drawing
from ezdxf import edgeminer as em
from ezdxf import edgesmith as es

CWD = Path(__file__).parent
OUTBOX = Path("~/Desktop/Outbox").expanduser()


def new_doc() -> Drawing:
    return ezdxf.new()


def load(filename: str) -> list[em.Edge]:
    doc = ezdxf.readfile(CWD / filename)
    msp = doc.modelspace()
    edges = list(es.edges_from_entities_2d(msp))
    return edges


def find_all_simple_chains(edges: Sequence[em.Edge], filename: str):
    deposit = em.Deposit(edges)
    doc = new_doc()
    msp = doc.modelspace()
    for chain in em.find_all_simple_chains(deposit):
        entity = es.lwpolyline_from_chain(chain)
        msp.add_entity(entity)
    doc.saveas(OUTBOX / filename)


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

ALL_FILES = [FILE_1, FILE_2, FILE_3, FILE_4, FILE_5]


def find_chains():
    for filename in ALL_FILES:
        outname = f"find_all_simple_chains_in_{filename}"
        edges = load(filename)
        print(f"\nfind_all_simple_chains() in {filename}")
        try:
            find_all_simple_chains(edges, filename=outname)
        except IOError as e:
            print(f"Failed to export: {outname}")
            print(str(e))
        else:
            print(f"Exported: {outname}")
        # find_all_loops(edges, filename="find_all_loops.dxf")


def find_chains_without_coincident_edges():
    # remove congruent lines to get a simpler result
    outname = f"polylines_without_coincident_edges.dxf"
    edges = load(FILE_5)
    deposit = em.Deposit(edges)
    unique_edges = em.filter_coincident_edges(deposit)
    print(f"Removed {len(edges) - len(unique_edges)} from {len(edges)} edges")
    try:
        find_all_simple_chains(unique_edges, filename=outname)
    except IOError as e:
        print(f"Failed to export: {outname}")
        print(str(e))
    else:
        print(f"Exported: {outname}")


if __name__ == "__main__":
    find_chains()
    find_chains_without_coincident_edges()
