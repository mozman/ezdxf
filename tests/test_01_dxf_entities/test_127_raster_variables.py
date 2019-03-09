# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.image import RasterVariables
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

RASTERVARIABLES = """0
RASTERVARIABLES
5
0
102
{ACAD_REACTORS
330
0
102
}
330
0
100
AcDbRasterVariables
90
0
70
0
71
1
72
3
"""


@pytest.fixture
def entity():
    return RasterVariables.from_text(RASTERVARIABLES)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'RASTERVARIABLES' in ENTITY_CLASSES


def test_default_init():
    entity = RasterVariables()
    assert entity.dxftype() == 'RASTERVARIABLES'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = RasterVariables.new(handle='ABBA', owner='0', dxfattribs={
    })
    assert entity.dxf.class_version == 0
    assert entity.dxf.frame == 0
    assert entity.dxf.quality == 1
    assert entity.dxf.units == 3


def test_load_from_text(entity):
    assert entity.dxf.class_version == 0
    assert entity.dxf.frame == 0
    assert entity.dxf.quality == 1
    assert entity.dxf.units == 3


def test_write_dxf():
    entity = RasterVariables.from_text(RASTERVARIABLES)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(RASTERVARIABLES)
    assert result == expected
