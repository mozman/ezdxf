# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License

from pathlib import Path
import random
import ezdxf
from ezdxf.addons import r12writer
from ezdxf.tools.standards import setup_dimstyle

DIR = Path("~/Desktop/Outbox").expanduser()
XSIZE, YSIZE = (100, 100)
COUNT = 1000
POINTS = [
    (random.random() * XSIZE, random.random() * YSIZE) for _ in range(COUNT)
]
XREF = "points.dxf"
# scale 1:1000; text size H = 2.5mm on paper; 1 drawing unit = 1m
DIMSTYLE = "USR_M_1000_H25_M"

with r12writer(str(DIR / XREF)) as r12:
    for point in POINTS:
        r12.add_point(point, layer="Points")

doc = ezdxf.new("R2000", setup=True)
doc.add_xref_def(filename=".\\" + XREF, name="points_xref")

msp = doc.modelspace()
msp.add_blockref(name="points_xref", insert=(0, 0))
setup_dimstyle(
    doc, fmt=DIMSTYLE, style=ezdxf.options.default_dimension_text_style
)
msp.add_aligned_dim(p1=(0, 0), p2=(0, 100), distance=5, dimstyle=DIMSTYLE)
msp.add_aligned_dim(p1=(0, 100), p2=(100, 100), distance=5, dimstyle=DIMSTYLE)
doc.set_modelspace_vport(height=YSIZE * 1.25, center=(XSIZE / 2, YSIZE / 2))
doc.saveas(DIR / "host.dxf")
