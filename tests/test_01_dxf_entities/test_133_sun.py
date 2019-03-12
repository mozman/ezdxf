# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entities.sun import Sun
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

SUN = """0
SUN
5
0
330
0
100
AcDbSun
90
1
290
1
63
7
421
16777215
40
1.0
291
1
91
2456922
92
43200
292
0
70
0
71
256
280
1
"""


@pytest.fixture
def entity():
    return Sun.from_text(SUN)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'SUN' in ENTITY_CLASSES


def test_default_init():
    entity = Sun()
    assert entity.dxftype() == 'SUN'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = Sun.new(handle='ABBA', owner='0', dxfattribs={
    })
    assert entity.dxf.version == 1
    assert entity.dxf.status == 1
    assert entity.dxf.color == 7
    assert entity.dxf.true_color == 16777215
    assert entity.dxf.intensity == 1
    assert entity.dxf.shadows == 1
    assert entity.dxf.julian_day == 2456922
    assert entity.dxf.time == 43200
    assert entity.dxf.daylight_savings_time == 0
    assert entity.dxf.shadow_type == 0
    assert entity.dxf.shadow_map_size == 256
    assert entity.dxf.shadow_softness == 1


def test_load_from_text(entity):
    assert entity.dxf.version == 1
    assert entity.dxf.status == 1
    assert entity.dxf.color == 7
    assert entity.dxf.true_color == 16777215
    assert entity.dxf.intensity == 1
    assert entity.dxf.shadows == 1
    assert entity.dxf.julian_day == 2456922
    assert entity.dxf.time == 43200
    assert entity.dxf.daylight_savings_time == 0
    assert entity.dxf.shadow_type == 0
    assert entity.dxf.shadow_map_size == 256
    assert entity.dxf.shadow_softness == 1


def test_write_dxf():
    entity = Sun.from_text(SUN)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(SUN)
    assert result == expected


def test_sun():
    doc = ezdxf.new('R2007')
    sun = doc.objects.new_entity('SUN', {})
    assert sun.dxftype() == 'SUN'
    assert sun.dxf.version == 1
