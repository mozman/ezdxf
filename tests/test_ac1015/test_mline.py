# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


def test_generic_mline(dwg):
    msp = dwg.modelspace()
    mline = msp.build_and_add_entity('MLINE', {})
    assert mline.dxftype() == 'MLINE'


def test_standard_mline_style(dwg):
    mline_style = dwg.mline_styles.get('STANDARD')
    assert mline_style.dxftype() == 'MLINESTYLE'

    elements = list(mline_style.get_elements())
    assert len(elements) == mline_style.dxf.n_elements
    assert elements[0]['offset'] == 0.5
    assert elements[0]['color'] == 256
    assert elements[0]['linetype'] == 'BYLAYER'
    assert elements[1]['offset'] == -0.5
    assert elements[1]['color'] == 256
    assert elements[1]['linetype'] == 'BYLAYER'

