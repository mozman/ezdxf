#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.fonts import lff


@pytest.fixture(scope="module")
def font() -> lff.LCFont:
    return lff.loads(EXAMPLE)


def test_load_font(font):
    assert font.name == "FontName"
    assert font.letter_spacing == 3.0
    assert font.word_spacing == 6.75
    assert len(font) == 5


def test_glyph_A(font):
    glyph = font.get(ord("A"))
    assert glyph.code == 65
    assert len(glyph.polylines) == 2

    p0, p1 = glyph.polylines
    assert len(p0) == 2
    assert len(p1) == 3

    assert p0[0][0] == pytest.approx(0.8333)
    assert p1[1][1] == pytest.approx(9)


def test_glyph_dollar(font):
    glyph = font.get(ord("$"))
    assert glyph.code == 36
    assert len(glyph.polylines) == 2
    assert len(glyph.polylines[1][1]) == 3
    bulge = glyph.polylines[1][1][2]
    assert bulge == pytest.approx(0.0935)


def test_composite_glyph(font):
    glyph = font.get(194)
    assert glyph.code == 194
    assert len(glyph.polylines) == 3

    p0, p1, p2 = glyph.polylines
    assert len(p0) == 2
    assert len(p1) == 3
    assert len(p2) == 3

    assert p0[0][0] == pytest.approx(0.8333)
    assert p1[1][1] == pytest.approx(9)
    assert p2[0][1] == pytest.approx(11.5)


def test_render_glyphs(font: lff.LCFont):
    p = font.get(112).to_path()
    assert p.has_curves is True
    assert p.start.isclose((0, -3))
    assert p.end.isclose((0, 0))


EXAMPLE = """# Just a comment
# Name:              FontName
# LetterSpacing:     3
# WordSpacing:       6.75

[0024] $
2,0;2,9
0,1.5;2.39,1,A0.0935;3.235,3.81,A0.8;0.7685,5.19;1.6125,8,A-0.8;4,7.5,A-0.09

[0041] A
0.8333,2.5;5.1666,2.5
0,0;3,9;6,0

[0070] p
0,-3;0,6;2.5,6;4,4.5,A-0.4142;4,1.5;2.5,0,A-0.4142;0,0

[0078] x
0,0;4,6
0,6;4,0

[00c2] Â
C0041
1.5,11.5;3,13;4.5,11.5

"""
if __name__ == "__main__":
    pytest.main([__file__])
