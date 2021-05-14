# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-03-06
import pytest
from ezdxf.entities.mtext import MText
from ezdxf.layouts import VirtualLayout
from ezdxf.lldxf import const
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.colors import rgb2int

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
    e = MText.from_text(MTEXT)
    return e


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
def test_required_escaping_of_line_endings_at_dxf_export(layout, text):
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


def test_default_text_chunk_size_of_250_chars(layout):
    text = "0123456789" * 25 + "abcdefghij" * 25 + "a new mtext"
    mtext = layout.add_mtext(text)
    collector = TagCollector()
    mtext.export_dxf(collector)
    first, second, last = [tag for tag in collector.tags if tag[0] in (1, 3)]

    assert first.code == 3
    assert len(first.value) == 250
    assert text.startswith(first.value)

    assert second.code == 3
    assert len(second.value) == 250
    assert text[250:500] == second.value

    assert last.code == 1
    assert text.endswith(last.value)


def test_text_direction_wins_over_rotation(layout):
    mtext = layout.add_mtext('TEST')
    mtext.dxf.text_direction = (1, 1, 0)  # 45 deg
    mtext.dxf.rotation = 30
    assert mtext.get_rotation() == 45, \
        'Text direction should have higher priority than text rotation,' \
        'if both are present.'


def test_set_rotation_replaces_text_direction(layout):
    mtext = layout.add_mtext('TEST')
    mtext.dxf.text_direction = (1, 1, 0)  # 45 deg
    mtext.set_rotation(30)
    assert mtext.get_rotation() == 30
    assert mtext.dxf.hasattr('text_direction') is False


def test_append_text(layout):
    mtext = layout.add_mtext('abc')
    mtext += 'def'
    assert mtext.text == 'abcdef'


def test_set_location(layout):
    mtext = layout.add_mtext("TEST")
    mtext.set_location(
        insert=(3, 4),
        rotation=15,
        attachment_point=const.MTEXT_MIDDLE_CENTER,
    )
    assert const.MTEXT_MIDDLE_CENTER == mtext.dxf.attachment_point
    assert mtext.dxf.rotation == 15
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


def test_set_text_frame_only(layout):
    # special case, text frame only with scaling factor = 1.5
    mtext = layout.add_mtext("TEST").set_bg_color(None, text_frame=True)
    assert mtext.dxf.bg_fill == const.MTEXT_TEXT_FRAME
    assert mtext.dxf.hasattr('bg_fill_color') is False
    assert mtext.dxf.hasattr('bg_fill_true_color') is False
    assert mtext.dxf.hasattr('bg_fill_color_name') is False
    assert mtext.dxf.hasattr('box_fill_scale') is False


def test_transform_interface():
    mtext = MText()
    mtext.dxf.insert = (1, 0, 0)
    mtext.translate(1, 2, 3)
    assert mtext.dxf.insert == (2, 2, 3)


def test_bg_fill_flags():
    mtext = MText.new()
    mtext.dxf.bg_fill = 0  # bg fill off
    mtext.dxf.bg_fill = 1  # bg fill as color
    assert mtext.dxf.bg_fill == 1
    mtext.dxf.bg_fill = 2  # bg fill as window color
    assert mtext.dxf.bg_fill == 2
    mtext.dxf.bg_fill = 3  # bg fill as background color
    assert mtext.dxf.bg_fill == 3
    mtext.dxf.bg_fill = 0x10  # text frame?
    assert mtext.dxf.bg_fill == 0x10
    mtext.dxf.bg_fill = 4  # invalid flag
    assert mtext.dxf.bg_fill == 0
    mtext.dxf.bg_fill = 0x20  # invalid flag
    assert mtext.dxf.bg_fill == 0
