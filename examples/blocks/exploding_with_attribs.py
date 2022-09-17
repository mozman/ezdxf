# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
from typing import cast, Tuple
import pathlib
import ezdxf
import random

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to explode block references with attached ATTRIB
# entities.
#
# https://ezdxf.mozman.at/docs/tutorials/blocks.html
# ------------------------------------------------------------------------------


def get_random_point() -> Tuple[int, int]:
    """Returns random x, y coordinates."""
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return x, y


def main():
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    flag = doc.blocks.new(name="FLAG")
    flag.add_lwpolyline(
        [(0, 0), (0, 5), (4, 3), (0, 3)]
    )  # the flag symbol as 2D polyline
    flag.add_circle(
        (0, 0), 0.4, dxfattribs={"color": 1}
    )  # mark the base point with a circle
    flag.add_attdef("NAME", (0.5, -0.5), dxfattribs={"height": 0.5, "color": 3})
    flag.add_attdef(
        "XPOS", (0.5, -1.0), dxfattribs={"height": 0.25, "color": 4}
    )
    flag.add_attdef(
        "YPOS", (0.5, -1.5), dxfattribs={"height": 0.25, "color": 4}
    )

    # Create 50 random placing points.
    placing_points = [get_random_point() for _ in range(50)]

    for number, point in enumerate(placing_points):
        # values is a dict with the attribute tag as item-key and
        # the attribute text content as item-value.
        values = {
            "NAME": f"P({number + 1})",
            "XPOS": f"x = {point[0]:.3f}",
            "YPOS": f"y = {point[1]:.3f}",
        }

        # Every flag has a different scaling and a rotation of +15 deg.
        random_scale = 0.5 + random.random() * 2.0
        msp.add_auto_blockref(
            "FLAG", point, values, dxfattribs={"rotation": 15}
        ).set_scale(random_scale)

    doc.set_modelspace_vport(200)
    doc.saveas(CWD / "flags-with-attribs.dxf")

    # Explode auto block references, wrapped into anonymous block references
    for auto_blockref in msp.query("INSERT"):
        cast("Insert", auto_blockref).explode()

    # Explode flag block references
    for flag in msp.query("INSERT[name=='FLAG']"):
        cast("Insert", flag).explode()

    doc.saveas(CWD / "flags-exploded.dxf")


if __name__ == "__main__":
    main()
