# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
from random import random
from pathlib import Path
from ezdxf.addons import r12writer

OUTBOX = Path("~/Desktop/Outbox").expanduser()
MAX_X_COORD = 1000.0
MAX_Y_COORD = 1000.0
CIRCLE_COUNT = 10000

with r12writer(OUTBOX / "quick_and_dirty_dxf_r12.dxf") as dxf:
    dxf.add_line((0, 0), (17, 23))
    dxf.add_circle((0, 0), radius=2)
    dxf.add_arc((0, 0), radius=3, start=0, end=175)
    dxf.add_solid([(0, 0), (1, 0), (0, 1), (1, 1)])
    dxf.add_point((1.5, 1.5))
    dxf.add_polyline([(5, 5), (7, 3), (7, 6)])  # 2d polyline
    dxf.add_polyline([(4, 3, 2), (8, 5, 0), (2, 4, 9)])  # 3d polyline
    dxf.add_text("test the text entity", align="MIDDLE_CENTER")

with r12writer(OUTBOX / "many_circles.dxf") as dxf:
    for i in range(CIRCLE_COUNT):
        dxf.add_circle(
            (MAX_X_COORD * random(), MAX_Y_COORD * random()), radius=2
        )

with r12writer(OUTBOX / "many_circles_bin.dxf", fmt="bin") as dxf:
    for i in range(CIRCLE_COUNT):
        dxf.add_circle(
            (MAX_X_COORD * random(), MAX_Y_COORD * random()), radius=2
        )

LINETYPES = [
    "CONTINUOUS",
    "CENTER",
    "CENTERX2",
    "CENTER2",
    "DASHED",
    "DASHEDX2",
    "DASHED2",
    "PHANTOM",
    "PHANTOMX2",
    "PHANTOM2",
    "DASHDOT",
    "DASHDOTX2",
    "DASHDOT2",
    "DOT",
    "DOTX2",
    "DOT2",
    "DIVIDE",
    "DIVIDEX2",
    "DIVIDE2",
]

with r12writer(OUTBOX / "r12_linetypes.dxf", fixed_tables=True) as dxf:
    for n, ltype in enumerate(LINETYPES):
        dxf.add_line((0, n), (10, n), linetype=ltype)
        dxf.add_text(ltype, (0, n + 0.1), height=0.25, style="OpenSans")
