# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def msp():
    dwg = ezdxf.new('R2010')
    return dwg.modelspace()


def test_generic_acad_table(msp):
    table = msp.build_and_add_entity('ACAD_TABLE', {})
    assert table.dxftype() == 'ACAD_TABLE'
    assert table.dxf.version == 0
