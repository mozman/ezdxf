# Created: 13.03.2016, 2018 rewritten for pytest
# Copyright (C) 2016-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

import ezdxf
from ezdxf.modern.underlay import PdfDefinition, PdfUnderlay
from ezdxf.lldxf.extendedtags import ExtendedTags


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('AC1015')


@pytest.fixture
def pdf_def(dwg):
    tags = ExtendedTags.from_text(PDF_DEFINITION)
    return PdfDefinition(tags, dwg)


def test_imagedef_properties(pdf_def):
    assert 'PDFDEFINITION' == pdf_def.dxftype()
    assert 'PDFUNDERLAY' == pdf_def.entity_name


def test_imagedef_dxf_attribs(pdf_def):
    assert 'underlay.pdf' == pdf_def.dxf.filename
    assert 'underlay_key' == pdf_def.dxf.name


@pytest.fixture
def pdf(dwg):
    tags = ExtendedTags.from_text(PDF_UNDERLAY)
    return PdfUnderlay(tags, dwg)


def test_image_properties(pdf):
    assert 'PDFUNDERLAY' == pdf.dxftype()


def test_image_dxf_attribs(pdf):
    assert (0., 0., 0.) == pdf.dxf.insert
    assert 2.5 == pdf.dxf.scale_x
    assert 2.5 == pdf.dxf.scale_y
    assert 2.5 == pdf.dxf.scale_z
    assert (2.5, 2.5, 2.5) == pdf.scale
    assert 2 == pdf.dxf.flags
    assert pdf.clipping == 0
    assert pdf.on == 1
    assert pdf.monochrome == 0
    assert pdf.adjust_for_background == 0
    assert 100 == pdf.dxf.contrast
    assert 0 == pdf.dxf.fade
    assert 'DEAD1' == pdf.dxf.underlay_def


def test_get_boundary_path(pdf):
    assert [] == pdf.get_boundary_path()


def test_reset_boundary_path(pdf):
    pdf.reset_boundary_path()
    assert [] == pdf.get_boundary_path()
    assert pdf.clipping == False


def test_set_boundary_path(pdf):
    pdf.set_boundary_path([(0, 0), (640, 180), (320, 360)])  # 3 vertices triangle
    assert pdf.clipping == 1
    assert [(0, 0), (640, 180), (320, 360)] == pdf.get_boundary_path()


def test_set_scale(pdf):
    pdf.scale = (1.2, 1.3, 1.4)
    assert (1.2, 1.3, 1.4) == pdf.scale

    pdf.scale = 1.7
    assert (1.7, 1.7, 1.7) == pdf.scale


@pytest.fixture
def new_dwg():
    # setting up a drawing is expensive - use as few test methods as possible
    return ezdxf.new('R2000')


def test_new_pdf_underlay_def(new_dwg):
    rootdict = new_dwg.rootdict
    assert 'ACAD_PDFDEFINITIONS' not in rootdict
    underlay_def = new_dwg.add_underlay_def('underlay.pdf', format='pdf', name='u1')

    # check internals pdf_def_owner -> ACAD_PDFDEFINITIONS
    pdf_dict_handle = rootdict['ACAD_PDFDEFINITIONS']
    pdf_dict = new_dwg.get_dxf_entity(pdf_dict_handle)
    assert underlay_def.dxf.owner == pdf_dict.dxf.handle

    assert 'underlay.pdf' == underlay_def.dxf.filename
    assert 'u1' == underlay_def.dxf.name


def test_new_image(new_dwg):
    msp = new_dwg.modelspace()
    underlay_def = new_dwg.add_underlay_def('underlay.pdf')
    underlay = msp.add_underlay(underlay_def, insert=(0, 0, 0), scale=2)
    assert (0, 0, 0) == underlay.dxf.insert
    assert 2 == underlay.dxf.scale_x
    assert 2 == underlay.dxf.scale_y
    assert 2 == underlay.dxf.scale_z
    assert underlay_def.dxf.handle == underlay.dxf.underlay_def
    assert underlay.clipping == 0
    assert underlay.on == 1
    assert underlay.monochrome == 0
    assert underlay.adjust_for_background == 0
    assert 2 == underlay.dxf.flags

    underlay_def2 = underlay.get_underlay_def()
    assert underlay_def.dxf.handle == underlay_def2.dxf.handle


PDF_DEFINITION = """  0
PDFDEFINITION
  5
DEAD1
330
DEAD2
100
AcDbUnderlayDefinition
  1
underlay.pdf
  2
underlay_key
"""

PDF_UNDERLAY = """  0
PDFUNDERLAY
  5
DEAD3
330
DEAD4
100
AcDbEntity
  8
0
100
AcDbUnderlayReference
340
DEAD1
 10
0.0
 20
0.0
 30
0.0
 41
2.5
 42
2.5
 43
2.5
280
  2
281
   100
282
     0
"""