# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-03-06
import pytest
from ezdxf.entities.mtext import (
    MText, split_mtext_string, plain_mtext, caret_decode,
    _dxf_encode_line_endings, replace_non_printable_characters,
)
from ezdxf.lldxf import const
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.tools.rgb import rgb2int
from ezdxf.layouts import VirtualLayout

MTEXT = """0
MTEXT
5
0
330
0
100
AcDbEntity
8
0
100
AcDbMText
 10
0
 20
0
 30
0
40
1.0
71
1
1

73
1
"""


@pytest.fixture
def entity():
    return MText.from_text(MTEXT)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'MTEXT' in ENTITY_CLASSES


def test_default_init():
    entity = MText()
    assert entity.dxftype() == 'MTEXT'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = MText.new(handle='ABBA', owner='0', dxfattribs={
        'color': 7,
        'insert': (1, 2, 3),
        'char_height': 1.8,
        'width': 20,
        'defined_height': 30,
        'attachment_point': 3,
        'flow_direction': 3,
        'style': 'OpenSans',
        'extrusion': (4, 5, 6),
        'text_direction': (7, 8, 9),
        'rect_width': 42,
        'rect_height': 43,
        'rotation': 50,
        'line_spacing_style': 2,
        'line_spacing_factor': 1.7,
        'box_fill_scale': 1.1,
        'bg_fill': 3,
        'bg_fill_color': 14,
        'bg_fill_true_color': 111222,
        'bg_fill_color_name': 'magenta',
        'bg_fill_transparency': 1,
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.insert == (1, 2, 3)
    assert entity.dxf.char_height == 1.8
    assert entity.dxf.width == 20
    assert entity.dxf.defined_height == 30
    assert entity.dxf.attachment_point == 3
    assert entity.dxf.flow_direction == 3
    assert entity.dxf.extrusion == (4, 5, 6)
    assert entity.dxf.text_direction == (7, 8, 9)
    assert entity.dxf.rect_width == 42
    assert entity.dxf.rect_height == 43
    assert entity.dxf.rotation == 50
    assert entity.dxf.line_spacing_style == 2
    assert entity.dxf.line_spacing_factor == 1.7
    assert entity.dxf.box_fill_scale == 1.1
    assert entity.dxf.bg_fill == 3
    assert entity.dxf.bg_fill_color == 14
    assert entity.dxf.bg_fill_true_color == 111222
    assert entity.dxf.bg_fill_color_name == 'magenta'
    assert entity.dxf.bg_fill_transparency == 1


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.insert == (0, 0, 0)
    assert entity.dxf.char_height == 1.
    assert entity.dxf.attachment_point == 1
    assert entity.dxf.line_spacing_style == 1
    assert entity.text == ''


def test_write_dxf():
    entity = MText.from_text(MTEXT)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(MTEXT)
    assert result == expected


def test_expected_python_backslash_decoding():
    s = r"Swiss 721 (helvetica-like)\P\P\pt7.1875,8.38542;{\H0.6667x;Regular" \
        r"\P\P\pl0.899488,t8.38542;Swiss Light^I\fSwis721 Lt BT|b0|i0|c0|p34" \
        r";\C5;abcdefghijABCDEFGHIJ123456789!@#$%^ &*()\P\Ftxt.shx|c1;\P\C25" \
        r"6;Swiss Light Italic\Ftxt.shx|c0;^I\fSwis721 Lt BT|b0|i"
    assert len(s) == 253


@pytest.fixture
def layout():
    return VirtualLayout()


@pytest.mark.parametrize('text', [
    'test\ntext',  # single new line
    'test\r\ntext',  # single new line
    'test\ntext\rtext',  # ignore a single '\r'
])
def test_required_escaping_of_line_endings(layout, text):
    txt = layout.add_mtext(text)
    collector = TagCollector(optional=True)
    txt.export_dxf(collector)
    for tag in collector.tags:
        if tag[0] == 1:
            assert tag[1].count(r'\P') == 1
            assert '\n' not in tag[1]
            assert '\r' not in tag[1]


@pytest.mark.parametrize('text', [
    "a new mtext",
    "0123456789" * 25 + "a new mtext",
    "0123456789" * 25 + "abcdefghij" * 25,
])
def test_new_long_mtext(layout, text):
    mtext = layout.add_mtext(text)
    assert text == mtext.text
    assert text == mtext.plain_text()


def test_last_text_chunk_mtext(layout):
    text = "0123456789" * 25 + "abcdefghij" * 25 + "a new mtext"
    mtext = layout.add_mtext(text)
    collector = TagCollector()
    mtext.export_dxf(collector)
    tags = collector.tags
    last_text_chunk = ""
    for tag in tags:
        if tag[0] == 1:
            last_text_chunk = tag.value
    assert last_text_chunk == "a new mtext"


def test_get_rotation(layout):
    mtext = layout.add_mtext('TEST')
    mtext.dxf.text_direction = (1, 1, 0)  # 45 deg
    mtext.dxf.rotation = 30
    assert 45 == mtext.get_rotation()


def test_set_rotation(layout):
    mtext = layout.add_mtext('TEST')
    mtext.dxf.text_direction = (1, 1, 0)  # 45 deg
    mtext.set_rotation(30)
    assert 30 == mtext.get_rotation()
    assert mtext.dxf.hasattr('text_direction') is False


def test_append_text(layout):
    mtext = layout.add_mtext('abc')
    mtext += 'def'
    assert mtext.text == 'abcdef'


def test_set_location(layout):
    mtext = layout.add_mtext("TEST").set_location(
        (3, 4), rotation=15, attachment_point=const.MTEXT_MIDDLE_CENTER)
    assert const.MTEXT_MIDDLE_CENTER == mtext.dxf.attachment_point
    assert 15 == mtext.dxf.rotation
    assert (3, 4, 0) == mtext.dxf.insert


def test_set_bg_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color(2)
    assert mtext.dxf.bg_fill == 1
    assert mtext.dxf.bg_fill_color == 2
    assert mtext.dxf.hasattr('box_fill_scale') is True, \
        "box_fill_scale attribute must exists, else AutoCAD complains"


def test_set_bg_true_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color((10, 20, 30), scale=2)
    assert mtext.dxf.bg_fill == 1
    assert mtext.dxf.bg_fill_true_color == rgb2int((10, 20, 30))
    assert mtext.dxf.box_fill_scale == 2
    assert mtext.dxf.hasattr('bg_fill_color') is True, \
        "bg_fill_color attribute must exists, else AutoCAD complains"


def test_delete_bg_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color(None)
    # AutoCAD always complains about anything if bg_fill is set to 0,
    # so I delete all related tags.
    assert mtext.dxf.hasattr('bg_fill') is False
    assert mtext.dxf.hasattr('bg_fill_color') is False
    assert mtext.dxf.hasattr('bg_fill_true_color') is False
    assert mtext.dxf.hasattr('bg_fill_color_name') is False
    assert mtext.dxf.hasattr('box_fill_scale') is False


def test_set_bg_canvas_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color('canvas')
    assert mtext.dxf.bg_fill == 3
    assert mtext.has_dxf_attrib('bg_fill_color') is True, \
        "bg_fill_color attribute must exists, else AutoCAD complains"
    assert mtext.has_dxf_attrib('box_fill_scale') is True, \
        "box_fill_scale attribute must exists, else AutoCAD complains"


TESTSTR = "0123456789"


def test_split_empty_string():
    s = ""
    chunks = split_mtext_string(s, 20)
    assert 0 == len(chunks)


def test_split_short_string():
    s = TESTSTR
    chunks = split_mtext_string(s, 20)
    assert 1 == len(chunks)
    assert TESTSTR == chunks[0]


def test_split_long_string():
    s = TESTSTR * 3
    chunks = split_mtext_string(s, 20)
    assert 2 == len(chunks)
    assert TESTSTR * 2 == chunks[0]
    assert TESTSTR == chunks[1]


def test_split_longer_string():
    s = TESTSTR * 4
    chunks = split_mtext_string(s, 20)
    assert 2 == len(chunks)
    assert TESTSTR * 2 == chunks[0]
    assert TESTSTR * 2 == chunks[1]


def test_do_not_split_at_caret():
    # do not split at '^'
    s = 'a' * 19 + '^Ixxx^'
    chunks = split_mtext_string(s, 20)
    assert 2 == len(chunks)
    assert chunks[0] == 'a' * 19
    assert chunks[1] == '^Ixxx^'


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


def test_transform_interface():
    mtext = MText()
    mtext.dxf.insert = (1, 0, 0)
    mtext.translate(1, 2, 3)
    assert mtext.dxf.insert == (2, 2, 3)


def test_dxf_line_ending_encoding():
    assert _dxf_encode_line_endings('\\P test') == '\\P test'
    assert _dxf_encode_line_endings('abc\ndef') == 'abc\\Pdef'
    assert _dxf_encode_line_endings('abc\rdef') == 'abcdef', \
        r"a single '\r' should be ignored"
    assert _dxf_encode_line_endings('abc\r\ndef') == 'abc\\Pdef', \
        r"'\r\n' represents a single newline"


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


def test_replace_non_printable():
    assert replace_non_printable_characters('abc') == 'abc'
    assert replace_non_printable_characters('abc def') == 'abc def'
    assert replace_non_printable_characters('abc \tdef') == 'abc \tdef'
    assert replace_non_printable_characters('abc\0def') == 'abc▯def'
    assert replace_non_printable_characters(
        'abc\0def', replacement=' ') == 'abc def'
