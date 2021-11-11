#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

import ezdxf
from ezdxf.blkrefs import BlockReferenceCounter


def test_count_empty_document():
    doc = ezdxf.new()
    ref_counter = BlockReferenceCounter(doc)
    assert len(ref_counter) == 0
    assert ref_counter["xyz"] == 0, "not existing handle should return 0"


def test_non_exiting_handles_return_0():
    doc = ezdxf.new()
    ref_counter = BlockReferenceCounter(doc)
    assert ref_counter["xyz"] == 0, "not existing handles should return 0"


def test_count_simple_references():
    count = 10
    doc = ezdxf.new()
    block = doc.blocks.new("First")
    msp = doc.modelspace()
    for _ in range(count):
        msp.add_blockref("First", (0, 0))
    ref_counter = BlockReferenceCounter(doc)
    assert len(ref_counter) == 1
    assert ref_counter[block.block_record.dxf.handle] == 10


if __name__ == "__main__":
    pytest.main([__file__])
