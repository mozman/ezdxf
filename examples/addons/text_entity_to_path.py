# Copyright (c) 2021-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import text2path
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Vec3
from ezdxf import path

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to convert TEXT entities to outline paths.
#
# docs: https://ezdxf.mozman.at/docs/addons/text2path.html
# ------------------------------------------------------------------------------


def add_rect(msp, p1, p2, height):
    p2 = Vec3(p2) + (0, height)
    points = [p1, (p2.x, p1.y), p2, (p1.x, p2.y)]
    msp.add_lwpolyline(points, close=True, dxfattribs={"color": 6})


def main():
    doc = ezdxf.new(setup=["styles"])
    msp = doc.modelspace()

    p1 = Vec3(0, 0)
    p2 = Vec3(12, 0)
    height = 1
    text = msp.add_text(
        "OpenSansCondensed-Light ALIGNED",
        dxfattribs={
            "style": "OpenSansCondensed-Light",
            "layer": "TEXT",
            "height": height,
            "color": 1,
        },
    )
    text.set_placement(p1, p2, TextEntityAlignment.ALIGNED)
    attr = {"layer": "OUTLINE", "color": 2}
    path.render_splines_and_polylines(
        msp, text2path.make_paths_from_entity(text), dxfattribs=attr
    )
    add_rect(msp, p1, p2, height)

    p1 = Vec3(0, 2)
    p2 = Vec3(12, 2)
    height = 2
    text = msp.add_text(
        "OpenSansCondensed-Light FIT",
        dxfattribs={
            "style": "OpenSansCondensed-Light",
            "layer": "TEXT",
            "height": height,
            "color": 1,
        },
    )
    text.set_placement(p1, p2, TextEntityAlignment.FIT)
    path.render_splines_and_polylines(
        msp, text2path.make_paths_from_entity(text), dxfattribs=attr
    )
    add_rect(msp, p1, p2, height)

    doc.set_modelspace_vport(10, (6, 2))
    doc.saveas(CWD / "entity2path.dxf")


if __name__ == "__main__":
    main()
