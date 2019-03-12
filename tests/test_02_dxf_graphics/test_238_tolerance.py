# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entities.tolerance import Tolerance
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

TOLERANCE = """0
TOLERANCE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbFcf
3
Standard
10
0.0
20
0.0
30
0.0
1

11
1.0
21
0.0
31
0.0
"""


@pytest.fixture
def entity():
    return Tolerance.from_text(TOLERANCE)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'TOLERANCE' in ENTITY_CLASSES


def test_default_init():
    entity = Tolerance()
    assert entity.dxftype() == 'TOLERANCE'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = Tolerance.new(handle='ABBA', owner='0', dxfattribs={
        'color': 7,
        'dimstyle': 'EZDXF',
        'insert': (1, 2, 3),
        'extrusion': (4, 5, 6),
        'x_axis_vector': (7, 8, 9),
        'content': 'abcdef',
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.dimstyle == 'EZDXF'
    assert entity.dxf.insert == (1, 2, 3)
    assert entity.dxf.extrusion == (4, 5, 6)
    assert entity.dxf.x_axis_vector == (7, 8, 9)
    assert entity.dxf.content == 'abcdef'


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.dimstyle == 'Standard'
    assert entity.dxf.insert == (0, 0, 0)
    assert entity.dxf.extrusion == (0, 0, 1)  # default value
    assert entity.dxf.x_axis_vector == (1, 0, 0)
    assert entity.dxf.content == ''


def test_write_dxf():
    entity = Tolerance.from_text(TOLERANCE)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(TOLERANCE)
    assert result == expected


def test_add_tolerance():
    doc = ezdxf.new2()
    msp = doc.modelspace()
    light = msp.new_entity('TOLERANCE', {})
    assert light.dxftype() == 'TOLERANCE'
    assert light.dxf.dimstyle == 'Standard'
    assert light.dxf.insert == (0, 0, 0)
    assert light.dxf.content == ''
    assert light.dxf.extrusion == (0, 0, 1)
    assert light.dxf.x_axis_vector == (1, 0, 0)
