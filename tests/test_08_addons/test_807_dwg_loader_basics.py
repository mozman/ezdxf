# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import os
import pytest
from pathlib import Path
from ezdxf.addons.dwg import Document

file = Path(__file__)

FILE1 = file.parent / '807_1.dwg'


pytestmark = pytest.mark.skipif(not FILE1.exists(), reason=f"Data file '{FILE1}' not present.")


@pytest.fixture(scope='module')
def dwg1() -> bytes:
    return FILE1.read_bytes()


def test_load_classes(dwg1):
    doc = Document(dwg1)
    doc.load()
    assert len(doc.dxf_object_types) == 15
    assert doc.dxf_object_types[500] == 'ACDBDICTIONARYWDFLT'
    assert doc.dxf_object_types[514] == 'LAYOUT'


if __name__ == '__main__':
    pytest.main([__file__])
