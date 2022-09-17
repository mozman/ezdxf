# Copyright (c) 2020-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to render a single block reference multiple times in a
# regular grid.
#
# tutorial: https://ezdxf.mozman.at/docs/tutorials/blocks.html
# ------------------------------------------------------------------------------


FLAG_SYMBOL = [(0, 0), (0, 5), (4, 3), (0, 3)]


def main():
    doc = ezdxf.new()
    doc.layers.add("FLAGS")

    flag = doc.blocks.new(name="FLAG")
    flag.add_polyline2d(FLAG_SYMBOL)
    flag.add_circle((0, 0), 0.4, dxfattribs={"color": 1})

    # Define some attribute templates as ATTDEF entities:
    flag.add_attdef(
        tag="NAME", insert=(0.5, -0.5), dxfattribs={"height": 0.5, "color": 3}
    )
    flag.add_attdef(
        tag="XPOS", insert=(0.5, -1.0), dxfattribs={"height": 0.25, "color": 4}
    )
    flag.add_attdef(
        tag="YPOS", insert=(0.5, -1.5), dxfattribs={"height": 0.25, "color": 4}
    )
    modelspace = doc.modelspace()
    location = (0, 0)
    values = {
        "NAME": "Flag",
        "XPOS": f"x = {location[0]:.3f}",
        "YPOS": f"y = {location[1]:.3f}",
    }

    block_ref = modelspace.add_blockref(
        "FLAG",
        location,
        dxfattribs={
            "layer": "FLAGS",
        },
    ).grid(
        size=(5, 5), spacing=(10, 10)
    )  # render multiple blocks
    block_ref.dxf.rotation = 15
    block_ref.add_auto_attribs(values)

    filename = CWD / "multi_insert_with_attribs.dxf"
    doc.set_modelspace_vport(height=200)
    doc.saveas(filename)
    print(f"drawing '{filename}' created.")


if __name__ == "__main__":
    main()
