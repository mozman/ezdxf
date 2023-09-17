# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pathlib
import ezdxf
from ezdxf import bbox, transform


CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def main():
    doc = ezdxf.new()
    msp = doc.modelspace()

    # create a new block definition
    circle_block = doc.blocks.new("CIRCLE")
    circle_block.add_circle((100, 100), 3)
    current_base_point = circle_block.base_point

    # add a block reference to the model space
    msp.add_blockref("CIRCLE", (0, 0))
    doc.saveas(CWD / "original.dxf")

    # get new base point from bounding box detection:
    extents = bbox.extents(circle_block, fast=True)
    new_base_point = extents.center  # or extents.extmin/extmax ...
    offset = current_base_point - new_base_point

    circle_block.base_point = new_base_point
    doc.saveas(CWD / "move_base_point.dxf")

    # WARNING:
    # This solution does not update the INSERT entities, therefore the block references
    # are wrong located!!!

    # Update INSERT entities:
    # get ALL block references for block "CIRCLE"
    block_refs = doc.query("INSERT[name=='CIRCLE']")
    # translate all block references by offset vector
    transform.translate(block_refs, -offset)

    doc.saveas(CWD / "updated_block_references.dxf")


if __name__ == "__main__":
    assert ezdxf.version >= (1, 1, 0), "This example requires ezdxf v1.1 or newer."
    main()
