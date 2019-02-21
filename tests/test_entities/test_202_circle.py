# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.circle import Circle
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

TEST_CLASS = Circle
TEST_TYPE = 'CIRCLE'

ENTITY_R12 = """0
CIRCLE
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
"""

ENTITY_R2000 = """0
CIRCLE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbCircle
10
0.0
20
0.0
30
0.0
40
1.0
"""


@pytest.fixture(params=[ENTITY_R12, ENTITY_R2000])
def entity(request):
    return TEST_CLASS.from_text(request.param)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert TEST_TYPE in ENTITY_CLASSES


def test_default_init():
    entity= TEST_CLASS()
    assert entity.dxftype() == TEST_TYPE
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'center': (1, 2, 3),
        'radius': 2.5,
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == 'BYLAYER'

    assert entity.dxf.center == (1, 2, 3)
    assert entity.dxf.center.x == 1, 'is not Vector compatible'
    assert entity.dxf.center.y == 2, 'is not Vector compatible'
    assert entity.dxf.center.z == 3, 'is not Vector compatible'
    assert entity.dxf.radius == 2.5
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr('extrusion') is False, 'just the default value'


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.center == (0, 0, 0)
    assert entity.dxf.radius == 1


def test_write_dxf_2000():
    expected = basic_tags_from_text(ENTITY_R2000)
    line = TEST_CLASS.from_text(ENTITY_R2000)
    collector = TagCollector(dxfversion=DXF2000)
    line.export_dxf(collector)
    assert collector.tags == expected


def test_write_dxf_r12():
    expected = basic_tags_from_text(ENTITY_R12)
    line = TEST_CLASS.from_text(ENTITY_R12)
    line.dxf.shadow_mode = 1  # set value of later DXF version, ignore at export
    assert line.dxf.shadow_mode == 1

    collector = TagCollector(dxfversion=DXF12)
    line.export_dxf(collector)
    assert collector.tags == expected
