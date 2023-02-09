# Copyright (c) 2019-2022 Manfred Moitzi
# License: MIT License
import pathlib

import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to transform entities by putting them into an anonymous
# BLOCK and INSERT them transformed. This was the only way to transform entities
# by ezdxf before the general transformation support was added in version v0.14.
# ------------------------------------------------------------------------------


def main(size=5):
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_polyline2d([(0, 0), (size, 0), (size, size), (0, size)], close=True)
    msp.add_circle((size / 2, size / 2), radius=size / 2)

    doc.saveas(CWD / "transformation_example_before.dxf")

    # create a new anonymous block
    block = doc.blocks.new_anonymous_block(base_point=(0, 0))
    # move entities from modelspace to the new block
    # create a list, because entities are removed from modelspace while iterating
    for entity in list(msp):
        msp.move_to_layout(entity, block)

    # insert block wherever you want
    msp.add_blockref(
        block.name,
        insert=(10, 10),
        dxfattribs={
            "rotation": 23,  # with rotation
            "xscale": 1.5,  # and none uniform scaling
            "yscale": 3.7,
        },
    )
    doc.saveas(CWD / "transformation_example_after.dxf")


if __name__ == '__main__':
    main()
