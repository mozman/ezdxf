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
SPACING = 200
TRANSFORMATIONS = [
    ((0, 0), 1, 1, 0),
    ((SPACING, 0), 2, 2, 0),
    ((0, SPACING), -1, -1, 15),
    ((SPACING, SPACING), -2, -2, 15),
]
def main():
    doc = ezdxf.new()
    doc.layers.add("FLAGS")

    flag = doc.blocks.new(name="FLAG")
    flag.add_polyline2d(FLAG_SYMBOL)

    flag_grid = doc.blocks.new(name="FLAG_GRID")
    flag_grid.add_blockref(
        "FLAG",
        (0, 0),
        dxfattribs={
            "layer": "FLAGS",
        },
    ).grid(
        size=(5, 5), spacing=(10, 10)
    )

    msp = doc.modelspace()    
    for location, sx, sy, rotation in TRANSFORMATIONS:
        block_ref = msp.add_blockref( "FLAG_GRID", location, dxfattribs={
            "xscale": sx,
            "yscale": sy,
            "rotation": rotation,
        })

    filename = CWD / "multi_insert_transform.dxf"
    doc.set_modelspace_vport(height=500)
    doc.saveas(filename)
    print(f"drawing '{filename}' created.")


if __name__ == "__main__":
    main()
