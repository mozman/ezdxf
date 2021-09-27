# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.addons import text2path
from ezdxf.math import Vec3
from ezdxf import zoom


def add_rect(p1, p2, height):
    p2 = Vec3(p2) + (0, height)
    points = [p1, (p2.x, p1.y), p2, (p1.x, p2.y)]
    msp.add_lwpolyline(points, close=True, dxfattribs={"color": 6})


DIR = Path("~/Desktop/Outbox").expanduser()
doc = ezdxf.new(setup=["styles"])
doc.styles.new("NARROW", dxfattribs={"font": "arialn.ttf"})
msp = doc.modelspace()

p1 = Vec3(0, 0)
p2 = Vec3(12, 0)
height = 1
text = msp.add_text(
    "Arial Narrow",
    dxfattribs={
        "style": "NARROW",
        "layer": "TEXT",
        "height": height,
        "color": 1,
    },
)
text.set_pos(p1, p2, "LEFT")
attr = {"layer": "OUTLINE", "color": 2}
kind = text2path.Kind.SPLINES
for e in text2path.virtual_entities(text, kind):
    e.update_dxf_attribs(attr)
    msp.add_entity(e)

p1 = Vec3(0, 2)
p2 = Vec3(12, 2)
height = 2
text = msp.add_text(
    "OpenSansCondensed-Light",
    dxfattribs={
        "style": "OpenSansCondensed-Light",
        "layer": "TEXT",
        "height": height,
        "color": 1,
    },
)
text.set_pos(p1, p2, "LEFT")
for e in text2path.virtual_entities(text, kind):
    e.update_dxf_attribs(attr)
    msp.add_entity(e)

zoom.extents(msp, factor=1.1)
doc.saveas(DIR / "condensed_fonts.dxf")
