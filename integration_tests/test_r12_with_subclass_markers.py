#  Copyright (c) 2020-2024, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import pytest
import ezdxf
from ezdxf import recover

DATADIR = Path(__file__).parent / "data"


def test_read_sublass_markers_in_r12_entities():
    """DXF R12 file with subclass markers (100, ...) in DXF entities."""
    doc = ezdxf.readfile(DATADIR / "Leica_Disto_S910.dxf")
    msp = doc.modelspace()
    points = list(msp.query("POINT"))
    assert len(points) == 11
    assert len(points[0].dxf.location) == 3


def test_read_sublass_markers_in_r12_table_entries():
    """DXF R12 file with subclass markers (100, ...) in table entries."""
    doc, _ = recover.readfile(DATADIR / "issue1106.dxf")
    msp = doc.modelspace()
    assert len(msp) == 10


if __name__ == "__main__":
    pytest.main([__file__])
