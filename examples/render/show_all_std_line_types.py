# Copyright (c) 2019-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.math import Vec3
from ezdxf.tools.standards import linetypes

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows the standard linetypes supported by ezdxf.
# ------------------------------------------------------------------------------


def main():
    # IMPORTANT:
    # The argument setup=True is REQUIRED to create these linetypes otherwise
    # the linetypes are undefined and AutoCAD will not open the DXf file!
    doc = ezdxf.new("R2007", setup=True)
    msp = doc.modelspace()

    # How to change the global linetype scaling:
    doc.header["$LTSCALE"] = 0.5

    p1 = Vec3(0, 0)
    p2 = Vec3(9, 0)
    delta = Vec3(0, -1)
    text_offset = Vec3(0, 0.1)

    for lt in linetypes():
        name = lt[0]
        msp.add_line(p1, p2, dxfattribs={"linetype": name, "lineweight": 25})
        msp.add_text(
            name,
            dxfattribs={"style": "OpenSansCondensed-Light", "height": 0.25},
        ).set_placement(p1 + text_offset)
        p1 += delta
        p2 += delta

    doc.set_modelspace_vport(25, center=(5, -10))
    doc.saveas(CWD / "all_std_line_types.dxf")


if __name__ == "__main__":
    main()
