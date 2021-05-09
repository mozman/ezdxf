#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.text import MTextEditor


def test_append_text():
    m = MTextEditor()
    m.append('TEXT')
    assert str(m) == "TEXT"


def test_iadd_text():
    m = MTextEditor()
    m += 'TEXT'
    assert str(m) == "TEXT"


def test_stacked_text_limits_style():
    m = MTextEditor().stack('1', '2')
    assert str(m) == r"\S1^ 2;"


def test_stacked_text_with_horizontal_divider_line():
    m = MTextEditor().stack('1', '2', "/")
    assert str(m) == r"\S1/2;"  # no space after "/" required


def test_stacked_text_with_slanted_divider_line():
    m = MTextEditor().stack('1', '2', "#")
    assert str(m) == r"\S1#2;"  # no space after "#" required


def test_invalid_divider_char_raises_value_error():
    m = MTextEditor()
    pytest.raises(ValueError, m.stack, "1", "2", "x")


def test_change_color_name():
    m = MTextEditor()
    m.color('red')
    assert str(m) == r"\C1;"
    m.clear()
    m.aci(0)
    assert str(m) == r"\C0;"


def test_change_aci_color():
    m = MTextEditor()
    m.aci(0).aci(256)
    assert str(m) == r"\C0;\C256;"


@pytest.mark.parametrize('aci', [-1, 257])
def test_aci_color_raises_value_error(aci):
    with pytest.raises(ValueError):
        MTextEditor().aci(aci)


def test_change_to_red_by_rgb():
    m = MTextEditor().rgb((255, 0, 0))
    assert str(m) == r"\c255;"


def test_change_to_green_by_rgb():
    m = MTextEditor().rgb((0, 255, 0))
    assert str(m) == r"\c65280;"


def test_change_to_blue_by_rgb():
    m = MTextEditor().rgb((0, 0, 255))
    assert str(m) == r"\c16711680;"


def test_change_font():
    m = MTextEditor()
    m.font('Arial', bold=False, italic=False)
    assert str(m) == r"\fArial|b0|i0|c0|p0;"


def test_scale_height_factor():
    assert str(MTextEditor().scale_height(2)) == r"\H2x;"
    assert str(MTextEditor().scale_height(1.6666)) == r"\H1.667x;"


def test_absolute_text_height():
    assert str(MTextEditor().height(2)) == r"\H2;"
    assert str(MTextEditor().height(1.6666)) == r"\H1.667;"


def test_change_width_factor():
    assert str(MTextEditor().width_factor(2)) == r"\W2;"
    assert str(MTextEditor().width_factor(1.6666)) == r"\W1.667;"


def test_change_char_tracking_factor():
    assert str(MTextEditor().char_tracking_factor(2)) == r"\T2;"
    assert str(MTextEditor().char_tracking_factor(1.6666)) == r"\T1.667;"


def test_change_oblique_angle():
    assert str(MTextEditor().oblique(0)) == r"\Q0;"  # vertical
    assert str(MTextEditor().oblique(15)) == r"\Q15;"


def test_fluent_interface():
    m = MTextEditor(
        "some text").color("red").stack('1', '2').append("end.")
    assert str(m) == r"some text\C1;\S1^ 2;end."


def test_grouping():
    m = MTextEditor("some text")
    group_content = str(MTextEditor().font("Arial").append("Font=Arial"))
    m.group(group_content)
    assert str(m) == r"some text{\fArial|b0|i0|c0|p0;Font=Arial}"


def test_underline_text():
    assert str(MTextEditor().underline("TEXT")) == r"\LTEXT\l"


def test_overline_text():
    assert str(MTextEditor().overline("TEXT")) == r"\OTEXT\o"


def test_strike_through_text():
    assert str(MTextEditor().strike_through("TEXT")) == r"\KTEXT\k"


def test_bullet_lists():
    result = MTextEditor().bullet_list(
        indent=4,  # left indentation of the list items
        bullets=["-", "+"],  # bullets - mark in front of the list item
        content=["first", "second"]  # list items
    )
    assert str(result) == r"{\pi-3,l4,xt4;-^Ifirst\P+^Isecond\P}"


if __name__ == '__main__':
    pytest.main([__file__])
