#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import math
import ezdxf
from ezdxf.entities import Text, DXFEntity
from ezdxf.tools.text import (
    TextLine,
    plain_text,
    caret_decode,
    escape_dxf_line_endings,
    replace_non_printable_characters,
    split_mtext_string,
    text_wrap,
    is_text_vertical_stacked,
    fast_plain_mtext,
    plain_mtext,
    has_inline_formatting_codes,
    is_upside_down_text_angle,
    upright_text_angle,
    estimate_mtext_content_extents,
)
from ezdxf.tools.fonts import MonospaceFont
from ezdxf.math import Vec3
from ezdxf.lldxf import const


@pytest.fixture
def font():
    return MonospaceFont(2.5, descender_factor=0.333)


@pytest.fixture
def text_line(font):
    return TextLine("text", font)


class TestTextLine:
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
            Vec3(0, 0),
            Vec3(10, 0),
        ]

    def test_baseline_vertices_center_aligned(self, text_line):
        assert text_line.baseline_vertices(Vec3(0, 0), halign=const.CENTER) == [
            Vec3(-5, 0),
            Vec3(5, 0),
        ]

    def test_baseline_vertices_right_aligned(self, text_line):
        assert text_line.baseline_vertices(Vec3(0, 0), halign=const.RIGHT) == [
            Vec3(-10, 0),
            Vec3(0, 0),
        ]

    def test_corner_vertices_baseline_aligned(self, text_line):
        fm = text_line.font_measurements()
        top = fm.cap_height
        bottom = -fm.descender_height
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.BASELINE) == [
            Vec3(0, bottom),
            Vec3(10, bottom),
            Vec3(10, top),
            Vec3(0, top),
        ]

    def test_corner_vertices_top_aligned(self, text_line):
        bottom = -text_line.height
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.TOP) == [
            Vec3(0, bottom),
            Vec3(10, bottom),
            Vec3(10, 0),
            Vec3(0, 0),
        ]

    def test_corner_vertices_bottom_aligned(self, text_line):
        top = text_line.height
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.BOTTOM) == [
            Vec3(0, 0),
            Vec3(10, 0),
            Vec3(10, top),
            Vec3(0, top),
        ]

    def test_corner_vertices_middle_aligned(self, text_line):
        fm = text_line.font_measurements()
        top = fm.cap_height / 2
        bottom = -(fm.descender_height + top)
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.MIDDLE) == [
            Vec3(0, bottom),
            Vec3(10, bottom),
            Vec3(10, top),
            Vec3(0, top),
        ]


class TestTextLineTransformation:
    def test_empty_input(self, text_line):
        assert text_line.transform_2d([]) == []

    @pytest.mark.parametrize(
        "location", [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]
    )
    def test_translation(self, text_line, location):
        v = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        vertices = text_line.transform_2d(vertices=v, insert=location)
        for index in range(len(v)):
            assert vertices[index] == Vec3(location) + v[index]

    @pytest.mark.parametrize(
        "angle", [0, math.pi / 2, math.pi / 4, -math.pi / 2, -math.pi / 4]
    )
    def test_rotate(self, text_line, angle):
        vertices = text_line.transform_2d(
            vertices=[
                (1, 0),
                (2, 0),
            ],
            rotation=angle,
        )
        assert vertices[0] == (math.cos(angle), math.sin(angle))
        assert vertices[1] == (math.cos(angle) * 2, math.sin(angle) * 2)

    @pytest.mark.parametrize(
        "x,scale,expected",
        [
            (0, 2, 0),
            (1, 2, 2),
            (2, 2, 4),
            (2, -1, -2),
            (2, -2, -4),
        ],
    )
    def test_scale_x(self, text_line, x, scale, expected):
        vertices = text_line.transform_2d(
            vertices=[
                Vec3(x, 0),  # at the base line
                Vec3(x, 1),  # at height 1
                Vec3(x, -1),  # at height -1
            ],
            scale=(scale, 1),
        )
        assert vertices[0] == (expected, 0)
        assert vertices[1] == (expected, 1)
        assert vertices[2] == (expected, -1)

    @pytest.mark.parametrize(
        "y,scale,expected",
        [
            (0, 2, 0),
            (1, 2, 2),
            (2, 2, 4),
            (2, -1, -2),
            (2, -2, -4),
        ],
    )
    def test_scale_y(self, text_line, y, scale, expected):
        vertices = text_line.transform_2d(
            vertices=[
                Vec3(0, y),  # at the center
                Vec3(1, y),  # at width 1
                Vec3(-1, y),  # at width -1
            ],
            scale=(1, scale),
        )
        assert vertices[0] == (0, expected)
        assert vertices[1] == (1, expected)
        assert vertices[2] == (-1, expected)

    def test_oblique(self, text_line):
        oblique = math.pi / 4  # 45 deg
        vertices = text_line.transform_2d(
            vertices=[
                Vec3(0, 0),  # at the base line
                Vec3(0, 1),  # at height 1
                Vec3(0, -1),  # at height -1
                Vec3(10, 1),  # away from origin
            ],
            oblique=oblique,
        )
        assert vertices[0].isclose((0, 0))
        assert vertices[1].isclose((1, 1))
        assert vertices[2].isclose((-1, -1))
        assert vertices[3].isclose((11, 1))


