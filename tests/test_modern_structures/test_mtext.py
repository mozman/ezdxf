# Copyright (c) 2014-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.modern.mtext import split_string_in_chunks, MTextData
from ezdxf.lldxf import const


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007')


@pytest.fixture(scope='module')
def layout(dwg):
    return dwg.modelspace()


def test_new_short_mtext(layout):
    mtext = layout.add_mtext("a new mtext")
    assert "a new mtext" == mtext.get_text()


def test_new_long_mtext(layout):
    text = "0123456789" * 25 + "a new mtext"
    mtext = layout.add_mtext(text)
    assert text == mtext.get_text()


def test_new_long_mtext_2(layout):
    text = "0123456789" * 25 + "abcdefghij" * 25
    mtext = layout.add_mtext(text)
    assert text == mtext.get_text()


def test_last_text_chunk_mtext(layout):
    # this tests none public details of MText class
    text = "0123456789" * 25 + "abcdefghij" * 25 + "a new mtext"
    mtext = layout.add_mtext(text)
    tags = mtext.tags.get_subclass("AcDbMText")
    last_text_chunk = ""
    for tag in tags:
        if tag.code == 1:
            last_text_chunk = tag.value
    assert last_text_chunk == "a new mtext"


def test_get_rotation(layout):
    mtext = layout.add_mtext('TEST')
    mtext.dxf.text_direction = (1, 1, 0) # 45 deg
    mtext.dxf.rotation = 30
    assert 45 == mtext.get_rotation()


def test_set_rotation(layout):
    mtext = layout.add_mtext('TEST')
    mtext.dxf.text_direction = (1, 1, 0) # 45 deg
    mtext.set_rotation(30)
    assert 30 == mtext.get_rotation()
    assert mtext.dxf_attrib_exists('text_direction') is False, "dxfattrib 'text_direction' should be deleted!"


def test_buffer(layout):
    text = "0123456789" * 27
    text2 = "abcdefghij" * 27
    mtext = layout.add_mtext(text)
    with mtext.edit_data() as data:
        data.text = text2
    assert text2 == mtext.get_text()


def test_set_location(layout):
    mtext = layout.add_mtext("TEST").set_location((3, 4), rotation=15, attachment_point=const.MTEXT_MIDDLE_CENTER)
    assert const.MTEXT_MIDDLE_CENTER == mtext.dxf.attachment_point
    assert 15 == mtext.dxf.rotation
    assert (3, 4, 0) == mtext.dxf.insert


def test_set_bg_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color(2)
    assert mtext.dxf.bg_fill == 1
    assert mtext.dxf.bg_fill_color == 2
    assert mtext.dxf_attrib_exists('box_fill_scale') is True, "box_fill_scale must exists, else AutoCAD complains"


def test_set_bg_true_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color((10, 20, 30), scale=2)
    assert mtext.dxf.bg_fill == 1
    assert mtext.dxf.bg_fill_true_color == ezdxf.rgb2int((10, 20, 30))
    assert mtext.dxf.box_fill_scale == 2
    assert mtext.dxf_attrib_exists('bg_fill_color') is True, "bg_fill_color must exists, else AutoCAD complains"


def test_delete_bg_color(layout):
    mtext = layout.add_mtext("TEST").set_bg_color(None)
    # AutoCAD always complains about anything if bg_fill is set to 0, so I delete all tags
    assert mtext.dxf_attrib_exists('bg_fill') is False
    assert mtext.dxf_attrib_exists('bg_fill_color') is False
    assert mtext.dxf_attrib_exists('bg_fill_true_color') is False
    assert mtext.dxf_attrib_exists('bg_fill_color_name') is False
    assert mtext.dxf_attrib_exists('box_fill_scale') is False


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
