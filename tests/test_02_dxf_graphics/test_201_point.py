# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest
import math

from ezdxf.entities.point import Point
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Matrix44
from ezdxf.explode import explode_entity

TEST_CLASS = Point
TEST_TYPE = 'POINT'

ENTITY_R12 = """0
POINT
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
"""

ENTITY_R2000 = """0
POINT
5
0
330
0
100
AcDbEntity
8
0
100
AcDbPoint
10
0.0
20
0.0
30
0.0
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
        'location': (1, 2, 3),
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == 'BYLAYER'
    assert entity.dxf.location == (1, 2, 3)
    assert entity.dxf.location.x == 1, 'is not Vector compatible'
    assert entity.dxf.location.y == 2, 'is not Vector compatible'
    assert entity.dxf.location.z == 3, 'is not Vector compatible'
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr('extrusion') is False, 'just the default value'


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.location == (0, 0, 0)


@pytest.mark.parametrize("txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    point = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    point.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    point.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


def test_transform():
    point = Point.new(dxfattribs={'location': (2, 3, 4), 'extrusion': (0, 1, 0), 'thickness': 2})
    # 1. rotation - 2. scaling - 3. translation
    m = Matrix44.chain(Matrix44.scale(2, 3, 1), Matrix44.translate(1, 1, 1))
    point.transform(m)
    assert point.dxf.location == (5, 10, 5)
    assert point.dxf.extrusion == (0, 1, 0)
    assert point.dxf.thickness == 6

    angle = math.pi / 4
    point.transform(Matrix44.z_rotate(math.pi / 4))
    assert point.dxf.extrusion.isclose((-math.cos(angle), math.sin(angle), 0))
    assert math.isclose(point.dxf.thickness, 6)


def test_fast_translation():
    point = Point.new(dxfattribs={'location': (2, 3, 4), 'extrusion': (0, 1, 0), 'thickness': 2})
    point.translate(1, 2, 3)
    assert point.dxf.location == (3, 5, 7)


def test_do_not_explode_point_entity():
    point = Point()
    with pytest.raises(TypeError):
        explode_entity(point)