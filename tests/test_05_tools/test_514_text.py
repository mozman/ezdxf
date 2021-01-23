#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.entities import Text
from ezdxf.tools.text import (
    FontMeasurements, MonospaceFont, TextLine, plain_text, caret_decode,
    escape_dxf_line_endings, replace_non_printable_characters, plain_mtext,
    split_mtext_string,
)
from ezdxf.math import Vec3
from ezdxf.lldxf import const


@pytest.fixture
def default():
    return FontMeasurements(
        baseline=1.3,
        cap_height=1.0,
        x_height=0.5,
        descender_height=0.25
    )


def test_total_heigth(default):
    assert default.total_height == 1.25


def test_scale(default):
    fm = default.scale(2)
    assert fm.baseline == 2.6, "expected scaled baseline"
    assert fm.total_height == 2.5, "expected scaled total height"


def test_shift(default):
    fm = default.shift(1.0)
    assert fm.baseline == 2.3
    assert fm.total_height == 1.25


def test_scale_from_baseline(default):
    fm = default.scale_from_baseline(desired_cap_height=2.0)
    assert fm.baseline == 1.3, "expected unchanged baseline value"
    assert fm.cap_height == 2.0
    assert fm.x_height == 1.0
    assert fm.descender_height == 0.50
    assert fm.total_height == 2.5


def test_cap_top(default):
    assert default.cap_top == 2.3


def test_x_top(default):
    assert default.x_top == 1.8


def test_bottom(default):
    assert default.bottom == 1.05


def test_monospace_font():
    font = MonospaceFont(2.5, 0.75)
    assert font.text_width("1234") == 7.5


class TestTextLine:
    @pytest.fixture
    def font(self):
        return MonospaceFont(2.5, descender_factor=0.333)

    @pytest.fixture
    def text_line(self, font):
        return TextLine("text", font)

    def test_text_width_and_height(self, text_line):
        assert text_line.width == 10
        assert text_line.height == 2.5 * 1.333  # 1 + descender factor

    def test_shrink_to_fit(self, text_line):
        text_line.stretch("FIT", Vec3(0, 0), Vec3(5, 0))  # 50% shrink
        assert text_line.width == 5.0, "should shrink width"
        # cap height * 1.333 = 3.3325
        assert text_line.height == 3.3325, "should not shrink height"

    def test_stretch_to_aligned(self, text_line):
        text_line.stretch("ALIGNED", Vec3(0, 0), Vec3(15, 0))  # 50% stretch
        assert text_line.width == 15.0, "should stretch width"
        # cap height * 1.333 * 1.5 = 4.99875
        assert text_line.height == 4.99875, "should stretch height"

    def test_baseline_vertices_left_aligned(self, text_line):
        assert text_line.baseline_vertices(Vec3(0, 0)) == [
            Vec3(0, 0), Vec3(10, 0)]

    def test_baseline_vertices_center_aligned(self, text_line):
        assert text_line.baseline_vertices(Vec3(0, 0), halign=const.CENTER) == [
            Vec3(-5, 0), Vec3(5, 0)]

    def test_baseline_vertices_right_aligned(self, text_line):
        assert text_line.baseline_vertices(Vec3(0, 0), halign=const.RIGHT) == [
            Vec3(-10, 0), Vec3(0, 0)]

    def test_corner_vertices_baseline_aligned(self, text_line):
        fm = text_line.font_measurements()
        top = fm.cap_height
        bottom = -fm.descender_height
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.BASELINE) == [
            Vec3(0, bottom), Vec3(10, bottom), Vec3(10, top), Vec3(0, top)]

    def test_corner_vertices_top_aligned(self, text_line):
        bottom = -text_line.height
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.TOP) == [
            Vec3(0, bottom), Vec3(10, bottom), Vec3(10, 0), Vec3(0, 0)]

    def test_corner_vertices_bottom_aligned(self, text_line):
        top = text_line.height
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.BOTTOM) == [
            Vec3(0, 0), Vec3(10, 0), Vec3(10, top), Vec3(0, top)]

    def test_corner_vertices_middle_aligned(self, text_line):
        fm = text_line.font_measurements()
        top = fm.cap_height / 2
        bottom = -(fm.descender_height + top)
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.MIDDLE) == [
            Vec3(0, bottom), Vec3(10, bottom), Vec3(10, top), Vec3(0, top)
        ]


