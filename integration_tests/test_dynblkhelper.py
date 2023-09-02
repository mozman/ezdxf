#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import pathlib
import ezdxf
from ezdxf.entities import Insert
from ezdxf import dynblkhelper

BASEDIR = pathlib.Path(__file__)
DYN_BLOCKS = BASEDIR.parent / "data" / "dynblks.zip"


def test_direct_dynamic_block_references():
    doc = ezdxf.readzip(DYN_BLOCKS, "dynblk0.dxf")
    msp = doc.modelspace()

    references = msp.query("INSERT")
    assert len(references) == 4

    insert: Insert
    for insert in references:
        assert not insert.dxf.name.startswith("*"), "expected regular block reference"
        block = dynblkhelper.get_dynamic_block_definition(insert)
        assert block is not None
        assert block.name == insert.dxf.name


def test_indirect_dynamic_block_references():
    doc = ezdxf.readzip(DYN_BLOCKS, "dynblk1.dxf")
    msp = doc.modelspace()

    references = msp.query("INSERT")
    assert len(references) == 2

    insert: Insert
    for insert in references:
        assert insert.dxf.name.startswith("*"), "expected anonymous block reference"
        block = dynblkhelper.get_dynamic_block_definition(insert)
        assert block is not None
        assert block.name == "XYZ"


if __name__ == "__main__":
    pytest.main([__file__])
