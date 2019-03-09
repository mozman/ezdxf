# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.image import ImageDefReactor
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

IMAGEDEF_REACTOR = """0
IMAGEDEF_REACTOR
5
0
330
0
100
AcDbRasterImageDefReactor
90
2
330
0
"""


@pytest.fixture
def entity():
    return ImageDefReactor.from_text(IMAGEDEF_REACTOR)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'IMAGEDEF_REACTOR' in ENTITY_CLASSES


def test_default_init():
    entity = ImageDefReactor()
    assert entity.dxftype() == 'IMAGEDEF_REACTOR'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = ImageDefReactor.new(handle='ABBA', owner='0', dxfattribs={
        'image_handle': 'FEFE'
    })
    assert entity.dxf.class_version == 2
    assert entity.dxf.image_handle == 'FEFE'


def test_load_from_text(entity):
    assert entity.dxf.class_version == 2
    assert entity.dxf.image_handle == '0'


def test_write_dxf():
    entity = ImageDefReactor.from_text(IMAGEDEF_REACTOR)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(IMAGEDEF_REACTOR)
    assert result == expected
