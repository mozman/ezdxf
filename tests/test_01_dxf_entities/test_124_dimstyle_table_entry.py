# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.entities.dimstyle import DimStyle
from ezdxf.document import Drawing
from ezdxf.lldxf.const import DXF12


@pytest.fixture
def dimstyle():
    doc = Drawing.new()
    doc.blocks.new("left_arrow")
    doc.blocks.new("right_arrow")
    doc.blocks.new("arrow")
    doc.blocks.new("_DOT")
    doc.blocks.new("_OPEN")
    return DimStyle.new(
        "FFFF",
        doc=doc,
        dxfattribs={
            "name": "DIMSTYLE1",
        },
    )


def test_name(dimstyle):
    assert "DIMSTYLE1" == dimstyle.dxf.name


def test_set_blk1_and_blk2_arrows(dimstyle):
    dimstyle.set_arrows("", "left_arrow", "right_arrow")
    assert dimstyle.dxf.dimblk == ""
    assert dimstyle.dxf.dimblk1 == "left_arrow"
    assert dimstyle.dxf.dimblk2 == "right_arrow"


def test_set_both_arrows(dimstyle):
    dimstyle.set_arrows("arrow")
    assert dimstyle.dxf.dimblk == "arrow"
    assert dimstyle.dxf.dimblk1 == ""
    assert dimstyle.dxf.dimblk2 == ""

    dimstyle.set_arrows(blk1="OPEN", blk2="DOT")
    assert dimstyle.dxf.dimblk == ""
    assert dimstyle.dxf.dimblk1 == "OPEN"
    assert dimstyle.dxf.dimblk2 == "DOT"


def test_set_tick(dimstyle):
    dimstyle.set_tick(0.25)
    assert dimstyle.dxf.dimtsz == 0.25


def test_set_text_align(dimstyle):
    dimstyle.set_text_align(valign="above")
    assert dimstyle.dxf.dimtad == 1


def test_set_text_format(dimstyle):
    dimstyle.set_text_format(
        prefix="+",
        postfix=" cm",
        rnd=0.5,
        leading_zeros=False,
        trailing_zeros=False,
    )
    assert dimstyle.dxf.dimpost == "+<> cm"
    assert dimstyle.dxf.dimrnd == 0.5
    assert dimstyle.dxf.dimzin == 12


@pytest.fixture(scope="module")
def dimstyle2():
    import ezdxf

    doc = ezdxf.new("R2007", setup=("linetypes",))
    doc.blocks.new("left_arrow")
    doc.blocks.new("right_arrow")
    doc.blocks.new("TestArrow")
    doc.blocks.new("arrow")
    doc.styles.new("TestStyle")
    return doc.dimstyles.new("testing")


def test_handle_export(dimstyle2):
    dimstyle2.set_arrows("", "left_arrow", "right_arrow", "arrow")
    # test handles
    blocks = dimstyle2.doc.blocks
    left_arrow = blocks.get("left_arrow")
    right_arrow = blocks.get("right_arrow")
    leader_arrow = blocks.get("arrow")

    # prepare for export
    dimstyle2.set_handles()
    assert dimstyle2.dxf.hasattr("dimblk_handle") is False
    assert dimstyle2.dxf.dimblk1_handle == left_arrow.block_record_handle
    assert dimstyle2.dxf.dimblk2_handle == right_arrow.block_record_handle
    assert dimstyle2.dxf.dimldrblk_handle == leader_arrow.block_record_handle


def test_dont_write_handles_for_R12(dimstyle):
    from ezdxf.lldxf.tagwriter import TagWriter
    from io import StringIO

    s = StringIO()
    t = TagWriter(s)
    t.dxfversion = DXF12
    t.write_handles = False
    dimstyle.export_dxf(t)
    result = s.getvalue()
    assert "105\nFFFF\n" not in result


def test_dimstyle_name(dimstyle2):
    assert "testing" == dimstyle2.dxf.name


def test_dimstyle_blk1_and_blk2_ticks(dimstyle2):
    dimstyle2.set_arrows("", "left_arrow", "right_arrow")
    assert dimstyle2.get_dxf_attrib("dimblk") == ""
    assert dimstyle2.get_dxf_attrib("dimblk1") == "left_arrow"
    assert dimstyle2.get_dxf_attrib("dimblk2") == "right_arrow"


def test_dimstyle_both_ticks(dimstyle2):
    dimstyle2.set_arrows("arrow")
    assert dimstyle2.get_dxf_attrib("dimblk") == "arrow"
    assert dimstyle2.get_dxf_attrib("dimblk1") == ""  # closed filled
    assert dimstyle2.get_dxf_attrib("dimblk2") == ""  # closed filled

    assert dimstyle2.get_dxf_attrib("dimblk1") == ""
    assert dimstyle2.get_dxf_attrib("dimblk2") == ""


