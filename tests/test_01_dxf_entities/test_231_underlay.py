# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.underlay import PdfUnderlay, DwfUnderlay, DgnUnderlay
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

PDFUNDERLAY = """0
PDFUNDERLAY
5
0
330
0
100
AcDbEntity
8
0
100
AcDbUnderlayReference
340
0
10
0.0
20
0.0
30
0.0
41
1.0
42
1.0
43
1.0
50
0.0
280
2
281
100
282
0
"""


@pytest.fixture
def entity():
    return PdfUnderlay.from_text(PDFUNDERLAY)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'PDFUNDERLAY' in ENTITY_CLASSES


def test_default_init():
    entity = PdfUnderlay()
    assert entity.dxftype() == 'PDFUNDERLAY'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = PdfUnderlay.new(handle='ABBA', owner='0', dxfattribs={
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.insert == (0, 0, 0)
    assert entity.dxf.underlay_def_handle is None  # set by add_underlay()
    assert entity.dxf.scale_x == 1
    assert entity.dxf.scale_y == 1
    assert entity.dxf.scale_y == 1
    assert entity.dxf.rotation == 0
    assert entity.dxf.extrusion == (0, 0, 1)
    assert entity.dxf.flags == 2
    assert entity.dxf.contrast == 100
    assert entity.dxf.fade == 0
    assert entity.boundary_path == []


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.insert == (0, 0, 0)
    assert entity.dxf.underlay_def_handle == '0'
    assert entity.dxf.scale_x == 1
    assert entity.dxf.scale_y == 1
    assert entity.dxf.scale_y == 1
    assert entity.dxf.rotation == 0
    assert entity.dxf.extrusion == (0, 0, 1)
    assert entity.dxf.flags == 2
    assert entity.dxf.contrast == 100
    assert entity.dxf.fade == 0
    assert entity.boundary_path == []


def test_write_dxf():
    entity = PdfUnderlay.from_text(PDFUNDERLAY)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(PDFUNDERLAY)
    assert result == expected


def test_dwf_underlay():
    assert DwfUnderlay.DXFTYPE == 'DWFUNDERLAY'


def test_dgn_underlay():
    assert DgnUnderlay.DXFTYPE == 'DGNUNDERLAY'
