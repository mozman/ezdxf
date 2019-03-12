# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-03-06
import pytest
import ezdxf
from ezdxf.lldxf import const

from ezdxf.entities.mtext import MText, split_string_in_chunks, MTextData
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text


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


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new('R2007')


@pytest.fixture(scope='module')
def layout(doc):
    return doc.modelspace()


def test_new_short_mtext(layout):
    mtext = layout.add_mtext("a new mtext")
    assert "a new mtext" == mtext.text


def test_new_long_mtext(layout):
    text = "0123456789" * 25 + "a new mtext"
    mtext = layout.add_mtext(text)
    assert text == mtext.text


def test_new_long_mtext_2(layout):
    text = "0123456789" * 25 + "abcdefghij" * 25
    mtext = layout.add_mtext(text)
    assert text == mtext.text


def test_last_text_chunk_mtext(layout):
    # this tests none public details of MText class
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
    mtext.dxf.text_direction = (1, 1, 0) # 45 deg
    mtext.set_rotation(30)
    assert 30 == mtext.get_rotation()
    assert mtext.dxf.hasattr('text_direction') is False, "dxfattrib 'text_direction' should be deleted!"


def test_buffer(layout):
    text = "0123456789" * 27
    text2 = "abcdefghij" * 27
    mtext = layout.add_mtext(text)
    with mtext.edit_data() as data:
        data.text = text2
    assert text2 == mtext.text


def test_set_location(layout):
    mtext = layout.add_mtext("TEST").set_location((3, 4), rotation=15, attachment_point=const.MTEXT_MIDDLE_CENTER)
    assert const.MTEXT_MIDDLE_CENTER == mtext.dxf.attachment_point
    assert 15 == mtext.dxf.rotation
    assert (3, 4, 0) == mtext.dxf.insert


def test_set_bg_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color(2)
    assert mtext.dxf.bg_fill == 1
    assert mtext.dxf.bg_fill_color == 2
    assert mtext.dxf.hasattr('box_fill_scale') is True, "box_fill_scale must exists, else AutoCAD complains"


def test_set_bg_true_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color((10, 20, 30), scale=2)
    assert mtext.dxf.bg_fill == 1
    assert mtext.dxf.bg_fill_true_color == ezdxf.rgb2int((10, 20, 30))
    assert mtext.dxf.box_fill_scale == 2
    assert mtext.dxf.hasattr('bg_fill_color') is True, "bg_fill_color must exists, else AutoCAD complains"


def test_delete_bg_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color(None)
    # AutoCAD always complains about anything if bg_fill is set to 0, so I delete all tags
    assert mtext.dxf.hasattr('bg_fill') is False
    assert mtext.dxf.hasattr('bg_fill_color') is False
    assert mtext.dxf.hasattr('bg_fill_true_color') is False
    assert mtext.dxf.hasattr('bg_fill_color_name') is False
    assert mtext.dxf.hasattr('box_fill_scale') is False


def test_set_bg_canvas_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color('canvas')
    assert mtext.dxf.bg_fill == 3
    assert mtext.dxf_attrib_exists('bg_fill_color') is True, "bg_fill_color must exists, else AutoCAD complains"
    assert mtext.dxf_attrib_exists('box_fill_scale') is True, "box_fill_scale must exists, else AutoCAD complains"


TESTSTR = "0123456789"


def test_empty_string():
    s = ""
    chunks = split_string_in_chunks(s, 20)
    assert 0 == len(chunks)


def test_short_string():
    s = TESTSTR
    chunks = split_string_in_chunks(s, 20)
    assert 1 == len(chunks)
    assert TESTSTR == chunks[0]


def test_long_string():
    s = TESTSTR * 3
    chunks = split_string_in_chunks(s, 20)
    assert 2 == len(chunks)
    assert TESTSTR*2 == chunks[0]
    assert TESTSTR == chunks[1]


def test_long_string_2():
    s = TESTSTR * 4
    chunks = split_string_in_chunks(s, 20)
    assert 2 == len(chunks)
    assert TESTSTR*2 == chunks[0]
    assert TESTSTR*2 == chunks[1]


def test_new_buffer():
    b = MTextData("abc")
    assert "abc" == b.text


def test_append_text():
    b = MTextData("abc")
    b += "def" + b.NEW_LINE

    assert "abcdef\\P;" == b.text
