# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf import zoom

DIR = Path("~/Desktop/outbox").expanduser()

doc = ezdxf.new()
msp = doc.modelspace()


arc = msp.add_arc(
    center=(0, 0),
    radius=1.0,
    start_angle=0,
    end_angle=360,
    dxfattribs={"layer": "arc"},
)

spline = arc.to_spline(replace=False)
spline.dxf.layer = "B-spline"
spline.dxf.color = 1

zoom.extents(msp)
doc.saveas(DIR / "spline_from_arc.dxf")
