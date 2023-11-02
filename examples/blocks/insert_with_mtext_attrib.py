# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def main():
    doc = ezdxf.new(dxfversion="R2018")
    # create a new block definition:
    block = doc.blocks.new("TEST")
    block.add_circle((0, 0), 1)

    msp = doc.modelspace()
    # create a block reference in modelspace:
    insert = msp.add_blockref("TEST", (0, 0))
    # add a single line attribute to the block reference:
    attrib = insert.add_attrib("ATT0", "dummy")
    # create a MTEXT entity:
    m_text = msp.add_mtext("test1\ntest2\ntest3")
    m_text.set_location((5, 5))
    # embed the MTEXT entity into the attribute:
    attrib.embed_mtext(m_text)

    doc.saveas(CWD / "insert_with_mtext_attribute.dxf")


if __name__ == "__main__":
    main()
