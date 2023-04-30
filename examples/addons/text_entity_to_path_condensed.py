# Copyright (c) 2021-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.enums import TextEntityAlignment
from ezdxf.addons import text2path
from ezdxf.math import Vec3
from ezdxf import zoom

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to convert TEXT entities to outline paths.
#
# docs: https://ezdxf.mozman.at/docs/addons/text2path.html
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new(setup=["styles"])
    arial_narrow = doc.styles.add("NARROW", font="ArialN.ttf")
    # Extended font data is required for "Arial Narrow", why? - ask Autodesk!
    arial_narrow.set_extended_font_data("Arial Narrow")
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
    text.set_placement(p1, p2, TextEntityAlignment.LEFT)
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
    text.set_placement(p1, p2, TextEntityAlignment.LEFT)
    for e in text2path.virtual_entities(text, kind):
        e.update_dxf_attribs(attr)
        msp.add_entity(e)

    zoom.extents(msp, factor=1.1)
    doc.saveas(CWD / "condensed_fonts.dxf")


if __name__ == "__main__":
    main()
