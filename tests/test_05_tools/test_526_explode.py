#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf import explode


@pytest.fixture(scope="module")
def doc():
    doc_ = ezdxf.new()
    block = doc_.blocks.new("BLK1")
    block.add_line((0, 0), (1, 0))
    return doc_


def test_virtual_entities_from_insert(doc):
    msp = doc.modelspace()
    insert = msp.add_blockref("BLK1", (0, 0))
    result = list(explode.virtual_block_reference_entities(insert))
    assert len(result) == 1


def test_transparency_of_virtual_entities_from_insert(doc):
    msp = doc.modelspace()
    insert = msp.add_blockref("BLK1", (0, 0))
    line = list(explode.virtual_block_reference_entities(insert))[0]
    assert line.transparency == 0.0
    assert line.dxf.hasattr("transparency") is False


if __name__ == '__main__':
    pytest.main([__file__])
