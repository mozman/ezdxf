# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entities.light import Light
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

LIGHT = """0
LIGHT
5
0
330
0
100
AcDbEntity
8
0
100
AcDbLight
90
0
1
NAME
70
1
290
1
291
0
40
1.0
72
2
292
0
293
1
73
0
"""


@pytest.fixture
def entity():
    return Light.from_text(LIGHT)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'LIGHT' in ENTITY_CLASSES


def test_default_init():
    entity = Light()
    assert entity.dxftype() == 'LIGHT'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = Light.new(handle='ABBA', owner='0', dxfattribs={
    })
    assert entity.dxf.version == 0
    assert entity.dxf.name == ""
    assert entity.dxf.type == 1
    assert entity.dxf.status == 1
    assert entity.dxf.plot_glyph == 0
    assert entity.dxf.intensity == 1
    assert entity.dxf.attenuation_type == 2
    assert entity.dxf.use_attenuation_limits == 0
    assert entity.dxf.cast_shadows == 1
    assert entity.dxf.shadow_type == 0


def test_load_from_text(entity):
    assert entity.dxf.version == 0
    assert entity.dxf.name == "NAME"
    assert entity.dxf.type == 1
    assert entity.dxf.status == 1
    assert entity.dxf.plot_glyph == 0
    assert entity.dxf.intensity == 1
    assert entity.dxf.attenuation_type == 2
    assert entity.dxf.use_attenuation_limits == 0
    assert entity.dxf.cast_shadows == 1
    assert entity.dxf.shadow_type == 0


def test_write_dxf():
    entity = Light.from_text(LIGHT)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(LIGHT)
    assert result == expected


def test_add_light():
    doc = ezdxf.new('R2007')
    msp = doc.modelspace()
    light = msp.new_entity('LIGHT', {'name': 'Licht'})
    assert light.dxftype() == 'LIGHT'
    assert light.dxf.name == 'Licht'
