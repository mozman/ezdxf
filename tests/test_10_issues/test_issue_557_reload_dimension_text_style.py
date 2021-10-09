#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.lldxf.tagwriter import TagCollector, Tags

TEXTSTYLE_NAME = "TextStyle"
DIMSTYLE_NAME = "DimensionStyle"
FONT_NAME = "any_font.shx"


@pytest.fixture
def doc():
    doc = ezdxf.new("R2010", setup=False)
    doc.styles.new(TEXTSTYLE_NAME, dxfattribs={"font": FONT_NAME})
    doc.dimstyles.new(DIMSTYLE_NAME, dxfattribs={"dimtxsty": TEXTSTYLE_NAME})
    return doc


def test_export_dimtxsty(doc):
    dimstyle = doc.dimstyles.get(DIMSTYLE_NAME)
    style = doc.styles.get(TEXTSTYLE_NAME)
    t = TagCollector()
    dimstyle.export_dxf(t)
    tags = Tags(t.tags)
    dimtxsty_handle = tags.get_first_value(340)
    assert style.dxf.handle == dimtxsty_handle


def test_reload_dimtxsty(doc, tmpdir):
    filename = tmpdir.join("dim_text_style.dxf")
    doc.saveas(filename)
    # reload file
    doc2 = ezdxf.readfile(filename)

    style = doc2.styles.get(TEXTSTYLE_NAME)
    assert style.dxf.font == FONT_NAME

    dimstyle = doc2.dimstyles.get(DIMSTYLE_NAME)
    assert dimstyle.dxf.dimtxsty == TEXTSTYLE_NAME


if __name__ == "__main__":
    pytest.main([__file__])
