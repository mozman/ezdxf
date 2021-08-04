# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.entities import Attrib, MText
from ezdxf.entities.attrib import EmbeddedMText, EmbeddedMTextNS
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

TEST_CLASS = Attrib
TEST_TYPE = "ATTRIB"

ENTITY_R12 = """0
ATTRIB
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
DEFAULTTEXT
50
0.0
51
0.0
7
STANDARD
41
1.0
72
0
11
0.0
21
0.0
31
0.0
71
0
2
TAG
70
0
74
0
"""

ENTITY_R2000 = """0
ATTRIB
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
DEFAULTTEXT
50
0.0
51
0.0
7
STANDARD
41
1.0
72
0
11
0.0
21
0.0
31
0.0
71
0
100
AcDbAttribute
2
TAG
70
0
73
0
74
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
    "txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)]
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
    txt = Attrib()
    txt.dxf.text = invalid_text
    assert txt.dxf.text == "testtext"


class TestEmbeddedMTextSupport:
    @pytest.fixture
    def attrib(self) -> Attrib:
        return Attrib.from_text(EMBEDDED_MTEXT)

    def test_has_embedded_mtext(self, attrib):
        assert attrib.has_embedded_mtext_entity is True

    def test_get_plain_mtext(self, attrib):
        assert attrib.plain_mtext() == "TEST VENUE\nTEST FLOOR PLAN"

    def test_get_virtual_mtext_entity(self, attrib):
        mtext = attrib.virtual_mtext_entity()
        assert mtext.plain_text() == "TEST VENUE\nTEST FLOOR PLAN"

    def test_attrib_graphic_attributes(self, attrib):
        assert attrib.dxf.color == 7
        assert attrib.dxf.layer == "AttribLayer"

    def test_mtext_graphic_attributes_inherited_from_host(self, attrib):
        mtext = attrib.virtual_mtext_entity()
        assert mtext.dxf.color == 7
        assert mtext.dxf.layer == "AttribLayer"

    def test_mtext_entity_attributes(self, attrib):
        mtext = attrib.virtual_mtext_entity()
        # These seems to be the required DXF tag for the embedded MTEXT entity:
        assert mtext.dxf.insert.isclose((592.3, 962.6, 0))
        assert mtext.dxf.char_height == 3.0
        assert mtext.dxf.width == 0
        assert mtext.dxf.defined_height == 0
        assert mtext.dxf.attachment_point == 5
        assert mtext.dxf.flow_direction == 5
        assert mtext.dxf.style == "Arial_3 NARROW"
        assert mtext.dxf.line_spacing_style == 1
        assert mtext.dxf.line_spacing_factor == 1.0

    def test_dxf_export_matches_test_data(self, attrib):
        result = TagCollector.dxftags(attrib, dxfversion=ezdxf.const.DXF2018)
        expected = basic_tags_from_text(EMBEDDED_MTEXT)
        assert result == expected

    def test_set_mtext(self):
        attrib = Attrib.new(dxfattribs={"color": 3, "text": "TEST"})
        mtext = MText.new(dxfattribs={"color": 3})
        mtext.text = "LINE1\nLINE2"
        attrib.set_mtext(mtext)
        assert attrib.has_embedded_mtext_entity is True


class TestEmbeddedMText:
    def test_special_namespace(self):
        ns = EmbeddedMTextNS()
        assert "char_height" in ns.dxfattribs
        assert "color" not in ns.dxfattribs

    def test_setup(self):
        txt = EmbeddedMText()
        assert "char_height" in txt.dxf.dxfattribs
        assert "color" not in txt.dxf.dxfattribs

    def test_set_mtext_attribute(self):
        txt = EmbeddedMText()
        txt.dxf.char_height = 2.5
        assert txt.dxf.char_height == 2.5

    def test_set_invalid_mtext_attribute(self):
        txt = EmbeddedMText()
        assert txt.dxf.hasattr("color") is False
        with pytest.raises(AttributeError):
            txt.dxf.color = 3


EMBEDDED_MTEXT = r"""0
ATTRIB
5
2AE
330
2AD
100
AcDbEntity
8
AttribLayer
62
7
100
AcDbText
10
574.8
20
961.1
30
0.0
40
3.0
1
TEST VENUE
7
Arial_3 NARROW
72
1
11
592.3
21
962.6
31
0.0
100
AcDbAttribute
280
0
2
DRAWING-NAME
70
0
74
2
280
0
71
2
72
0
11
592.3
21
962.6
31
0.0
101
Embedded Object
10
592.3
20
962.6
30
0.0
40
3.0
41
0.0
46
0.0
71
5
72
5
1
TEST VENUE\PTEST FLOOR PLAN
7
Arial_3 NARROW
73
1
44
1.0
"""
