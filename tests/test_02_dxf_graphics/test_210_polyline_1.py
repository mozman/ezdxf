# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest
import ezdxf

from ezdxf.entities.polyline import Polyline
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Vector

TEST_CLASS = Polyline
TEST_TYPE = 'POLYLINE'

ENTITY_R12 = """0
POLYLINE
5
0
8
0
66
1
10
0.0
20
0.0
30
0.0
70
0
"""

ENTITY_R2000 = """0
POLYLINE
5
0
330
0
100
AcDbEntity
8
0
100
AcDb2dPolyline
66
1
10
0.0
20
0.0
30
0.0
70
0
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
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == 'BYLAYER'
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'


def test_polyline_3d():
    polyline = Polyline.new(dxfattribs={'flags': Polyline.POLYLINE_3D})
    collector = TagCollector(dxfversion='R2000', optional=True)
    polyline.export_dxf(collector)
    assert (100, 'AcDb3dPolyline') == collector.tags[5]


def test_poly_face_mesh():
    polyline = Polyline.new(dxfattribs={'flags': Polyline.POLYFACE})
    collector = TagCollector(dxfversion='R2000', optional=True)
    polyline.export_dxf(collector)
    assert (100, 'AcDbPolyFaceMesh') == collector.tags[5]


def test_polygon_mesh():
    polyline = Polyline.new(dxfattribs={'flags': Polyline.POLYMESH})
    collector = TagCollector(dxfversion='R2000', optional=True)
    polyline.export_dxf(collector)
    assert (100, 'AcDbPolygonMesh') == collector.tags[5]


def test_copy_polyline():
    doc = ezdxf.new()
    msp = doc.modelspace()
    polyline = msp.add_polyline2d([(1, 2), (7, 8), (4, 3)])
    assert isinstance(polyline, Polyline)
    assert len(polyline) == 3

    copy = polyline.copy()
    assert isinstance(polyline, Polyline)
    assert len(copy) == 3
    assert list(polyline.points()) == list(copy.points())
    assert polyline.vertices is not copy.vertices
    assert polyline.vertices[0] is not copy.vertices[0]
    copy.append_vertices([(9, 9)])
    assert len(polyline) == 3
    assert len(copy) == 4

    assert copy not in msp, 'is not assigned to modelspace'
    # but only one polyline is stored
    assert len(msp) == 1
    msp.add_entity(copy)
    assert len(msp) == 2
    assert polyline.dxf.handle != copy.dxf.handle
    assert polyline.dxf.owner == copy.dxf.owner
    for vertex in copy.vertices:
        assert vertex.dxf.owner == copy.dxf.owner, 'vertices should have same owner as polyline'


@pytest.mark.parametrize("txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    polyline = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    polyline.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    polyline.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


def test_polyline2d_transform_interface():
    pline = Polyline()
    pline.append_vertices([(0, 0, 0), (2, 0, 0), (1, 1, 0)])
    pline.translate(1, 1, 1)
    vertices = list(v.dxf.location for v in pline.vertices)
    assert pline.is_2d_polyline is True
    assert vertices[0] == (1, 1, 1)
    assert vertices[1] == (3, 1, 1)
    assert vertices[2] == (2, 2, 1)
    assert pline.dxf.elevation == (0, 0, 1)
    assert Vector(0, 0, 1).isclose(pline.dxf.extrusion)


def test_polyline3d_transform_interface():
    pline = Polyline.new(dxfattribs={'flags': 8})
    pline.append_vertices([(0, 0, 0), (2, 0, 0), (1, 1, 0)])
    pline.translate(1, 1, 1)
    vertices = list(v.dxf.location for v in pline.vertices)
    assert pline.is_3d_polyline is True
    assert vertices[0] == (1, 1, 1)
    assert vertices[1] == (3, 1, 1)
    assert vertices[2] == (2, 2, 1)


def test_2d_polyline_has_default_width():
    assert Polyline().has_width is False
    assert Polyline.new(dxfattribs={'default_start_width': .1}).has_width is True
    assert Polyline.new(dxfattribs={'default_end_width': .1}).has_width is True


def test_2d_polyline_has_any_start_width():
    pline = Polyline()
    pline.append_formatted_vertices([(0, 0, .1)], format='xys')
    assert pline.has_width is True


def test_2d_polyline_has_any_end_width():
    pline = Polyline()
    pline.append_formatted_vertices([(0, 0, .1)], format='xye')
    assert pline.has_width is True


def test_2d_polyline_has_any_arc():
    pline = Polyline()
    assert pline.has_arc is False
    pline.append_formatted_vertices([(0, 0, 1.0)], format='xyb')
    assert pline.has_arc is True
