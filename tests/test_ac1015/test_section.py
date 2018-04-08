# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def msp():
    dwg = ezdxf.new('R2007')
    return dwg.modelspace()


def test_generic_section(msp):
    section = msp.build_and_add_entity('SECTION', {})
    assert section.dxftype() == 'SECTION'
    assert section.dxf.name == 'NAME'
