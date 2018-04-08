# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def msp():
    dwg = ezdxf.new('R2007')
    return dwg.modelspace()


def test_generic_tolerance(msp):
    light = msp.build_and_add_entity('TOLERANCE', {})
    assert light.dxftype() == 'TOLERANCE'
    assert light.dxf.dimstyle == 'STANDARD'
