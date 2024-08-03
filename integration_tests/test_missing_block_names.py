# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

from pathlib import Path
import ezdxf

DATA = Path(__file__).parent / "data"


def test_load_r12_blocks_with_no_name():
    """DXF R12 has no BLOCK_RECORD and therefore the block name cannot be recovered."""
    doc = ezdxf.readfile(DATA / "r12_blocks_with_no_names.dxf")
    assert len(doc.blocks) == 2


def test_load_r2000_blocks_with_recovered_names():
    """DXF R2000 requires a BLOCK_RECORD for each block definition and therefore the
    block name can be recovered from the BLOCK_RECORD.
    """
    doc = ezdxf.readfile(DATA / "r2000_blocks_with_no_names.dxf")
    assert len(doc.blocks) == 4
    for name in ("Test", "Test2"):
        block = doc.blocks.get(name)
        assert block.name == name
        assert block.block.dxf.name == name
        assert block.block_record.dxf.name == name


def test_load_r2000_blocks_with_no_name_and_no_block_record():
    """The block name cannot be recovered without an associated block record."""
    doc = ezdxf.readfile(DATA / "r2000_blocks_with_no_name_and_no_block_record.dxf")
    assert len(doc.blocks) == 2
    for name in ("Test", "Test2"):
        assert name not in doc.blocks
        assert name not in doc.block_records


if __name__ == "__main__":
    pytest.main([__file__])
