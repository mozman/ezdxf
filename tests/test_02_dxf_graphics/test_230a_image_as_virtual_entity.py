# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-02-15
from typing import cast
import pytest

from ezdxf.entities.image import Image
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

IMAGE = """0
IMAGE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbRasterImage
90
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
0.0
31
0.0
12
0.0
22
1.0
32
0.0
13
640
23
320
340
0
70
3
280
0
281
50
282
50
283
0
360
0
71
1
91
2
"""


@pytest.fixture
def entity():
    return Image.from_text(IMAGE)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'IMAGE' in ENTITY_CLASSES


def test_default_init():
    entity = Image()
    assert entity.dxftype() == 'IMAGE'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = Image.new(handle='ABBA', owner='0', dxfattribs={
        'image_size': (640, 200)
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.insert is None  # set by add_image()
    assert entity.dxf.u_pixel is None  # set by add_image()
    assert entity.dxf.v_pixel is None  # set by add_image()
    assert entity.dxf.class_version == 0
    assert entity.dxf.image_size == (640, 200)
    assert entity.dxf.image_def_handle is None  # set by add_image()
    assert entity.dxf.flags == 3
    assert entity.dxf.clipping == 0
    assert entity.dxf.brightness == 50
    assert entity.dxf.contrast == 50
    assert entity.dxf.fade == 0
    assert entity.dxf.image_def_reactor_handle is None  # set by add_image()
    assert entity.dxf.clipping_boundary_type == 1
    assert entity.dxf.clip_mode == 0
    assert entity.boundary_path[0] == (-0.5, -0.5)
    assert entity.boundary_path[1] == (639.5, 199.5)


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.insert == (0, 0, 0)
    assert entity.dxf.u_pixel == (1, 0, 0)
    assert entity.dxf.v_pixel == (0, 1, 0)
    assert entity.dxf.class_version == 0
    assert entity.dxf.image_size == (640, 320)
    assert entity.dxf.image_def_handle == '0'
    assert entity.dxf.flags == 3
    assert entity.dxf.clipping == 0
    assert entity.dxf.brightness == 50
    assert entity.dxf.contrast == 50
    assert entity.dxf.fade == 0
    assert entity.dxf.image_def_reactor_handle == '0'
    assert entity.dxf.clipping_boundary_type == 1
    assert entity.dxf.clip_mode == 0
    assert entity.boundary_path[0] == (-0.5, -0.5)
    assert entity.boundary_path[1] == (639.5, 319.5)


def test_image_write_dxf():
    entity = Image.from_text(IMAGE)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(EXPECTED)
    assert result == expected


EXPECTED = """0
IMAGE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbRasterImage
90
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
0.0
31
0.0
12
0.0
22
1.0
32
0.0
13
640
23
320
340
0
70
3
280
0
281
50
282
50
283
0
360
0
71
1
91
2
14
-0.5
24
-0.5
14
639.5
24
319.5
290
0
"""
