# Copyright (c) 2011-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create a BLOCK definition and a block reference
# (INSERT entity).
#
# tutorial: https://ezdxf.mozman.at/docs/tutorials/blocks.html
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new("AC1009")

    # Create a BLOCK definition:
    block = doc.blocks.new("TEST")
    block.add_line((-1, -1), (+1, +1))
    block.add_line((-1, +1), (+1, -1))

    # Create a block reference (INSERT entity):
    ms = doc.modelspace()
    ms.add_blockref("TEST", (5, 5))
    doc.saveas(CWD / "using_blocks.dxf")


if __name__ == "__main__":
    main()
