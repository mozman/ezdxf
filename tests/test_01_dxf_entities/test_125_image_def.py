# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.image import ImageDef
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

IMAGEDEF = """0
IMAGEDEF
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
AcDbRasterImageDef
 90
  0
  1
path/filename.jpg
 10
640
 20
480
 11
0.01
 21
0.01
280
  1
281
  0
"""


@pytest.fixture
def entity():
    return ImageDef.from_text(IMAGEDEF)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'IMAGEDEF' in ENTITY_CLASSES


def test_default_init():
    entity = ImageDef()
    assert entity.dxftype() == 'IMAGEDEF'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = ImageDef.new(handle='ABBA', owner='0', dxfattribs={
        'filename': 'image.jpg'
    })
    assert entity.dxf.class_version == 0
    assert entity.dxf.filename == 'image.jpg'
    assert entity.dxf.image_size is None
    assert entity.dxf.pixel_size == (.01, .01)
    assert entity.dxf.loaded == 1
    assert entity.dxf.resolution_units == 0


def test_load_from_text(entity):
    assert entity.dxf.class_version == 0
    assert entity.dxf.filename == 'path/filename.jpg'
    assert entity.dxf.image_size == (640, 480)
    assert entity.dxf.pixel_size == (.01, .01)
    assert entity.dxf.loaded == 1
    assert entity.dxf.resolution_units == 0


def test_write_dxf():
    entity = ImageDef.from_text(IMAGEDEF)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(IMAGEDEF)
    assert result == expected
