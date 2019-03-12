# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-03-05
import pytest

from ezdxf.entities.xline import Ray
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

RAY = """0
RAY
5
0
330
0
100
AcDbEntity
8
0
100
AcDbRay
10
0.0
20
0.0
30
0.0
11
1.0
21
0.0
31
0.0
"""


@pytest.fixture
def entity():
    return Ray.from_text(RAY)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'RAY' in ENTITY_CLASSES


def test_default_init():
    entity = Ray()
    assert entity.dxftype() == 'RAY'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = Ray.new(handle='ABBA', owner='0', dxfattribs={
        'color': 7,
        'start': (1, 2, 3),
        'unit_vector': (4, 5, 6),
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.start == (1, 2, 3)
    assert entity.dxf.unit_vector == (4, 5, 6)


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.start == (0, 0, 0)
    assert entity.dxf.unit_vector == (1, 0, 0)


def test_write_dxf():
    entity = Ray.from_text(RAY)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(RAY)
    assert result == expected
