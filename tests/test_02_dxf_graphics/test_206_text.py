# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
import pytest
import math

import ezdxf
from ezdxf.entities.text import Text
from ezdxf.enums import TextEntityAlignment
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Vec3, Matrix44

TEST_CLASS = Text
TEST_TYPE = "TEXT"

ENTITY_R12 = """0
TEXT
5
0
8
0
10
0.0
20
0.0
30
0.0
40
1.0
1
TEXTCONTENT
50
0.0
51
0.0
7
Standard
41
1.0
71
0
72
0
11
0.0
21
0.0
31
0.0
73
0
"""

ENTITY_R2000 = """0
TEXT
5
0
330
0
100
AcDbEntity
8
0
100
AcDbText
10
0.0
20
0.0
30
0.0
40
1.0
1
TEXTCONTENT
50
0.0
51
0.0
7
Standard
41
1.0
71
0
72
0
11
0.0
21
0.0
31
0.0
100
AcDbText
73
0
"""


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


@pytest.fixture(params=[ENTITY_R12, ENTITY_R2000])
def entity(request):
    return TEST_CLASS.from_text(request.param)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES

    assert TEST_TYPE in ENTITY_CLASSES


def test_default_init():
    entity = TEST_CLASS()
    assert entity.dxftype() == TEST_TYPE


def test_default_new():
    entity = TEST_CLASS.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "insert": (1, 2, 3),
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == "BYLAYER"
    assert entity.dxf.insert == (1, 2, 3)
    assert entity.dxf.insert.x == 1, "is not Vec3 compatible"
    assert entity.dxf.insert.y == 2, "is not Vec3 compatible"
    assert entity.dxf.insert.z == 3, "is not Vec3 compatible"
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr("extrusion") is False, "just the default value"


def test_load_from_text(entity):
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 256, "default color is 256 (by layer)"
    assert entity.dxf.insert == (0, 0, 0)


@pytest.mark.parametrize(
    "txt,ver",
    [
        (ENTITY_R2000, DXF2000),
        (ENTITY_R12, DXF12),
    ],
)
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    attdef = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    attdef.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    attdef.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


@pytest.mark.parametrize(
    "invalid_text",
    [
        "test\ntext\r",
        "test\r\ntext",
        "testtext^",
        "test\ntext^",
        "test\ntext^\r",
    ],
)
def test_removing_invalid_chars_at_setting_content(invalid_text):
    txt = Text()
    txt.dxf.text = invalid_text
    assert txt.dxf.text == "testtext"


@pytest.fixture
def text():
    return Text.new(handle="ABBA", owner="0")


def test_set_alignment(text):
    text.set_placement((2, 2), align=TextEntityAlignment.TOP_CENTER)
    assert text.dxf.halign == 1
    assert text.dxf.valign == 3
    assert text.dxf.align_point == (2, 2)


def test_set_fit_alignment(text):
    text.set_placement((2, 2), (4, 2), align=TextEntityAlignment.FIT)
    assert text.dxf.halign == 5
    assert text.dxf.valign == 0
    assert text.dxf.insert == (2, 2)
    assert text.dxf.align_point == (4, 2)


def test_reset_fit_alignment(text):
    text.set_placement((2, 2), (4, 2), align=TextEntityAlignment.FIT)
    text.set_placement((3, 3), (5, 3))
    assert text.dxf.halign == 5
    assert text.dxf.valign == 0
    assert text.dxf.insert == (3, 3)
    assert text.dxf.align_point == (5, 3)


def test_resetting_location_raises_value_error_for_missing_point(text):
    text.set_placement((2, 2), (4, 2), align=TextEntityAlignment.FIT)
    with pytest.raises(ValueError):
        text.set_placement((3, 3))


def test_get_align_enum(text):
    text.dxf.halign = 1
    text.dxf.valign = 3
    assert text.get_align_enum() == TextEntityAlignment.TOP_CENTER


def test_get_pos_enum_TOP_CENTER(text):
    text.set_placement((2, 2), align=TextEntityAlignment.TOP_CENTER)
    align, p1, p2 = text.get_placement()
    assert align == TextEntityAlignment.TOP_CENTER
    assert p1 == (2, 2)
    assert p2 is None


def test_get_pos_LEFT(text):
    text.set_placement((2, 2))
    align, p1, p2 = text.get_placement()
    assert align == TextEntityAlignment.LEFT
    assert p1 == (2, 2)
    assert p2 is None


def test_transform_interface():
    text = Text()
    text.dxf.insert = (1, 0, 0)
    text.transform(Matrix44.translate(1, 2, 3))
    assert text.dxf.insert == (2, 2, 3)

    # optimized translate
    text.dxf.align_point = (3, 2, 1)
    text.translate(1, 2, 3)
    assert text.dxf.insert == (3, 4, 6)
    assert text.dxf.align_point == (4, 4, 4)


def test_fit_length(text):
    text.set_placement((2, 2), (4, 2), align=TextEntityAlignment.FIT)
    assert text.fit_length() == 2

    # remove align point
    del text.dxf.align_point
    assert text.fit_length() == 0


def test_default_font_name(text):
    assert text.font_name() == "arial.ttf"


@pytest.fixture
def text2():
    return Text.new(
        dxfattribs={
            "text": "TEXT",
            "height": 1.0,
            "width": 1.0,
            "rotation": 0,
            "layer": "text",
        }
    ).set_placement((0, 0, 0), align=TextEntityAlignment.LEFT)


@pytest.mark.parametrize("rx, ry", [(1, 1), (-1, 1), (-1, -1), (1, -1)])
def test_scale_and_reflexion(rx, ry, text2):
    insert = Vec3(0, 0, 0)
    m = Matrix44.chain(
        Matrix44.scale(2 * rx, 3 * ry, 1),
        Matrix44.z_rotate(math.radians(45)),
        Matrix44.translate(3 * rx, 3 * ry, 0),
    )

    text2.transform(m)
    check_point = m.transform(insert)
    ocs = text2.ocs()
    assert ocs.to_wcs(text2.dxf.insert).isclose(check_point)
    assert math.isclose(text2.dxf.height, 3.0)
    assert math.isclose(text2.dxf.width, 2.0 / 3.0)


def test_non_uniform_scaling(text2):
    text2.rotate_z(math.radians(30))
    text2.scale(1, 2, 1)
    assert math.isclose(text2.dxf.oblique, 33.004491598883064)


def test_is_backward(text):
    assert text.is_backward is False


def test_set_backward(text):
    text.is_backward = True
    assert text.is_backward is True


def test_is_upside_down(text):
    assert text.is_upside_down is False


def test_set_is_upside_down(text):
    text.is_upside_down = True
    assert text.is_upside_down is True


def test_get_pos_handles_missing_align_point():
    """Any text alignment except LEFT requires and uses the align_point
    attribute as text location point. But there are real world example from
    AutoCAD which do not provide the align_point even it is required.

    In this case the get_pos() method returns the insert attribute.

    """
    text = Text()
    text.dxf.halign = 1  # center
    text.dxf.valign = 1  # bottom
    text.dxf.insert = (1, 2)
    text.dxf.align_point = (3, 4)  # the real alignment point

    # the expected and correct align point:
    alignment, p1, p2 = text.get_placement()
    assert p1 == (3, 4)
    assert p2 is None  # only used for FIT and ALIGNED

    # remove the align point
    del text.dxf.align_point

    alignment, p1, p2 = text.get_placement()
    assert p1 == (1, 2)  # use the insert point instead
    assert p2 is None  # only used for FIT and ALIGNED
