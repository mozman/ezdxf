# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new2('R2007')


# todo: real MLINE tests
def test_generic_mline(doc):
    msp = doc.modelspace()
    mline = msp.new_entity('MLINE', {})
    assert mline.dxftype() == 'MLINE'


# todo: real MLINESTYLE tests
def test_standard_mline_style(doc):
    mline_style = doc.mline_styles.get('Standard')
    assert mline_style.dxftype() == 'MLINESTYLE'

    elements = mline_style.elements
    assert len(elements) == 2
    assert elements[0].offset == 0.5
    assert elements[0].color == 256
    assert elements[0].linetype == 'BYLAYER'
    assert elements[1].offset == -0.5
    assert elements[1].color == 256
    assert elements[1].linetype == 'BYLAYER'

