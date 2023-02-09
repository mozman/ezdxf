#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import ezdxf
from ezdxf import path, zoom
from ezdxf.tools import fonts
from ezdxf.addons import text2path
from ezdxf.enums import TextEntityAlignment

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")
# ------------------------------------------------------------------------------
# This example shows how to triangulate text-strings into SOLID entities.
#
# docs: https://ezdxf.mozman.at/docs/addons/text2path.html
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new()
    doc.layers.new("OUTLINE")
    doc.layers.new("FILLING")
    msp = doc.modelspace()

    attr = {"layer": "OUTLINE", "color": 1}
    ff = fonts.FontFace(family="Arial")
    s = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"

    align = TextEntityAlignment.LEFT
    paths = text2path.make_paths_from_str(s, ff, align=align)
    path.render_splines_and_polylines(msp, paths, dxfattribs=attr)

    attr["layer"] = "FILLING"
    attr["color"] = 2
    colors = [1, 2, 3, 4, 5, 6, 7]
    count = len(colors)
    for index, points in enumerate(path.triangulate(paths, 0.01)):
        attr["color"] = colors[index % count]
        msp.add_solid(points, dxfattribs=attr)

    zoom.extents(msp)
    doc.saveas(CWD / "text2triangles.dxf")


if __name__ == "__main__":
    main()
