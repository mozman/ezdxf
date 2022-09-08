# Copyright (c) 2021-2022, Manfred Moitzi
# License: MIT License

import pathlib
import ezdxf
from ezdxf import disassemble, zoom
from ezdxf.tools import fonts

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

fonts.load()

FILES = [
    "text_fonts.dxf",
    "text_oblique_rotate.dxf",
    "text_mirror_true_type_font.dxf",
    "text_stacked_shx_font.dxf",
]

# ------------------------------------------------------------------------------
# This example draws frames around existing text entities in DXF files locates
# at ../../examples_dxf/<filename>
#
# This shows the difference of text size calculation between Matplotlib and CAD
# applications.
# ------------------------------------------------------------------------------


def main():
    for filename in FILES:
        print(f"Processing: {filename}")
        doc = ezdxf.readfile(
            pathlib.Path(__file__).parent.parent / "examples_dxf" / filename
        )
        msp = doc.modelspace()

        # required to switch layer on/off
        doc.layers.add("TEXT_FRAME", color=6)
        for frame in disassemble.to_primitives(msp.query("TEXT")):
            msp.add_lwpolyline(
                frame.vertices(), close=True, dxfattribs={"layer": "TEXT_FRAME"}
            )

        zoom.extents(msp, factor=1.1)
        doc.saveas(CWD / filename)


if __name__ == "__main__":
    main()
