# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.text import Text
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

TEST_CLASS = Text
TEST_TYPE = 'TEXT'

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
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'insert': (1, 2, 3),
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == 'BYLAYER'
    assert entity.dxf.insert == (1, 2, 3)
    assert entity.dxf.insert.x == 1, 'is not Vector compatible'
    assert entity.dxf.insert.y == 2, 'is not Vector compatible'
    assert entity.dxf.insert.z == 3, 'is not Vector compatible'
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr('extrusion') is False, 'just the default value'


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.insert == (0, 0, 0)


@pytest.mark.parametrize("txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    attdef = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    attdef.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    attdef.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


@pytest.fixture
def text():
    return Text.new(handle='ABBA', owner='0')


def test_text_set_alignment(text):
    text.set_pos((2, 2), align="TOP_CENTER")
    assert text.dxf.halign == 1
    assert text.dxf.valign == 3
    assert text.dxf.align_point == (2, 2)


def test_text_set_fit_alignment(text):
    text.set_pos((2, 2), (4, 2), align="FIT")
    assert text.dxf.halign == 5
    assert text.dxf.valign == 0
    assert text.dxf.insert == (2, 2)
    assert text.dxf.align_point == (4, 2)


def test_text_get_alignment(text):
    text.dxf.halign = 1
    text.dxf.valign = 3
    assert text.get_align() == 'TOP_CENTER'


def test_text_get_pos_TOP_CENTER(text):
    text.set_pos((2, 2), align="TOP_CENTER")
    align, p1, p2 = text.get_pos()
    assert align == "TOP_CENTER"
    assert p1 == (2, 2)
    assert p2 is None


def test_text_get_pos_LEFT(text):
    text.set_pos((2, 2))
    align, p1, p2 = text.get_pos()
    assert align == "LEFT"
    assert p1 == (2, 2)
    assert p2 is None
