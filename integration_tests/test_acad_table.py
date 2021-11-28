#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest

from pathlib import Path
import ezdxf
from ezdxf.protocols import query_virtual_entities

DATA = Path(__file__).parent / "data"
ACAD_TABLE_WITH_BLK_REF = "acad_table_with_blk_ref.dxf"


@pytest.fixture(scope="module")
def doc():
    return ezdxf.readfile(DATA / ACAD_TABLE_WITH_BLK_REF)


@pytest.fixture
def acad_table(doc):
    msp = doc.modelspace()
    return msp.query("ACAD_TABLE").first


def test_virtual_entities_from_block(acad_table):
    content = query_virtual_entities(acad_table)
    assert len(content) == 42
    # Provides real INSERT entities:
    assert sum(int(e.dxftype() == "INSERT") for e in content) == 1


def test_virtual_entities_from_proxy_graphic(acad_table):
    content = list(acad_table.proxy_graphic_content())
    assert len(content) == 45
    # Does not provide INSERT entities:
    assert sum(int(e.dxftype() == "INSERT") for e in content) == 0


if __name__ == '__main__':
    pytest.main([__file__])
