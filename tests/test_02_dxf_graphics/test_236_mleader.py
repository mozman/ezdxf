# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.layouts import VirtualLayout


@pytest.fixture
def msp():
    return VirtualLayout()


# todo: real MLEADER tests
def test_generic_mleader(msp):
    mleader = msp.new_entity('MLEADER', {})
    assert mleader.dxftype() == 'MLEADER'
    assert mleader.dxf.leader_style_handle == '0'


def test_synonym_multileader(msp):
    mleader = msp.new_entity('MULTILEADER', {})
    assert mleader.dxftype() == 'MULTILEADER'
    assert mleader.dxf.leader_style_handle == '0'


# todo: real MLEADERSTYLE tests
def test_standard_mleader_style():
    doc = ezdxf.new('R2007')
    mleader_style = doc.mleader_styles.get('Standard')
    assert mleader_style.dxftype() == 'MLEADERSTYLE'
    assert mleader_style.dxf.content_type == 2
