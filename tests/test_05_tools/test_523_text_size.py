#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

import ezdxf
from ezdxf.layouts import VirtualLayout
from ezdxf.tools.text_size import text_size, mtext_size


# Exact text size checks are not possible if the used font is not available,
# which cannot guaranteed for all platforms therefore the matplotlib support is
# disabled deliberately by using a virtal layout, which has not text style
# tables attached and the "MonospaceFont" based text measurements are used.


@pytest.fixture
def msp():
    state = ezdxf.options.use_matplotlib
    ezdxf.options.use_matplotlib = False
    yield VirtualLayout()
    ezdxf.options.use_matplotlib = state


H3W1 = {"height": 3.0, "width": 1.0}
H3W2 = {"height": 2.0, "width": 2.0}


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
    """The "MonospaceFont" font has a char width of cap-height x width factor.
    """
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
    text = msp.add_text(s, dxfattribs=H3W2)
    size = text_size(text)
    assert size.width == len(s) * size.cap_height * 2.0


@pytest.mark.parametrize("s", [
    "ABC\n",  # remove line ending
    "ABC\r",  # remove line ending
    "AB^I",  # parse caret notation "^I" -> "\t" (tabulator)
    "AB%%d",  # parse special chars "%%d" -> "°"
])
def test_measurement_of_plain_text(msp, s):
    text = msp.add_text(s, dxfattribs=H3W1)
    size = text_size(text)
    assert size.width == 3.0 * size.cap_height


def test_matplotlib_support_for_text_size():
    if not ezdxf.options.use_matplotlib:
        return
    test_string = "TestString"
    doc = ezdxf.new()
    doc.styles.add("ARIAL", font="arial.ttf")
    text = doc.modelspace().add_text(test_string, dxfattribs={
        "style": "ARIAL",
        "height": 2.0,
    })
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
    assert size.column_heights == (0.0, )


def test_mtext_size_of_a_single_char(msp):

    mtext = msp.add_mtext("X", dxfattribs={"char_height": 2.0})
    size = mtext_size(mtext)
    assert size.total_height == 2.0
    assert size.total_width == 2.0
    assert size.column_width == 2.0
    assert size.gutter_width == 0.0
    assert size.column_count == 1


def test_mtext_size_of_a_string(msp):
    ezdxf.options.use_matplotlib = False
    mtext = msp.add_mtext("XXX", dxfattribs={"char_height": 2.0})
    size = mtext_size(mtext)
    assert size.total_height == 2.0
    assert size.total_width == 6.0
    assert size.column_width == 6.0
    assert size.gutter_width == 0.0
    assert size.column_count == 1



if __name__ == "__main__":
    pytest.main([__file__])