def test_plain_text():
    assert plain_text("%%C") == "Ø"  # alt-0216
    assert plain_text("%%D") == "°"  # alt-0176
    assert plain_text("%%P") == "±"  # alt-0177
    # underline
    assert plain_text("%%u") == ""
    assert plain_text("%%utext%%u") == "text"
    # overline
    assert plain_text("%%o") == ""
    # strike through
    assert plain_text("%%k") == ""

    # single %
    assert plain_text("%u%d%") == "%u%d%"
    t = Text.new(dxfattribs={"text": "45%%d"})
    assert t.plain_text() == "45°"

    assert plain_text("abc^a") == "abc!"
    assert plain_text("abc^Jdef") == "abcdef"
    assert plain_text("abc^@def") == "abc\0def"


def test_caret_decode():
    assert caret_decode("") == ""
    assert caret_decode("^") == "^"  # no match
    assert caret_decode("^ ") == "^"
    assert caret_decode("abc") == "abc"
    assert caret_decode("ab\\Pc") == "ab\\Pc"
    assert caret_decode("1^J\\P2") == "1\n\\P2"
    assert caret_decode("1^J2") == "1\n2"
    assert caret_decode("1^M2") == "1\r2"
    assert caret_decode("1^M^J2") == "1\r\n2"
    assert caret_decode("1^J^M2") == "1\n\r2"
    assert caret_decode("abc^ def") == "abc^def"
    assert caret_decode("abc^Idef") == "abc\tdef"
    assert caret_decode("abc^adef") == "abc!def"
    assert caret_decode("abc^ddef") == "abc$def"
    assert caret_decode("abc^zdef") == "abc:def"
    assert caret_decode("abc^@def") == "abc\0def"
    assert caret_decode("abc^^def") == "abc\x1edef"


def test_dxf_escape_line_endings():
    assert escape_dxf_line_endings("\\P test") == "\\P test"
    assert escape_dxf_line_endings("abc\ndef") == "abc\\Pdef"
    assert (
        escape_dxf_line_endings("abc\rdef") == "abcdef"
    ), r"a single '\r' should be ignored"
    assert (
        escape_dxf_line_endings("abc\r\ndef") == "abc\\Pdef"
    ), r"'\r\n' represents a single newline"


def test_replace_non_printable():
    assert replace_non_printable_characters("abc") == "abc"
    assert replace_non_printable_characters("abc def") == "abc def"
    assert replace_non_printable_characters("abc \tdef") == "abc \tdef"
    assert replace_non_printable_characters("abc\0def") == "abc▯def"
    assert (
        replace_non_printable_characters("abc\0def", replacement=" ")
        == "abc def"
    )


def test_plain_mtext_removes_formatting():
    raw_text = (
        r"\A1;Das ist eine MText\PZeile mit {\LFormat}ierung\Pänder "
        r"die Farbe\P\pi-7.5,l7.5,t7.5;1.^INummerierung\P2.^INummeri"
        r"erung\P\pi0,l0,tz;\P{\H0.7x;\S1/2500;}  ein Bruch"
    )
    expected = (
        "Das ist eine MText\nZeile mit Formatierung\nänder die Farbe\n"
        "1.^INummerierung\n2.^INummerierung\n\n1/2500  ein Bruch"
    )
    assert fast_plain_mtext(raw_text) == expected
    assert (
        fast_plain_mtext("\\:") == "\\:"
    ), "invalid escape code is printed verbatim"


