# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.solid import Solid, Trace, Face3d
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

TEST_CLASS = Solid
TEST_TYPE = 'SOLID'

ENTITY_R12 = """0
SOLID
5
0
8
0
10
0.0
20
0.0
30
0.0
11
0.0
21
0.0
31
0.0
12
0.0
22
0.0
32
0.0
13
0.0
23
0.0
33
0.0
"""

ENTITY_R2000 = """0
SOLID
5
0
330
0
100
AcDbEntity
8
0
100
AcDbTrace
10
0.0
20
0.0
30
0.0
11
0.0
21
0.0
31
0.0
12
0.0
22
0.0
32
0.0
13
0.0
23
0.0
33
0.0
"""


@pytest.fixture(params=[ENTITY_R12, ENTITY_R2000])
def entity(request):
    return TEST_CLASS.from_text(request.param)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert TEST_TYPE in ENTITY_CLASSES


def test_default_init():
    entity = TEST_CLASS()
    assert entity.dxftype() == TEST_TYPE


def test_default_new():
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'vtx3': (1, 2, 3),
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == 'BYLAYER'
    assert entity.dxf.vtx3 == (1, 2, 3)
    assert entity.dxf.vtx3.x == 1, 'is not Vector compatible'
    assert entity.dxf.vtx3.y == 2, 'is not Vector compatible'
    assert entity.dxf.vtx3.z == 3, 'is not Vector compatible'
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr('extrusion') is False, 'just the default value'


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.vtx3 == (0, 0, 0)


def test_write_dxf_2000():
    expected = basic_tags_from_text(ENTITY_R2000)
    line = TEST_CLASS.from_text(ENTITY_R2000)
    collector = TagCollector(dxfversion=DXF2000)
    line.export_dxf(collector)
    assert collector.tags == expected


def test_write_dxf_r12():
    expected = basic_tags_from_text(ENTITY_R12)
    line = TEST_CLASS.from_text(ENTITY_R12)
    line.dxf.shadow_mode = 1  # set value of later DXF version, ignore at export
    assert line.dxf.shadow_mode == 1

    collector = TagCollector(dxfversion=DXF12)
    line.export_dxf(collector)
    assert collector.tags == expected


def test_trace():
    trace = Trace()
    trace[0] = (1, 2, 3)
    trace[1] = (4, 5, 6)
    trace[2] = (7, 8, 9)
    trace[3] = (5, 1, 0)
    assert trace[0] == (1, 2, 3)
    assert trace[1] == (4, 5, 6)
    assert trace[2] == (7, 8, 9)
    assert trace[3] == (5, 1, 0)
    assert trace.dxf.vtx0 == (1, 2, 3)
    assert trace.dxf.vtx1 == (4, 5, 6)
    assert trace.dxf.vtx2 == (7, 8, 9)
    assert trace.dxf.vtx3 == (5, 1, 0)

    collector = TagCollector(dxfversion=DXF2000)
    trace.export_dxf(collector)
    assert collector.tags[0] == (0, 'TRACE')
    assert collector.tags[5] == (100, 'AcDbTrace')


def test_3dface():
    face = Face3d()
    face.dxf.invisible = 2+8
    assert face.is_invisible_edge(0) is False
    assert face.is_invisible_edge(1) is True
    assert face.is_invisible_edge(2) is False
    assert face.is_invisible_edge(3) is True

    face.dxf.invisible = 0
    face.set_edge_visibilty(3, True)
    assert face.dxf.invisible == 8
    face.set_edge_visibilty(1, True)
    assert face.dxf.invisible == 10
    face.set_edge_visibilty(3, False)
    assert face.dxf.invisible == 2

    collector = TagCollector(dxfversion=DXF2000)
    face.export_dxf(collector)
    assert collector.tags[0] == (0, '3DFACE')
    assert collector.tags[5] == (100, 'AcDbFace')
