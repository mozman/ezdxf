#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

import ezdxf
from ezdxf.layouts import VirtualLayout
from ezdxf.math import BoundingBox2d
from ezdxf.tools.text_size import (
    text_size,
    mtext_size,
    WordSizeDetector,
    estimate_mtext_extents,
)

from ezdxf.tools.text_layout import leading


@pytest.fixture
def msp():
    yield VirtualLayout()


H3W1 = {"height": 3.0, "width": 1.0}
H2W2 = {"height": 2.0, "width": 2.0}


def test_text_size_of_an_empty_string(msp):
    """The text_size() function does not measure the actual height of a char,
    it always returns the font measurement cap-height for text height and
    cap-height + descender for the total text height.
    """
    text = msp.add_text("", dxfattribs=H3W1)
    size = text_size(text)
    assert size.width == 0.0
    assert size.cap_height == 3.0
    assert size.total_height > 3.3  # assuming the descender factor is > 0.1


def test_text_width_of_a_single_char(msp):
    """The "MonospaceFont" font has a char width of cap-height x width factor."""
    text = msp.add_text("X", dxfattribs=H3W1)
    size = text_size(text)
    assert size.width == 3.0, "char width should be equal to cap height"


@pytest.mark.parametrize("s", ["ABC", ".,!", "   "])
def test_text_width_of_a_string(msp, s):
    text = msp.add_text(s, dxfattribs=H3W1)
    size = text_size(text)
    assert size.width == len(s) * size.cap_height


@pytest.mark.parametrize("s", ["ABC", ".,!", "   "])
def test_text_width_of_a_string_for_width_factor_2(msp, s):
    text = msp.add_text(s, dxfattribs=H2W2)
    size = text_size(text)
    assert size.width == len(s) * size.cap_height * 2.0


@pytest.mark.parametrize(
    "s",
    [
        "ABC\n",  # remove line ending
        "ABC\r",  # remove line ending
        "AB^I",  # parse caret notation "^I" -> "\t" (tabulator)
        "AB%%d",  # parse special chars "%%d" -> "°"
    ],
)
def test_measurement_of_plain_text(msp, s):
    text = msp.add_text(s, dxfattribs=H3W1)
    size = text_size(text)
    assert size.width == 3.0 * size.cap_height


def test_support_for_text_size():
    test_string = "TestString"
    doc = ezdxf.new()
    doc.styles.add("OpenSans", font="OpenSans.ttf")
    text = doc.modelspace().add_text(
        test_string,
        dxfattribs={
            "style": "OpenSans",
            "height": 2.0,
        },
    )
    length = len(test_string)
    size = text_size(text)
    # Do not check exact measurements, "arial.ttf" is not available at all
    # platforms by default!
    assert length * 1.0 < size.width < length * 2.0
    assert 1.95 < size.cap_height < 2.05
    assert size.total_height > size.cap_height


def test_mtext_size_of_an_empty_string(msp):
    mtext = msp.add_mtext("", dxfattribs={"char_height": 1.0})
    size = mtext_size(mtext)
    assert size.total_width == 0.0
    assert size.total_height == 0.0
    assert size.column_width == 0.0
    assert size.gutter_width == 0.0
    assert size.column_count == 1
    assert size.column_heights == (0.0,)


def test_mtext_size_of_a_single_char(msp):
    # Matplotlib support disabled and using MonospaceFont()
    mtext = msp.add_mtext("X", dxfattribs={"char_height": 2.0})
    size = mtext_size(mtext)
    assert size.total_height == 2.0
    assert size.total_width == pytest.approx(1.8794373744139317)
    assert size.column_width == pytest.approx(1.8794373744139317)
    assert size.gutter_width == 0.0
    assert size.column_count == 1


def test_mtext_size_of_a_string(msp):
    # Matplotlib support disabled and using MonospaceFont()
    mtext = msp.add_mtext("XXX", dxfattribs={"char_height": 2.0})
    size = mtext_size(mtext)
    assert size.total_height == 2.0
    assert size.total_width == pytest.approx(5.6383121232417945)
    assert size.column_width == size.total_width
    assert size.gutter_width == 0.0
    assert size.column_count == 1


def test_estimate_mtext_extents(msp):
    # Matplotlib support disabled and using MonospaceFont()
    mtext = msp.add_mtext(
        "XXXXXXXXXXXX\nYYYY\nZ",  # 5 lines!
        dxfattribs={
            "char_height": 2.0,
            "width": 8.0,
        },
    )
    width, height = estimate_mtext_extents(mtext)
    assert height == pytest.approx(15.336)  # 5 lines!
    assert width == 8.0


@pytest.mark.parametrize(
    "cap_height, expected", [(2.0, 6.703281982585398), (3.0, 10.054922973878098)]
)
def test_mtext_size_of_2_lines(cap_height, expected, msp):
    # Matplotlib support disabled and using MonospaceFont()
    mtext = msp.add_mtext(
        "XXX\nYYYY",
        dxfattribs={
            "char_height": cap_height,
            "line_spacing_factor": 1.0,
        },
    )
    size = mtext_size(mtext)
    expected_total_height = leading(cap_height, line_spacing=1.0) + cap_height
    assert size.total_height == pytest.approx(expected_total_height)
    assert size.total_width == pytest.approx(expected), "expected width of 2nd line"
    assert size.column_width == size.total_width


if __name__ == "__main__":
    pytest.main([__file__])
