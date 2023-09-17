# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pathlib
import ezdxf
from ezdxf import bbox, transform


CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


# This example requires ezdxf v1.1.0 or later.
def main():
    doc = ezdxf.new()
    msp = doc.modelspace()

    # create a new block definition, with the default base point at (0, 0):
    circle_block = doc.blocks.new("CIRCLE")
    circle_block.add_circle((100, 100), 3)

    # add a block reference to the model space
    msp.add_blockref("CIRCLE", (0, 0))
    doc.saveas(CWD / "original.dxf")

    # get new base point from bounding box of the block definition:
    extents = bbox.extents(circle_block, fast=True)
    new_base_point = extents.center
    # extents.extmin is the lower left corner
    # extents.extmax is the upper right corner
    # offset vector for block references:
    offset = new_base_point - circle_block.base_point

    circle_block.base_point = new_base_point
    doc.saveas(CWD / "move_base_point.dxf")

    # WARNING:
    # So far the INSERT entities have not been updated, hence the block references are
    # mislocated!!!

    # Update INSERT entities:
    # get ALL block references for block "CIRCLE"
    block_refs = doc.query("INSERT[name=='CIRCLE']")
    # translate all block references by offset vector
    transform.translate(block_refs, offset)

    doc.saveas(CWD / "updated_block_references.dxf")


if __name__ == "__main__":
    if ezdxf.version >= (1, 1, 0):
        main()
    else:
        print("This example requires ezdxf v1.1.0 or later.")
