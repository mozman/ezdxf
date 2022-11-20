# Copyright (c) 2010-2022, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf import const
from ezdxf.enums import MTextEntityAlignment
from ezdxf.addons import MText


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new("R12")


def test_horiz_top(doc):
    layout = doc.blocks.new("test_horiz_top")
    text = "lineA\nlineB"
    mtext = MText(text, (0.0, 0.0, 0.0), 1.0)
    mtext.render(layout)
    assert len(layout) == 2
    lines = list(layout)
    assert lines[0].dxftype() == "TEXT"
    assert lines[1].dxftype() == "TEXT"
    assert lines[0].dxf.text == "lineA"
    assert lines[1].dxf.text == "lineB"
    assert lines[0].dxf.align_point == (0, 0, 0)
    assert lines[1].dxf.align_point == (0, -1, 0)
    assert lines[0].dxf.valign == const.TOP
    assert lines[0].dxf.halign == const.LEFT


def test_horiz_bottom(doc):
    layout = doc.blocks.new("test_horiz_bottom")
    text = "lineA\nlineB"
    mtext = MText(
        text, (0.0, 0.0, 0.0), 1.0, align=MTextEntityAlignment.BOTTOM_LEFT
    )
    mtext.render(layout)
    assert len(layout) == 2
    lines = list(layout)
    assert lines[0].dxftype() == "TEXT"
    assert lines[1].dxftype() == "TEXT"
    assert lines[0].dxf.text == "lineA"
    assert lines[1].dxf.text == "lineB"
    assert lines[0].dxf.align_point == (0, 1, 0)
    assert lines[1].dxf.align_point == (0, 0, 0)
    assert lines[0].dxf.valign == const.BOTTOM
    assert lines[0].dxf.halign == const.LEFT


def test_horiz_middle(doc):
    layout = doc.blocks.new("test_horiz_middle")
    text = "lineA\nlineB"
    mtext = MText(
        text, (0.0, 0.0, 0.0), 1.0, align=MTextEntityAlignment.MIDDLE_LEFT
    )
    mtext.render(layout)
    assert len(layout) == 2
    lines = list(layout)
    assert lines[0].dxftype() == "TEXT"
    assert lines[1].dxftype() == "TEXT"
    assert lines[0].dxf.text == "lineA"
    assert lines[1].dxf.text == "lineB"
    assert lines[0].dxf.align_point == (0, 0.5, 0)
    assert lines[1].dxf.align_point == (0, -0.5, 0)
    assert lines[0].dxf.valign == const.MIDDLE
    assert lines[0].dxf.halign == const.LEFT


def test_45deg_top(doc):
    layout = doc.blocks.new("test_45deg_top")
    text = "lineA\nlineB\nlineC"
    mtext = MText(
        text,
        (0.0, 0.0, 0.0),
        1.0,
        align=MTextEntityAlignment.TOP_LEFT,
        rotation=45,
    )
    mtext.render(layout)
    assert len(layout) == 3
    lines = list(layout)
    assert lines[0].dxftype() == "TEXT"
    assert lines[1].dxftype() == "TEXT"
    assert lines[2].dxftype() == "TEXT"
    assert lines[0].dxf.text == "lineA"
    assert lines[1].dxf.text == "lineB"
    assert lines[2].dxf.text == "lineC"
    assert lines[0].dxf.align_point == (0, 0, 0)
    assert lines[1].dxf.align_point == (0.707107, -0.707107, 0)
    assert lines[2].dxf.align_point == (1.414214, -1.414214, 0)
    assert lines[0].dxf.rotation == 45
    assert lines[0].dxf.valign == const.TOP
    assert lines[0].dxf.halign == const.LEFT


def test_45deg_bottom(doc):
    layout = doc.blocks.new("test_45deg_bottom")
    text = "lineA\nlineB\nlineC"
    mtext = MText(
        text,
        (0.0, 0.0, 0.0),
        1.0,
        align=MTextEntityAlignment.BOTTOM_LEFT,
        rotation=45,
    )
    mtext.render(layout)
    assert len(layout) == 3
    lines = list(layout)
    assert lines[0].dxftype() == "TEXT"
    assert lines[1].dxftype() == "TEXT"
    assert lines[2].dxftype() == "TEXT"
    assert lines[0].dxf.text == "lineA"
    assert lines[1].dxf.text == "lineB"
    assert lines[2].dxf.text == "lineC"
    assert lines[0].dxf.align_point == (-1.414214, 1.414214, 0)
    assert lines[1].dxf.align_point == (-0.707107, 0.707107, 0)
    assert lines[2].dxf.align_point == (0, 0, 0)
    assert lines[0].dxf.rotation == 45
    assert lines[0].dxf.valign == const.BOTTOM
    assert lines[0].dxf.halign == const.LEFT


def test_one_liner(doc):
    layout = doc.blocks.new("test_one_liner")
    text = "OneLine"
    mtext = MText(text, (0.0, 0.0, 0.0))
    mtext.render(layout)
    assert len(layout) == 1
    lines = list(layout)
    assert lines[0].dxftype() == "TEXT"
    assert lines[0].dxf.align_point == (0, 0, 0)
    assert lines[0].dxf.valign == const.TOP
    assert lines[0].dxf.halign == const.LEFT


def test_get_attribute_by_subscript():
    mtext = MText("Test\nTest", (0, 0))
    layer = mtext["layer"]
    assert layer == mtext.layer


def test_set_attribute_by_subscript():
    mtext = MText("Test\nTest", (0, 0))
    mtext["layer"] = "modified"
    assert mtext.layer == "modified"
