# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def msp():
    dwg = ezdxf.new('R2007')
    return dwg.modelspace()


def test_generic_helix(msp):
    helix = msp.build_and_add_entity('HELIX', {})
    assert helix.dxftype() == 'HELIX'
    assert helix.dxf.major_release_number == 29
    # spline data exists
    assert helix.AcDbSpline is not None
    assert helix.dxf.degree == 3
