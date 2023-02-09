# Copyright (c) 2010-2022 Manfred Moitzi
# License: MIT License
import pathlib
import random
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to add block references and automatically create ATTRIB
# entities from ATTDEF templates.
#
# tutorial: https://ezdxf.mozman.at/docs/tutorials/blocks.html
# ------------------------------------------------------------------------------


def get_random_point():
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return x, y


SAMPLE_COORDS = [get_random_point() for x in range(50)]
FLAG_SYMBOL = [(0, 0), (0, 5), (4, 3), (0, 3)]


def main():
    doc = ezdxf.new("R2007")
    doc.layers.add("FLAGS")
    msp = doc.modelspace()

    flag = doc.blocks.new(name="FLAG")

    # Add dxf entities to the block (the flag).
    # Use base_point = (x, y) to define a different base_point than (0, 0).
    flag.add_polyline2d(FLAG_SYMBOL)
    flag.add_circle(center=(0, 0), radius=0.4, dxfattribs={"color": 1})

    # Create the ATTRIB templates as ATTDEF entities:
    flag.add_attdef(
        tag="NAME", insert=(0.5, -0.5), dxfattribs={"height": 0.5, "color": 3}
    )
    flag.add_attdef(
        tag="XPOS", insert=(0.5, -1.0), dxfattribs={"height": 0.25, "color": 4}
    )
    flag.add_attdef(
        tag="YPOS", insert=(0.5, -1.5), dxfattribs={"height": 0.25, "color": 4}
    )

    for number, point in enumerate(SAMPLE_COORDS):
        # Create the value dictionary for the ATTRIB entities, key is the tag
        # name of the ATTDEF entity and the value is the content string of the
        # ATTRIB entity:
        values = {
            "NAME": f"P({number + 1})",
            "XPOS": f"x = {point[0]:.3f}",
            "YPOS": f"y = {point[1]:.3f}",
        }
        random_scale = 0.5 + random.random() * 2.0
        block_ref = msp.add_blockref(
            "FLAG", point, dxfattribs={"layer": "FLAGS", "rotation": -15}
        ).set_scale(random_scale)

        # This method avoids the wrapper block of the add_auto_blockref() method,
        # but the visual results may not match the results of CAD applications,
        # especially for non-uniform scaling.
        block_ref.add_auto_attribs(values)

        # The example "auto_blockref.py" shows the "wrapping" strategy to
        # automatically add ATTRIB entities to block references.

    filename = CWD / "flags_with_attribs.dxf"
    doc.set_modelspace_vport(height=200)
    doc.saveas(filename)
    print(f"drawing '{filename}' created.")


if __name__ == "__main__":
    main()
