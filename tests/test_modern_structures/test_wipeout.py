# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_generic_wipeout(dwg):
    msp = dwg.modelspace()
    wipeout = msp.build_and_add_entity('WIPEOUT', {})
    assert wipeout.dxftype() == 'WIPEOUT'
    assert wipeout.dxf.insert == (0, 0, 0)

    dwg.set_wipeout_variables(frame=1)
    wipeout_variables = dwg.rootdict.get_entity('ACAD_WIPEOUT_VARS')
    assert wipeout_variables.dxf.frame == 1
