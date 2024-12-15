# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def block_definition_with_multiline_attdef():
    doc = ezdxf.new(dxfversion="R2018")
    block = doc.blocks.new(name="MY_BLOCK")

    # Text, location and height not needed, because copied from MTEXT entity
    attdef = block.add_attdef("TAG1")
    # Define the multiline attribute as MTEXT entity
    mtext = block.add_mtext("Default Value", dxfattribs={"char_height": 0.25})
    mtext.set_location((0, 0))
    # Set ATTDEF content from MTEXT entity
    attdef.set_mtext(mtext)

    attdef = block.add_attdef("TAG2", (0, -1))
    # reuse existing MTEXT entity
    mtext.text = "Another Default"
    mtext.set_location((0, -1))
    # Set ATTDEF content from MTEXT entity and destroy the MTEXT entity
    attdef.embed_mtext(mtext)

    # Usage of add_auto_attribs() with multiline ATTDEFs:
    msp = doc.modelspace()
    insert = msp.add_blockref("MY_BLOCK", insert=(5, 5))
    attribs = {
        "TAG1": "TAG1-Line1\nTAG1-Line2",
        "TAG2": "TAG2-Line3\nTAG2-Line4",
    }
    insert.add_auto_attribs(attribs)
    doc.saveas(CWD / "block_with_multiline_attdef.dxf")


def attach_multiline_attrib_to_block_reference():
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


def main():
    attach_multiline_attrib_to_block_reference()
    block_definition_with_multiline_attdef()


if __name__ == "__main__":
    main()
