# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest
import ezdxf
from ezdxf.entities.helix import Helix
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

HELIX = """0
HELIX
5
0
330
0
100
AcDbEntity
8
0
100
AcDbSpline
70
0
71
3
72
0
73
0
74
0
100
AcDbHelix
90
29
91
63
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
0.0
32
1.0
40
1.0
41
1.0
42
1.0
290
1
280
1
"""


@pytest.fixture
def entity():
    return Helix.from_text(HELIX)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'HELIX' in ENTITY_CLASSES


def test_default_init():
    entity = Helix()
    assert entity.dxftype() == 'HELIX'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = Helix.new(handle='ABBA', owner='0', dxfattribs={
        'color': 7,
        'axis_base_point': (1, 2, 3),
        'start_point': (4, 5, 6),
        'axis_vector': (7, 7, 7),
        'radius': 20,
        'turns': 5,
        'handedness': 0,
        'constrain': 2,
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.major_release_number == 29
    assert entity.dxf.maintenance_release_number == 63
    assert entity.dxf.axis_base_point == (1, 2, 3)
    assert entity.dxf.start_point == (4, 5, 6)
    assert entity.dxf.axis_vector == (7, 7, 7)
    assert entity.dxf.radius == 20
    assert entity.dxf.turns == 5
    assert entity.dxf.handedness == 0
    assert entity.dxf.constrain == 2


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.major_release_number == 29
    assert entity.dxf.maintenance_release_number == 63
    assert entity.dxf.axis_base_point == (0, 0, 0)
    assert entity.dxf.start_point == (1, 0, 0)
    assert entity.dxf.axis_vector == (0, 0, 1)
    assert entity.dxf.radius == 1
    assert entity.dxf.turns == 1
    assert entity.dxf.handedness == 1
    assert entity.dxf.constrain == 1


def test_write_dxf():
    entity = Helix.from_text(HELIX)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(HELIX)
    assert result == expected


def test_generic_helix():
    doc = ezdxf.new()
    msp = doc.modelspace()
    helix = msp.new_entity('HELIX', {})
    assert helix.dxftype() == 'HELIX'
    assert helix.dxf.major_release_number == 29
    assert helix.dxf.degree == 3