def test_dimstyle_virtual_dimtxsty_attribute(dimstyle2):
    dimstyle2.dxf.dimtxsty = "TestStyle"
    assert dimstyle2.dxf.dimtxsty == "TestStyle"

    # prepare for export
    dimstyle2.set_handles()
    assert (
        dimstyle2.dxf.dimtxsty_handle
        == dimstyle2.doc.styles.get("TestStyle").dxf.handle
    )


def test_dimstyle_virtual_dimldrblk_attribute(dimstyle2):
    dimstyle2.dxf.dimldrblk = "CLOSED"

    dimstyle2.dxf.dimldrblk = "TestArrow"
    assert dimstyle2.dxf.dimldrblk == "TestArrow"


def test_dimstyle_virtual_linetypes_attributes(dimstyle2):
    dimstyle2.dxf.dimltype = "DOT2"
    assert dimstyle2.dxf.dimltype == "DOT2"

    dimstyle2.dxf.dimltex1 = "DOT"
    assert dimstyle2.dxf.dimltex1 == "DOT"

    dimstyle2.dxf.dimltex2 = "DOTX2"
    assert dimstyle2.dxf.dimltex2 == "DOTX2"

    # prepare for export
    dimstyle2.set_handles()
    assert (
        dimstyle2.dxf.dimltype_handle
        == dimstyle2.doc.linetypes.get("DOT2").dxf.handle
    )
    assert (
        dimstyle2.dxf.dimltex1_handle
        == dimstyle2.doc.linetypes.get("DOT").dxf.handle
    )
    assert (
        dimstyle2.dxf.dimltex2_handle
        == dimstyle2.doc.linetypes.get("DOTX2").dxf.handle
    )


def test_dimstyle_group_codes(dimstyle):
    codes = DimStyle.CODE_TO_DXF_ATTRIB
    assert 105 not in codes
    assert 2 not in codes


def test_dimstyle_set_align(dimstyle2):
    dimstyle2.set_text_align(valign="above")
    assert dimstyle2.dxf.dimtad == 1
    dimstyle2.set_text_align(halign="above1")
    assert dimstyle2.dxf.dimjust == 3


def test_set_text_format_2(dimstyle2):
    dimstyle2.set_text_format(
        prefix="+",
        postfix=" cm",
        rnd=0.5,
        dec=2,
        sep=".",
        leading_zeros=False,
        trailing_zeros=False,
    )
    assert dimstyle2.dxf.dimpost == "+<> cm"
    assert dimstyle2.dxf.dimrnd == 0.5
    assert dimstyle2.dxf.dimdec == 2
    assert dimstyle2.dxf.dimdsep == ord(".")
    assert dimstyle2.dxf.dimzin == 12


def test_set_dimline_format(dimstyle2):
    dimstyle2.set_dimline_format(
        color=2,
        linetype="DOT",
        lineweight=18,
        extension=0.33,
        disable1=True,
        disable2=True,
    )
    assert dimstyle2.dxf.dimclrd == 2
    assert dimstyle2.dxf.dimltype == "DOT"
    assert dimstyle2.dxf.dimlwd == 18
    assert dimstyle2.dxf.dimdle == 0.33
    assert dimstyle2.dxf.dimsd1 == 1
    assert dimstyle2.dxf.dimsd2 == 1


def test_set_extline_format(dimstyle2):
    dimstyle2.set_extline_format(
        color=2,
        lineweight=18,
        extension=0.33,
        offset=0.77,
        fixed_length=0.5,
    )
    assert dimstyle2.dxf.dimclre == 2
    assert dimstyle2.dxf.dimlwe == 18
    assert dimstyle2.dxf.dimexe == 0.33
    assert dimstyle2.dxf.dimexo == 0.77
    assert dimstyle2.dxf.dimfxlon == 1
    assert dimstyle2.dxf.dimfxl == 0.5


def test_set_extline1(dimstyle2):
    dimstyle2.set_extline1(
        linetype="DOT",
        disable=True,
    )
    assert dimstyle2.dxf.dimltex1 == "DOT"
    assert dimstyle2.dxf.dimse1 == 1


def test_set_extline2(dimstyle2):
    dimstyle2.set_extline2(
        linetype="DOT",
        disable=True,
    )
    assert dimstyle2.dxf.dimltex2 == "DOT"
    assert dimstyle2.dxf.dimse2 == 1
