# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf import zoom

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to convert an ARC into a SPLINE.
# ------------------------------------------------------------------------------


def main():
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
    doc.saveas(CWD / "spline_from_arc.dxf")


if __name__ == "__main__":
    main()