def test_plain_text():
    assert plain_text('%%d') == '°'
    # underline
    assert plain_text('%%u') == ''
    assert plain_text('%%utext%%u') == 'text'
    # single %
    assert plain_text('%u%d%') == '%u%d%'
    t = Text.new(dxfattribs={'text': '45%%d'})
    assert t.plain_text() == '45°'

    assert plain_text('abc^a') == 'abc!'
    assert plain_text('abc^Jdef') == 'abcdef'
    assert plain_text('abc^@def') == 'abc\0def'


def test_caret_decode():
    assert caret_decode('') == ''
    assert caret_decode('^') == '^'  # no match
    assert caret_decode('^ ') == '^'
    assert caret_decode('abc') == 'abc'
    assert caret_decode('ab\\Pc') == 'ab\\Pc'
    assert caret_decode('1^J\\P2') == '1\n\\P2'
    assert caret_decode('1^J2') == '1\n2'
    assert caret_decode('1^M2') == '1\r2'
    assert caret_decode('1^M^J2') == '1\r\n2'
    assert caret_decode('1^J^M2') == '1\n\r2'
    assert caret_decode('abc^ def') == 'abc^def'
    assert caret_decode('abc^Idef') == 'abc\tdef'
    assert caret_decode('abc^adef') == 'abc!def'
    assert caret_decode('abc^ddef') == 'abc$def'
    assert caret_decode('abc^zdef') == 'abc:def'
    assert caret_decode('abc^@def') == 'abc\0def'
    assert caret_decode('abc^^def') == 'abc\x1edef'


def test_dxf_escape_line_endings():
    assert escape_dxf_line_endings('\\P test') == '\\P test'
    assert escape_dxf_line_endings('abc\ndef') == 'abc\\Pdef'
    assert escape_dxf_line_endings('abc\rdef') == 'abcdef', \
        r"a single '\r' should be ignored"
    assert escape_dxf_line_endings('abc\r\ndef') == 'abc\\Pdef', \
        r"'\r\n' represents a single newline"


def test_replace_non_printable():
    assert replace_non_printable_characters('abc') == 'abc'
    assert replace_non_printable_characters('abc def') == 'abc def'
    assert replace_non_printable_characters('abc \tdef') == 'abc \tdef'
    assert replace_non_printable_characters('abc\0def') == 'abc▯def'
    assert replace_non_printable_characters(
        'abc\0def', replacement=' ') == 'abc def'


def test_plain_text_removes_formatting():
    raw_text = r"\A1;Das ist eine MText\PZeile mit {\LFormat}ierung\Pänder " \
               r"die Farbe\P\pi-7.5,l7.5,t7.5;1.^INummerierung\P2.^INummeri" \
               r"erung\P\pi0,l0,tz;\P{\H0.7x;\S1/2500;}  ein Bruch"
    expected = "Das ist eine MText\nZeile mit Formatierung\nänder die Farbe\n" \
               "1.^INummerierung\n2.^INummerierung\n\n1/2500  ein Bruch"
    assert plain_mtext(raw_text) == expected
    assert plain_mtext('\\:') == '\\:', \
        "invalid escape code is printed verbatim"


def test_plain_text_convert_special_chars():
    assert plain_mtext("%%d") == "°"
    assert plain_mtext("%%u") == ""
    assert plain_mtext("%%U") == ""


class TestSplitMText:
    MTEXT_SHORT_STR = "0123456789"

    def test_do_not_split_at_caret(self):
        # do not split at '^'
        chunks = split_mtext_string('a' * 19 + '^Ixxx^', 20)
        assert len(chunks) == 2
        assert chunks[0] == 'a' * 19
        assert chunks[1] == '^Ixxx^'

    def test_split_empty_string(self):
        chunks = split_mtext_string('', 20)
        assert len(chunks) == 0

    def test_split_short_string(self):
        chunks = split_mtext_string(self.MTEXT_SHORT_STR, 20)
        assert len(chunks) == 1
        assert self.MTEXT_SHORT_STR == chunks[0]

    def test_split_long_string(self):
        chunks = split_mtext_string(self.MTEXT_SHORT_STR * 3, 20)
        assert len(chunks) == 2
        assert self.MTEXT_SHORT_STR * 2 == chunks[0]
        assert self.MTEXT_SHORT_STR == chunks[1]

    def test_split_longer_string(self):
        chunks = split_mtext_string(self.MTEXT_SHORT_STR * 4, 20)
        assert len(chunks) == 2
        assert chunks[0] == self.MTEXT_SHORT_STR * 2
        assert chunks[1] == self.MTEXT_SHORT_STR * 2


if __name__ == '__main__':
    pytest.main([__file__])
