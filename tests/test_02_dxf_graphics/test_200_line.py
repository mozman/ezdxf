# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.line import Line
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

TEST_CLASS = Line
TEST_TYPE = 'LINE'

ENTITY_R12 = """0
LINE
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
11
1.0
21
1.0
31
1.0
"""

ENTITY_R2000 = """0
LINE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbLine
10
0.0
20
0.0
30
0.0
11
1.0
21
1.0
31
1.0
"""


@pytest.fixture(params=[ENTITY_R12, ENTITY_R2000])
def line(request):
    return Line.from_text(request.param)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert TEST_TYPE in ENTITY_CLASSES


def test_default_init():
    entity = Line()
    assert entity.dxftype() == TEST_TYPE


def test_default_new():
    entity = Line.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'start': (1, 2, 3),
        'end': (4, 5, 6),
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.start == (1, 2, 3)
    assert entity.dxf.start.x == 1, 'is not Vector compatible'
    assert entity.dxf.start.y == 2, 'is not Vector compatible'
    assert entity.dxf.start.z == 3, 'is not Vector compatible'
    assert entity.dxf.end == (4, 5, 6)
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr('extrusion') is False, 'just the default value'

    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1


def test_load_from_text(line):
    assert line.dxf.layer == '0'
    assert line.dxf.color == 256, 'default color is 256 (by layer)'
    assert line.dxf.start == (0, 0, 0)
    assert line.dxf.end == (1, 1, 1)


@pytest.mark.parametrize("txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    line = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    line.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    line.export_dxf(collector2)
    assert collector.has_all_tags(collector2)