def test_plain_mtext2_removes_formatting():
    raw_text = (
        r"\A1;Das ist eine MText\PZeile mit {\LFormat}ierung\Pänder "
        r"die Farbe\P\pi-7.5,l7.5,t7.5;1.^INummerierung\P2.^INummeri"
        r"erung\P\pi0,l0,tz;\P{\H0.7x;\S1/2500;}  ein Bruch"
    )
    expected = (
        "Das ist eine MText\nZeile mit Formatierung\nänder die Farbe\n"
        "1. Nummerierung\n2. Nummerierung\n\n1/2500  ein Bruch"
    )
    assert plain_mtext(raw_text, tabsize=1) == expected
    assert (
        plain_mtext("\\:\\;") == "\\:\\;"
    ), "invalid escape code is printed verbatim"


def test_remove_commands_without_terminating_semicolon():
    # single letter commands do not need a trailing semicolon:
    assert plain_mtext(r"\C1Text") == "Text"
    assert fast_plain_mtext(r"\C1Text") == r"\C1Text"  # not the expected result


@pytest.mark.parametrize("func", [fast_plain_mtext, plain_mtext])
def test_plain_mtext_decoding_special_chars(func):
    assert func("%%C") == "Ø"  # alt-0216
    assert func("%%D") == "°"  # alt-0176
    assert func("%%P") == "±"  # alt-0177
    # formatting codes of TEXT are not supported in MTEXT
    # and unknown codes are rendered as they are:
    s = "%%a%%u_%%U_%%k_%%K_%%o_%%O_%%z"
    assert func(s) == s


class TestSplitMText:
    MTEXT_SHORT_STR = "0123456789"

    def test_do_not_split_at_caret(self):
        # do not split at '^'
        chunks = split_mtext_string("a" * 19 + "^Ixxx^", 20)
        assert len(chunks) == 2
        assert chunks[0] == "a" * 19
        assert chunks[1] == "^Ixxx^"

    def test_split_empty_string(self):
        chunks = split_mtext_string("", 20)
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


def test_text_wrapping():
    def get_text_width(s: str) -> float:
        return len(s)

    assert text_wrap("", 0, get_text_width) == []
    assert text_wrap("   \n    ", 1, get_text_width) == []

    assert text_wrap("abc", 0, get_text_width) == ["abc"]
    assert text_wrap(" abc", 6, get_text_width) == [
        " abc"
    ], "preserve leading spaces"
    assert text_wrap("abc ", 1, get_text_width) == [
        "abc"
    ], "do not wrap too long words"
    assert text_wrap(" abc ", 6, get_text_width) == [
        " abc"
    ], "remove trailing spaces"

    assert text_wrap("abc\ndef", 1, get_text_width) == [
        "abc",
        "def",
    ], "do not wrap too long words"
    assert text_wrap("   abc\ndef", 1, get_text_width) == [
        "",
        "abc",
        "def",
    ], "leading spaces can cause wrapping"
    assert text_wrap("   abc\ndef", 6, get_text_width) == ["   abc", "def"]
    assert text_wrap("abc    \n    def", 1, get_text_width) == ["abc", "def"]

    assert text_wrap(" a ", 1, get_text_width) == ["", "a"]
    assert text_wrap("\na ", 2, get_text_width) == ["", "a"]
    assert text_wrap(" \na ", 1, get_text_width) == ["", "a"]
    assert text_wrap(" \n \n ", 1, get_text_width) == []
    assert text_wrap(" \n \n a", 1, get_text_width) == ["", "", "a"]

    assert text_wrap("  abc", 6, get_text_width) == ["  abc"]
    assert text_wrap("  abc def", 6, get_text_width) == ["  abc", "def"]
    assert text_wrap("  abc def  ", 6, get_text_width) == ["  abc", "def"]
    assert text_wrap("  abc def", 1, get_text_width) == ["", "abc", "def"]
    assert text_wrap("  abc def", 6, get_text_width) == ["  abc", "def"]


