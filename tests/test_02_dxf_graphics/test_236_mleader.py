# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new('R2007')


# todo: real MLEADER tests
def test_generic_mleader(doc):
    msp = doc.modelspace()
    mleader = msp.new_entity('MLEADER', {})
    assert mleader.dxftype() == 'MLEADER'
    assert mleader.dxf.leader_style_handle == '0'


def test_synonym_multileader(doc):
    msp = doc.modelspace()
    mleader = msp.new_entity('MULTILEADER', {})
    assert mleader.dxftype() == 'MULTILEADER'
    assert mleader.dxf.leader_style_handle == '0'


# todo: real MLEADERSTYLE tests
def test_standard_mleader_style(doc):
    mleader_style = doc.mleader_styles.get('Standard')
    assert mleader_style.dxftype() == 'MLEADERSTYLE'
    assert mleader_style.dxf.content_type == 2
