# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.tools.standards import setup_visual_styles


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new("R2007")


def test_visualstyle(doc):
    vstyle = doc.objects.new_entity(
        "VISUALSTYLE", dxfattribs={"description": "Testing", "style_type": 7}
    )
    assert vstyle.dxftype() == "VISUALSTYLE"
    assert vstyle.dxf.description == "Testing"
    assert vstyle.dxf.style_type == 7


def test_setup_standard_visual_styles(doc):
    setup_visual_styles(doc)
    styles = doc.rootdict["ACAD_VISUALSTYLE"]
    assert len(styles) == 25
    assert "Wireframe" in styles
