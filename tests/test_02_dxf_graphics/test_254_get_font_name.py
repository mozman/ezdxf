#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.entities import get_font_name, DXFEntity
from ezdxf.lldxf import const


@pytest.fixture(scope="module")
def msp():
    doc = ezdxf.new()
    doc.styles.add("ARIAL", font="arial.ttf")
    return doc.modelspace()


def test_get_font_name_for_entity_without_font_support():
    e = DXFEntity()
    assert get_font_name(e) == const.DEFAULT_TEXT_FONT, "should return the default font"


def test_get_font_name_for_text(msp):
    text = msp.add_text("abc", dxfattribs={"style": "ARIAL"})
    assert get_font_name(text) == "arial.ttf"


def test_undefined_text_style(msp):
    text = msp.add_text("abc", dxfattribs={"style": "UNDEFINED"})
    assert get_font_name(text) == const.DEFAULT_TEXT_FONT


def test_get_font_name_for_mtext(msp):
    mtext = msp.add_mtext("abc", dxfattribs={"style": "ARIAL"})
    assert get_font_name(mtext) == "arial.ttf"


if __name__ == "__main__":
    pytest.main([__file__])
