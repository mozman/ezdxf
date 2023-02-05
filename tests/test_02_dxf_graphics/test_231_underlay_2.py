# Copyright (c) 2016-2019, Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.entities.underlay import PdfDefinition, PdfUnderlay


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new("R2000")


@pytest.fixture
def pdf_def(doc):
    return PdfDefinition.from_text(PDF_DEFINITION, doc)


def test_pdf_def_properties(pdf_def):
    assert "PDFDEFINITION" == pdf_def.dxftype()
    assert "PDFUNDERLAY" == pdf_def.entity_name


def test_pdf_def_dxf_attribs(pdf_def):
    assert "underlay.pdf" == pdf_def.dxf.filename
    assert "underlay_key" == pdf_def.dxf.name


@pytest.fixture
def pdf(doc):
    return PdfUnderlay.from_text(PDF_UNDERLAY, doc)


def test_pdf_properties(pdf):
    assert "PDFUNDERLAY" == pdf.dxftype()


def test_pdf_dxf_attribs(pdf):
    assert pdf.dxf.insert == (0.0, 0.0, 0.0)
    assert pdf.dxf.scale_x == 2.5
    assert pdf.dxf.scale_y == 2.5
    assert pdf.dxf.scale_z == 2.5
    assert pdf.scaling == (2.5, 2.5, 2.5)
    assert pdf.dxf.flags == 2
    assert pdf.clipping == 0
    assert pdf.on == 1
    assert pdf.monochrome == 0
    assert pdf.adjust_for_background == 0
    assert pdf.dxf.contrast == 100
    assert pdf.dxf.fade == 0
    assert pdf.dxf.underlay_def_handle == "DEAD1"


def test_get_boundary_path(pdf):
    assert pdf.boundary_path == []


def test_reset_boundary_path(pdf):
    pdf.reset_boundary_path()
    assert pdf.boundary_path == []
    assert pdf.clipping is False


def test_set_boundary_path(pdf):
    pdf.set_boundary_path([(0, 0), (640, 180), (320, 360)])  # 3 vertices triangle
    assert pdf.clipping == 1
    assert pdf.boundary_path == [(0, 0), (640, 180), (320, 360)]


def test_set_scale(pdf):
    pdf.scaling = (1.2, 1.3, 1.4)
    assert pdf.scaling == (1.2, 1.3, 1.4)

    pdf.scaling = 1.7
    assert pdf.scaling == (1.7, 1.7, 1.7)


@pytest.fixture
def new_doc():
    # setting up a drawing is expensive - use as few test methods as possible
    return ezdxf.new("R2000")


def test_new_pdf_underlay_def(new_doc):
    rootdict = new_doc.rootdict
    assert "ACAD_PDFDEFINITIONS" not in rootdict
    underlay_def = new_doc.add_underlay_def("underlay.pdf", fmt="pdf", name="u1")

    # check internals pdf_def_owner -> ACAD_PDFDEFINITIONS
    pdf_dict = rootdict["ACAD_PDFDEFINITIONS"]
    assert underlay_def.dxf.owner == pdf_dict.dxf.handle

    assert "underlay.pdf" == underlay_def.dxf.filename
    assert "u1" == underlay_def.dxf.name


def test_new_pdf(new_doc):
    msp = new_doc.modelspace()
    underlay_def = new_doc.add_underlay_def("underlay.pdf")
    underlay = msp.add_underlay(underlay_def, insert=(0, 0, 0), scale=2)
    assert underlay.dxf.insert == (0, 0, 0)
    assert underlay.dxf.scale_x == 2
    assert underlay.dxf.scale_y == 2
    assert underlay.dxf.scale_z == 2
    assert underlay_def.dxf.handle == underlay.dxf.underlay_def_handle
    assert underlay.clipping is False
    assert underlay.on is True
    assert underlay.monochrome is False
    assert underlay.adjust_for_background is False
    assert underlay.dxf.flags == 2

    underlay_def2 = underlay.get_underlay_def()
    assert underlay_def.dxf.handle == underlay_def2.dxf.handle


class TestCopyAndTransformUnderlay:
    @pytest.fixture(scope="class")
    def doc(self):
        return ezdxf.new()

    @pytest.fixture(scope="class")
    def underlay_def(self, doc):
        return doc.add_underlay_def("underlay.pdf")

    @pytest.fixture(scope="class")
    def msp(self, doc):
        return doc.modelspace()

    def test_copied_underlay_has_same_underlay_definition(self, msp, underlay_def):
        underlay = msp.add_underlay(underlay_def, insert=(0, 0, 0), scale=2)
        clone = underlay.copy()
        msp.add_entity(clone)
        assert (
            underlay.get_underlay_def() is clone.get_underlay_def()
        ), "expected the same underlay definition"

    def test_underlay_definition_has_reactor_handles_to_copies(self, msp, underlay_def):
        underlay = msp.add_underlay(underlay_def, insert=(0, 0, 0), scale=2)
        clone = underlay.copy()
        msp.add_entity(clone)

        assert (
            underlay.dxf.handle in underlay_def.reactors
        ), "expected reactor handle of original underlay"
        assert (
            clone.dxf.handle in underlay_def.reactors
        ), "expected reactor handle of cloned underlay"

    def test_transform_underlay(self, msp, underlay_def):
        """The UNDERLAY entity uses the same low-level transform function as INSERT,
        no extensive transformation testing is required.
        """
        underlay = msp.add_underlay(underlay_def, insert=(0, 0, 0), scale=2)
        underlay.translate(1, 2, 3)

        assert underlay.dxf.insert == (1, 2, 3)


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
