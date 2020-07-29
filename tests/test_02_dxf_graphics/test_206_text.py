# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest
import math

import ezdxf
from ezdxf.entities.text import Text, plain_text
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Vector, Matrix44
from ezdxf.audit import Auditor

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


@pytest.fixture(scope='module')
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


@pytest.mark.parametrize("txt,ver", [
    (ENTITY_R2000, DXF2000),
    (ENTITY_R12, DXF12),
])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    attdef = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    attdef.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    attdef.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


@pytest.mark.parametrize('invalid_text', [
    'test\ntext\r',
    'test\r\ntext',
    'testtext^',
    'test\ntext^',
    'test\ntext^\r',
])
def test_do_not_export_invalid_chars(invalid_text):
    txt = Text()
    txt.dxf.text = invalid_text
    collector = TagCollector(optional=True)
    txt.export_dxf(collector)
    for tag in collector.tags:
        if tag[0] == 1:
            assert tag[1] == 'testtext'


@pytest.mark.parametrize('invalid_text', [
    'test\ntext\r',
    'test\r\ntext',
    'testtext^',
    'test\ntext^',
    'test\ntext^\r',
])
def test_audit_fixes_invalid_chars(invalid_text, doc):
    msp = doc.modelspace()
    txt = msp.add_text(invalid_text)
    auditor = Auditor(doc)
    txt.audit(auditor)
    assert txt.dxf.text == 'testtext'
    assert len(auditor.fixes) > 0


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


def test_text_transform_interface():
    text = Text()
    text.dxf.insert = (1, 0, 0)
    text.transform(Matrix44.translate(1, 2, 3))
    assert text.dxf.insert == (2, 2, 3)

    # optimized translate
    text.dxf.align_point = (3, 2, 1)
    text.translate(1, 2, 3)
    assert text.dxf.insert == (3, 4, 6)
    assert text.dxf.align_point == (4, 4, 4)


@pytest.fixture
def text2():
    return Text.new(dxfattribs={
        'text': 'TEXT',
        'height': 1.0,
        'width': 1.0,
        'rotation': 0,
        'layer': 'text',
    }).set_pos((0, 0, 0), align='LEFT')


@pytest.mark.parametrize('rx, ry', [(1, 1), (-1, 1), (-1, -1), (1, -1)])
def test_text_scale_and_reflexion(rx, ry, text2):
    insert = Vector(0, 0, 0)
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


def test_text_non_uniform_scaling(text2):
    text2.rotate_z(math.radians(30))
    text2.scale(1, 2, 1)
    assert math.isclose(text2.dxf.oblique, 33.004491598883064)


def test_plain_text():
    assert plain_text('%%d') == '°'
    # underline
    assert plain_text('%%u') == ''
    assert plain_text('%%utext%%u') == 'text'
    # single %
    assert plain_text('%u%d%') == '%u%d%'
    t = Text.new(dxfattribs={'text': '45%%d'})
    assert t.plain_text() == '45°'

    assert plain_text('abc^a') == 'abc!'
    assert plain_text('abc^Jdef') == 'abcdef'
    assert plain_text('abc^@def') == 'abc\0def'
