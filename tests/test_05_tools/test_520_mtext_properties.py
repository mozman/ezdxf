#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.lldxf.const import MTextParagraphAlignment
from ezdxf.tools.text import (
    MTextProperties, ParagraphProperties
)


def test_underline():
    p = MTextProperties()
    assert p.underline is False
    p.underline = True
    assert p.underline is True


def test_strike():
    p = MTextProperties()
    assert p.strike_through is False
    p.strike_through = True
    assert p.strike_through is True


def test_overstrike():
    p = MTextProperties()
    assert p.overline is False
    p.overline = True
    assert p.overline is True


def test_copy():
    p = MTextProperties()
    p.underline = True
    p2 = p.copy()
    p2.underline = False
    assert p != p2


def test_equality():
    p = MTextProperties()
    p.underline = True
    p2 = MTextProperties()
    p2.underline = True
    assert p == p2


def test_set_aci():
    p = MTextProperties()
    p.rgb = (0, 1, 2)
    p.aci = 7
    assert p.aci == 7
    assert p.rgb is None, "should reset rgb value"


class TestParagraphPropertiesToString:
    def test_default_properties(self):
        assert ParagraphProperties().tostring() == ""

    def test_indent_first_line(self):
        assert ParagraphProperties(indent=2).tostring() == "\\pi2;"

    def test_indent_paragraph_left(self):
        assert ParagraphProperties(left=3).tostring() == "\\pi0,l3;"

    def test_indent_paragraph_right(self):
        assert ParagraphProperties(right=4).tostring() == "\\pi0,r4;"

    def test_center_alignment_without_indentation(self):
        # extended argument "alignment" requires a leading "x"
        assert ParagraphProperties(
            align=MTextParagraphAlignment.CENTER).tostring() == "\\pxqc;"

    def test_center_alignment_with_indentation(self):
        # always a "," after indentations
        # extended argument "alignment" requires a leading "x"
        assert ParagraphProperties(
            indent=2.5,
            align=MTextParagraphAlignment.CENTER).tostring() == "\\pi2.5,xqc;"

    def test_one_tab_stop(self):
        p = ParagraphProperties(tab_stops=(1, ))
        # extended argument "tab stops" requires a leading "x"
        assert p.tostring() == "\\pxt1;"

    def test_multiple_tab_stops(self):
        p = ParagraphProperties(tab_stops=(1, 2, 3))
        # extended argument "tab stops" requires a leading "x"
        assert p.tostring() == "\\pxt1,2,3;"

    def test_different_kinds_of_tab_stops(self):
        # tab stops without prefix or numbers are left adjusted
        # tab stops, e.g 2 or '2'
        # prefix 'c' defines a center adjusted tab stop e.g. 'c3.5'
        # prefix 'r' defines a right adjusted tab stop e.g. 'r2.7'
        p = ParagraphProperties(tab_stops=(1, 'c2', 'r3.7'))
        # extended argument "tab stops" requires a leading "x"
        assert p.tostring() == "\\pxt1,c2,r3.7;"

    def test_indention_and_multiple_tab_stops(self):
        p = ParagraphProperties(indent=1,
                                tab_stops=(1, 2, 3))
        # always a "," after indentations
        # extended argument "tab stops" requires a leading "x"
        assert p.tostring() == "\\pi1,xt1,2,3;"

    def test_justified_alignment_and_multiple_tab_stops(self):
        p = ParagraphProperties(align=MTextParagraphAlignment.JUSTIFIED,
                                tab_stops=(1, 2, 3))
        # extended argument "alignment" requires a leading "x"
        assert p.tostring() == "\\pxqjt1,2,3;"


if __name__ == '__main__':
    pytest.main([__file__])
