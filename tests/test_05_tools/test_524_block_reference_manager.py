#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

import ezdxf
from ezdxf.blkrefs import BlockReferenceCounter


def test_count_empty_document():
    doc = ezdxf.new()
    ref_counter = BlockReferenceCounter(doc)
    assert len(ref_counter) == 0


def test_non_exiting_handles_return_0():
    doc = ezdxf.new()
    ref_counter = BlockReferenceCounter(doc)
    assert ref_counter["xyz"] == 0, "not existing handles should return 0"
    assert (
        ref_counter.by_name("xyz") == 0
    ), "not existing block name should return 0"


def test_count_simple_references():
    count = 10
    doc = ezdxf.new()
    doc.blocks.new("First")
    msp = doc.modelspace()
    psp = doc.layout()
    for _ in range(count):
        msp.add_blockref("First", (0, 0))
        psp.add_blockref("First", (0, 0))
    ref_counter = BlockReferenceCounter(doc)
    assert len(ref_counter) == 1
    assert ref_counter.by_name("First") == 20


def test_count_nested_block_references():
    count = 10
    doc = ezdxf.new()
    block1 = doc.blocks.new("First")
    block2 = doc.blocks.new("Second")
    block1.add_blockref(block2.dxf.name, (0, 0))

    msp = doc.modelspace()
    for _ in range(count):
        msp.add_blockref("First", (0, 0))
    ref_counter = BlockReferenceCounter(doc)
    assert len(ref_counter) == 2
    assert ref_counter.by_name("First") == 10
    assert (
        ref_counter.by_name("Second") == 1
    ), "referenced only once in block First"


def test_count_references_used_in_xdata():
    doc = ezdxf.new()
    msp = doc.modelspace()
    block = doc.blocks.new("First")
    handle = block.block_record.dxf.handle
    line = msp.add_line((0, 0), (1, 0))

    # attach XDATA handle to block reference
    line.set_xdata("ezdxf", [(1005, handle)])
    ref_counter = BlockReferenceCounter(doc)
    assert ref_counter[handle] == 1


def test_count_references_used_in_app_data():
    doc = ezdxf.new()
    msp = doc.modelspace()
    block = doc.blocks.new("First")
    handle = block.block_record.dxf.handle
    line = msp.add_line((0, 0), (1, 0))

    # attach XDATA handle to block reference
    line.set_app_data("ezdxf", [(320, handle), (480, handle)])
    ref_counter = BlockReferenceCounter(doc)
    assert ref_counter[handle] == 2


def test_count_references_used_in_xrecord():
    doc = ezdxf.new()
    block = doc.blocks.new("First")
    handle = block.block_record.dxf.handle
    xrecord = doc.rootdict.add_xrecord("Test")
    xrecord.reset([(320, handle), (330, handle), (480, handle)])

    ref_counter = BlockReferenceCounter(doc)
    assert ref_counter[handle] == 3


def test_count_references_in_header_section():
    doc = ezdxf.new()
    doc.blocks.new("Arrow")
    for var_name in ("$DIMBLK", "$DIMBLK1", "$DIMBLK2", "$DIMLDRBLK"):
        doc.header[var_name] = "Arrow"

    ref_counter = BlockReferenceCounter(doc)
    assert ref_counter.by_name("Arrow") == 4


def test_count_references_in_dimstyle():
    doc = ezdxf.new()
    doc.blocks.new("Arrow")
    dimstyle = doc.dimstyles.new("Test")
    dimstyle.dxf.dimblk = "Arrow"
    dimstyle.dxf.dimblk1 = "Arrow"
    dimstyle.dxf.dimblk2 = "Arrow"
    dimstyle.dxf.dimldrblk = "Arrow"

    ref_counter = BlockReferenceCounter(doc)
    assert ref_counter.by_name("Arrow") == 4


if __name__ == "__main__":
    pytest.main([__file__])
