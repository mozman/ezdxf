# Copyright (c) 2021-2023, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf import path, zoom
from ezdxf.fonts import fonts
from ezdxf.addons import text2path
from ezdxf.enums import TextEntityAlignment

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to convert a text-string to outline paths.
#
# docs: https://ezdxf.mozman.at/docs/addons/text2path.html
# ------------------------------------------------------------------------------

FONT = "isocp.shx"


def main():
    doc = ezdxf.new()
    doc.layers.new("STROKE")
    doc.layers.new("TEXT")
    doc.styles.add("TXT", font=FONT)
    msp = doc.modelspace()

    attr = {"layer": "STROKE", "color": 1}
    ff = fonts.FontFace(filename=FONT)
    s = f'AXxp written with stroke font "{FONT}"'
    align = TextEntityAlignment.LEFT
    path.render_splines_and_polylines(
        msp, text2path.make_paths_from_str(s, ff, align=align, size=1), dxfattribs=attr
    )
    msp.add_text(s, height=1, dxfattribs={"layer": "TEXT", "color": 2, "style": "TXT"})
    font_ = fonts.make_font(FONT, 1)
    bottom = font_.measurements.baseline
    msp.add_line((0, bottom), (30, bottom), dxfattribs={"color": 5})
    top = bottom + font_.measurements.cap_height
    msp.add_line((0, top), (30, top), dxfattribs={"color": 5})
    zoom.extents(msp)
    doc.saveas(CWD / "shx2path.dxf")


if __name__ == "__main__":
    main()
