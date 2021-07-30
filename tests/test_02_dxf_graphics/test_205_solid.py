# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
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

ELEVATION = """0
SOLID
5
0
8
0
38
2.0
10
0.0
20
0.0
11
0.0
21
0.0
12
0.0
22
0.0
13
0.0
23
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
    assert entity.dxf.vtx3.x == 1, 'is not Vec3 compatible'
    assert entity.dxf.vtx3.y == 2, 'is not Vec3 compatible'
    assert entity.dxf.vtx3.z == 3, 'is not Vec3 compatible'
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr('extrusion') is False, 'just the default value'


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.vtx3 == (0, 0, 0)


@pytest.mark.parametrize("txt,ver",
                         [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    solid = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    solid.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    solid.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


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

    # Elevation tag should not be written by default
    assert any(tag[0] == 38 for tag in collector.tags) is False


def test_3dface():
    face = Face3d()
    face.dxf.invisible = 2 + 8
    assert face.is_invisible_edge(0) is False
    assert face.is_invisible_edge(1) is True
    assert face.is_invisible_edge(2) is False
    assert face.is_invisible_edge(3) is True  # accessible even when triangle

    assert face.get_edges_visibility() == [True, False, True]
    assert face.is_triangle
    assert face.num_vertices == 3

    face.dxf.vtx3 = (1, 2, 3)
    assert face.get_edges_visibility() == [True, False, True, False]
    assert not face.is_triangle
    assert face.num_vertices == 4

    face.dxf.invisible = 0
    face.set_edge_visibility(3, False)
    assert face.dxf.invisible == 8
    face.set_edge_visibility(1, False)
    assert face.dxf.invisible == 10
    face.set_edge_visibility(3, True)
    assert face.dxf.invisible == 2

    collector = TagCollector(dxfversion=DXF2000)
    face.export_dxf(collector)
    assert collector.tags[0] == (0, '3DFACE')
    assert collector.tags[5] == (100, 'AcDbFace')


def test_solid_translate():
    solid = Solid()
    solid.dxf.vtx1 = (3, 3, 0)
    solid.translate(1, 1, 0)
    assert solid.dxf.vtx1 == (4, 4, 0)


def test_trace_translate():
    face = Face3d()
    face.dxf.vtx1 = (3, 3, 0)
    face.translate(1, 1, 0)
    assert face.dxf.vtx1 == (4, 4, 0)


def test_solid_reorder_quad_ocs_vertices():
    solid = Solid()
    for index, vertex in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)]):
        solid[index] = vertex

    # reorder weird vertex order:
    assert solid.vertices() == [(0, 0), (1, 0), (1, 1), (0, 1)]


def test_solid_triangle_ocs_vertices():
    solid = Solid()
    for index, vertex in enumerate([(0, 0), (1, 0), (0, 1), (0, 1)]):
        solid[index] = vertex
    assert solid.vertices() == [(0, 0), (1, 0), (0, 1)]


def test_solid_close_triangle_ocs_vertices():
    solid = Solid()
    for index, vertex in enumerate([(0, 0), (1, 0), (0, 1), (0, 1)]):
        solid[index] = vertex
    assert solid.vertices(close=True) == [(0, 0), (1, 0), (0, 1), (0, 0)]


def test_solid_close_quad_ocs_vertices():
    solid = Solid()
    for index, vertex in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        solid[index] = vertex
    assert solid.vertices(close=True) == [
        (0, 0), (1, 0), (0, 1), (1, 1), (0, 0)]


def test_solid_wcs_vertices():
    solid = Solid()
    for index, vertex in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)]):
        solid[index] = vertex
    # reorder weird vertex order:
    assert solid.wcs_vertices() == [(0, 0), (1, 0), (1, 1), (0, 1)]


def test_3dface_quad_vertices():
    face = Face3d()
    for index, vertex in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        face[index] = vertex
    assert not face.is_triangle
    assert face.get_edges_visibility() == [True, True, True, True]
    assert face.num_vertices == 4
    # no weird vertex order:
    assert face.wcs_vertices() == [(0, 0), (1, 0), (1, 1), (0, 1)]
    assert face.wcs_vertices(close=True) == [(0, 0), (1, 0), (1, 1), (0, 1),
                                             (0, 0)]


def test_3dface_triangle_vertices():
    face = Face3d()
    for index, vertex in enumerate([(0, 0), (1, 0), (1, 1), (1, 1)]):
        face[index] = vertex
    assert face.is_triangle
    assert face.get_edges_visibility() == [True, True, True]
    assert face.num_vertices == 3
    assert face.wcs_vertices() == [(0, 0), (1, 0), (1, 1)]
    assert face.wcs_vertices(close=True) == [(0, 0), (1, 0), (1, 1), (0, 0)]


def test_elevation_group_code_support():
    solid = Solid.from_text(ELEVATION)
    # elevation data is copied to z-axis of vertices:
    assert solid.dxf.hasattr('elevation') is False
    vertices = solid.vertices()
    assert vertices[0] == (0, 0, 2)


def test_do_not_write_elevation_group_code():
    solid = Solid.from_text(ELEVATION)
    collector = TagCollector(dxfversion=DXF12)
    solid.export_dxf(collector)
    # Elevation tag should be written:
    assert any(tag[0] == 38 for tag in collector.tags) is False
