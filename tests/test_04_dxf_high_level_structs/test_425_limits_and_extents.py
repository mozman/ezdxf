#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf


@pytest.fixture(scope='module', params=['R12', 'R2000'])
def doc(request):
    return ezdxf.new(request.param)


def test_new_doc_extents(doc):
    extmin = doc.header["$EXTMIN"]
    extmax = doc.header["$EXTMAX"]
    assert extmin == (1e20, 1e20, 1e20)
    assert extmax == (-1e20, -1e20, -1e20)


def test_new_doc_limits(doc):
    limmin = doc.header["$LIMMIN"]
    limmax = doc.header["$LIMMAX"]
    assert limmin == (0, 0)
    assert limmax == (420, 297)


def test_default_modelspace_extents(doc):
    msp = doc.modelspace()
    extmin = msp.dxf.extmin
    extmax = msp.dxf.extmax
    assert extmin == (1e20, 1e20, 1e20)
    assert extmax == (-1e20, -1e20, -1e20)


def test_default_modelspace_limits(doc):
    msp = doc.modelspace()
    limmin = msp.dxf.limmin
    limmax = msp.dxf.limmax
    assert limmin == (0, 0)
    assert limmax == (420, 297)


def test_default_layout1_extents(doc):
    layout1 = doc.layout('Layout1')
    extmin = layout1.dxf.extmin
    extmax = layout1.dxf.extmax
    assert extmin == (1e20, 1e20, 1e20)
    assert extmax == (-1e20, -1e20, -1e20)


def test_default_layout1_limits(doc):
    layout1 = doc.modelspace()
    limmin = layout1.dxf.limmin
    limmax = layout1.dxf.limmax
    assert limmin == (0, 0)
    assert limmax == (420, 297)


if __name__ == '__main__':
    pytest.main([__file__])
