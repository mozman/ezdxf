#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import cast
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
    layout1 = doc.layout('Layout1')
    limmin = layout1.dxf.limmin
    limmax = layout1.dxf.limmax
    assert limmin == (0, 0)
    assert limmax == (420, 297)

    layout1.reset_paper_limits()
    assert limmin == (0, 0)
    assert limmax == (420, 297)


def test_reset_modelspace_extents(doc):
    extmin = (-100, -100, -100)
    extmax = (100, 100, 100)
    msp = doc.modelspace()
    msp.reset_extents(extmin, extmax)
    assert msp.dxf.extmin == extmin
    assert msp.dxf.extmax == extmax
    doc.update_extents()  # is automatically called by Drawing.write()
    assert doc.header["$EXTMIN"] == extmin
    assert doc.header["$EXTMAX"] == extmax

    # reset to default values:
    msp.reset_extents()
    assert msp.dxf.extmin == (1e20, 1e20, 1e20)
    assert msp.dxf.extmax == (-1e20, -1e20, -1e20)


def test_reset_modelspace_limits(doc):
    limmin = (-10, -10)
    limmax = (300, 50)
    msp = doc.modelspace()
    msp.reset_limits(limmin, limmax)
    assert msp.dxf.limmin == limmin
    assert msp.dxf.limmax == limmax
    doc.update_limits()  # is automatically called by Drawing.write()
    assert doc.header["$LIMMIN"] == limmin
    assert doc.header["$LIMMAX"] == limmax

    # reset to default values:
    msp.reset_limits()
    width = msp.dxf.paper_width
    height = msp.dxf.paper_height
    assert msp.dxf.limmin == (0, 0)
    assert msp.dxf.limmax == (width, height)


def test_default_active_msp_vport_config(doc):
    # A viewport configuration is always a list of one or more VPORT entities:
    vport_config = doc.viewports.get('*ACTIVE')
    assert len(vport_config) == 1
    vport = vport_config[0]

    assert vport.dxf.center == (344.2, 148.5)
    assert vport.dxf.height == 297


def test_default_active_layout1_viewport(doc):
    layout1 = doc.layout("Layout1")
    assert len(layout1.viewports()) == 0, "no default viewport expected"


def test_reset_layout1_active_viewport(doc):
    doc = ezdxf.new()
    layout1 = cast('Paperspace', doc.layout("Layout1"))
    layout1.reset_main_viewport()
    viewport = layout1.viewports()[0]
    assert viewport.dxf.center == (202.5, 128.5)
    paper_width = layout1.dxf.paper_width
    paper_height = layout1.dxf.paper_height
    assert viewport.dxf.width == paper_width * 1.1  # AutoCAD default factor
    assert viewport.dxf.height == paper_height * 1.1  # AutoCAD default factor


if __name__ == '__main__':
    pytest.main([__file__])
