# Copyright (c) 2011-2020, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.entities.textstyle import Textstyle


@pytest.fixture
def style():
    return Textstyle.new(
        "FFFF",
        dxfattribs={
            "name": "TEST",
            "font": "NOFONT.ttf",
            "width": 2.0,
        },
    )


def test_name(style):
    assert "TEST" == style.dxf.name


def test_font(style):
    assert "NOFONT.ttf" == style.dxf.font


def test_width(style):
    assert 2.0 == style.dxf.width


def test_height(style):
    assert 0.0 == style.dxf.height


def test_oblique(style):
    assert 0.0 == style.dxf.oblique


def test_bigfont(style):
    assert "" == style.dxf.bigfont


def test_is_backward(style):
    assert style.is_backward is False


def test_set_backward(style):
    style.is_backward = True
    assert style.is_backward is True


def test_is_upside_down(style):
    assert style.is_upside_down is False


def test_set_is_upside_down(style):
    style.is_upside_down = True
    assert style.is_upside_down is True


def test_set_is_vertical_stacked(style):
    style.is_vertical_stacked = True
    assert style.is_vertical_stacked is True


def test_not_existing_extended_font_data(style):
    assert style.has_extended_font_data is False
    assert style.get_extended_font_data() == ("", False, False)


@pytest.fixture
def xstyle():
    style = Textstyle.new(
        "FFFF",
        dxfattribs={
            "name": "OpenSans-BoldItalic",
            "font": "OpenSans-BoldItalic.ttf",
        },
    )
    style.set_xdata("ACAD", [(1000, "Open Sans"), [1071, 50331682]])
    return style


def test_extended_font_data(xstyle):
    assert xstyle.has_extended_font_data is True
    assert xstyle.get_extended_font_data() == ("Open Sans", True, True)


def test_discard_extended_font_data(xstyle):
    xstyle.discard_extended_font_data()
    assert xstyle.has_extended_font_data is False


def test_set_extended_font_data(style):
    style.set_extended_font_data("Arial", italic=True, bold=True)
    assert style.get_extended_font_data() == ("Arial", True, True)


def test_dxf_details_for_extended_font_data(style):
    style.set_extended_font_data("Arial", italic=True, bold=True)
    xdata = style.get_xdata("ACAD")
    assert len(xdata) == 2

    group_code, family = xdata[0]
    assert group_code == 1000
    assert family == "Arial"

    group_code, flags = xdata[1]
    assert group_code == 1071
    assert flags == 50331682


MALFORMED_STYLE = """0
STYLE
5
FEFE
100
AcDbTextStyleTableRecord
2
STY_EZDXF
70
0
40
0.0
41
1.5
50
30.0
71
0
42
0.0
3
txt
4

100
AcDbSymbolTableRecord
"""


def test_malformed_layer():
    style = Textstyle.from_text(MALFORMED_STYLE)
    assert style.dxf.name == "STY_EZDXF"
    assert style.dxf.handle == "FEFE"
    assert style.dxf.width == 1.5
    assert style.dxf.oblique == 30.0
