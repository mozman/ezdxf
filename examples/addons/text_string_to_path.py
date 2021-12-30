#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
#
# Requires: matplotlib

from pathlib import Path
import ezdxf
from ezdxf import path, zoom
from ezdxf.tools import fonts
from ezdxf.addons import text2path
from ezdxf.enums import TextEntityAlignment
DIR = Path("~/Desktop/Outbox").expanduser()
fonts.load()

doc = ezdxf.new()
doc.layers.new("OUTLINE")
doc.layers.new("FILLING")
msp = doc.modelspace()

attr = {"layer": "OUTLINE", "color": 1}
ff = fonts.FontFace(family="Noto Sans SC")
s = "Noto Sans SC 0123456789 %@ 中国文字"
align = TextEntityAlignment.LEFT
path.render_splines_and_polylines(
    msp, text2path.make_paths_from_str(s, ff, align=align), dxfattribs=attr
)

attr["layer"] = "FILLING"
attr["color"] = 2
for hatch in text2path.make_hatches_from_str(
    s, ff, align=align, dxfattribs=attr
):
    msp.add_entity(hatch)

zoom.extents(msp)
doc.saveas(DIR / "text2path.dxf")
