# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
import pathlib
import math
import ezdxf
from ezdxf import zoom

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to convert an ELLIPSE into a SPLINE.
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new()
    msp = doc.modelspace()

    ellipse = msp.add_ellipse(
        center=(0, 0),
        major_axis=(1, 0),
        ratio=0.5,
        start_param=0,
        end_param=math.tau,
        dxfattribs={"layer": "ellipse"},
    )

    spline = ellipse.to_spline(replace=False)
    spline.dxf.layer = "B-spline"
    spline.dxf.color = 1

    zoom.extents(msp)
    doc.saveas(CWD / "spline_from_ellipse.dxf")


if __name__ == "__main__":
    main()