class TestIsTextVerticalStacked:
    """The vertical stacked text flag is stored in the associated TextStyle
    table entry and not in the text entity itself.

    """

    @pytest.fixture(scope="class")
    def doc(self):
        d = ezdxf.new()
        style = d.styles.new("Stacked")
        style.is_vertical_stacked = True
        return d

    def test_virtual_text_entity(self):
        assert is_text_vertical_stacked(Text()) is False

    def test_standard_text_entity(self, doc):
        text = doc.modelspace().add_text("Test")
        assert is_text_vertical_stacked(text) is False

    def test_stacked_text_entity(self, doc):
        text = doc.modelspace().add_text(
            "Test", dxfattribs={"style": "Stacked"}
        )
        assert is_text_vertical_stacked(text) is True

    def test_stacked_mtext_entity(self, doc):
        """MTEXT supports the 'style' attribute, but does not really support
        the vertical stacked text feature.

        """
        mtext = doc.modelspace().add_mtext(
            "Test", dxfattribs={"style": "Stacked"}
        )
        assert is_text_vertical_stacked(mtext) is True

    def test_raise_type_error_for_unsupported_types(self):
        with pytest.raises(TypeError):
            is_text_vertical_stacked(DXFEntity())


class TestMTextContentHasInlineFormattingCodes:
    def test_line_breaks_is_not_an_inline_code(self):
        assert has_inline_formatting_codes(r"line\Pline") is False

    def test_non_breaking_space_is_not_an_inline_code(self):
        assert has_inline_formatting_codes(r"line\~line") is False

    def test_inline_formatting_code(self):
        assert has_inline_formatting_codes(r"\Lline") is True

    def test_line_break_and_inline_formatting_code(self):
        assert has_inline_formatting_codes(r"\Kline\Pline\k") is True


@pytest.mark.parametrize("a", [95, 180, 265, -95, -180, -265])
def test_is_upside_down_text_angle(a):
    assert is_upside_down_text_angle(a) is True


@pytest.mark.parametrize("a", [0, 90, 270, -90, -270])
def test_is_not_upside_down_text_angle(a):
    assert is_upside_down_text_angle(a) is False


def test_flipping_tolerance():
    assert is_upside_down_text_angle(95.0, tol=3.0) is True
    assert is_upside_down_text_angle(95.0, tol=5.0) is False
    assert is_upside_down_text_angle(265.0, tol=3.0) is True
    assert is_upside_down_text_angle(265.0, tol=5.0) is False


def test_upright_text_angle():
    assert upright_text_angle(0.0) == 0.0
    assert upright_text_angle(90.0) == 90.0
    assert upright_text_angle(95.0) == 275.0
    assert upright_text_angle(180.0) == 0.0
    assert upright_text_angle(265.0) == 85.0
    assert upright_text_angle(270.0) == 270.0


class TestEstimateMTextContentExtents:
    @pytest.fixture
    def font(self):
        return MonospaceFont(cap_height=2.0, width_factor=1.0)

    def test_empty_text(self, font):
        width, height = estimate_mtext_content_extents("", font)
        assert height == 0.0
        assert width == 0.0

    def test_more_empty_text(self, font):
        width, height = estimate_mtext_content_extents("\n\n\n", font)
        assert height == 0.0
        assert width == 0.0

    def test_single_line(self, font):
        width, height = estimate_mtext_content_extents("XXX", font)
        assert height == 2.0
        assert width == 6.0

    def test_many_lines_no_line_wrapping(self, font):
        width, height = estimate_mtext_content_extents("XXX\nYYYY\nZ", font)
        assert height == pytest.approx(8.668)  # 3x line height + 2x spacing
        assert width == 8.0

    def test_many_lines_with_line_wrapping(self, font):
        width, height = estimate_mtext_content_extents(
            "XXXXXXXXXXXX\nYYYY\nZ", font, column_width=8.0
        )
        assert height == pytest.approx(15.336)  # 5x line height + 4x spacing
        assert width == 8.0


if __name__ == "__main__":
    pytest.main([__file__])
