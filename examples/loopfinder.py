# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Sequence

from pathlib import Path

import ezdxf
from ezdxf import loopfinder
from ezdxf.math import Vec2, Matrix44

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")

    #   0   1   3
    # 4 +-K-+-L-+
    #   |   |   |
    #   H   I   J
    #   |   |   |
    # 1 +-F-+-G-+
    #   |   |   |
    #   C   D   E
    #   |   |   |
    # 0 +-A-+-B-+

EDGES = [
    loopfinder.Edge(Vec2(0, 0), Vec2(1, 0), 1, payload="A"),
    loopfinder.Edge(Vec2(1, 0), Vec2(3, 0), 2, payload="B"),
    loopfinder.Edge(Vec2(0, 0), Vec2(0, 1), 1, payload="C"),
    loopfinder.Edge(Vec2(1, 0), Vec2(1, 1), 1, payload="D"),
    loopfinder.Edge(Vec2(3, 0), Vec2(3, 1), 1, payload="E"),
    loopfinder.Edge(Vec2(0, 1), Vec2(1, 1), 1, payload="F"),
    loopfinder.Edge(Vec2(1, 1), Vec2(3, 1), 2, payload="G"),
    loopfinder.Edge(Vec2(0, 1), Vec2(0, 4), 3, payload="H"),
    loopfinder.Edge(Vec2(1, 1), Vec2(1, 4), 3, payload="I"),
    loopfinder.Edge(Vec2(3, 1), Vec2(3, 4), 3, payload="J"),
    loopfinder.Edge(Vec2(0, 4), Vec2(1, 4), 1, payload="K"),
    loopfinder.Edge(Vec2(1, 4), Vec2(3, 4), 2, payload="L"),
]
COLUMNS = 5


def vertices(edges: Sequence[loopfinder.Edge]) -> Sequence[Vec2]:
    return [edge.start for edge in edges]


def collect_payload(edges: Sequence[loopfinder.Edge]) -> str:
    return ",".join([e.payload for e in edges])


def main() -> None:
    doc = ezdxf.new()
    doc.styles.add("ARIAL", font="arial.ttf")
    msp = doc.modelspace()
    text_attribs = {"char_height": 0.1, "style": "ARIAL"}

    solutions = loopfinder.find_all_loops(EDGES)
    print(f"found {len(solutions)} solutions")
    for index, edges in enumerate(solutions):
        x = index % COLUMNS * 5
        y = index // COLUMNS * 5
        m = Matrix44.translate(x, y, 0)
        polyline = msp.add_lwpolyline(vertices(edges), close=True)
        polyline.transform(m)
        signature = collect_payload(edges) + f" length={loopfinder.loop_length(edges)}"
        msp.add_mtext(signature, dxfattribs=text_attribs).set_location((x, y - 0.05))
    doc.saveas(CWD / "loops.dxf")


if __name__ == "__main__":
    main()
