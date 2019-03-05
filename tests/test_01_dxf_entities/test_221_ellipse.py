# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest
import math

from ezdxf.entities.ellipse import Ellipse
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text


ELLIPSE = """0
ELLIPSE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbEllipse
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
40
1.0
41
0.0
42
6.283185307179586
"""

@pytest.fixture
def entity():
    return Ellipse.from_text(ELLIPSE)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'ELLIPSE' in ENTITY_CLASSES


def test_default_init():
    dxfclass = Ellipse()
    assert dxfclass.dxftype() == 'ELLIPSE'
    assert dxfclass.dxf.handle is None
    assert dxfclass.dxf.owner is None


def test_default_new():
    entity = Ellipse.new(handle='ABBA', owner='0', dxfattribs={
        'color': 7,
        'ratio': 2,
        'center': (1, 2, 3),
        'major_axis': (4, 5, 6),
        'start_param': 10,
        'end_param': 20,
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.center == (1, 2, 3)
    assert entity.dxf.major_axis == (4, 5, 6)
    assert entity.dxf.ratio == 2
    assert entity.dxf.start_param == 10
    assert entity.dxf.end_param == 20


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.center == (0, 0, 0)
    assert entity.dxf.major_axis == (1, 0, 0)
    assert entity.dxf.ratio == 1
    assert entity.dxf.start_param == 0
    assert entity.dxf.end_param == math.pi*2


def test_write_dxf():
    entity = Ellipse.from_text(ELLIPSE)
    collector = TagCollector()
    entity.export_dxf(collector)
    result = collector.tags
    expected = basic_tags_from_text(ELLIPSE)
    assert result == expected


