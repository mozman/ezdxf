# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import pytest
import math
import ezdxf
from ezdxf.layouts import VirtualLayout

POINTS = [(0, 0), (1, 0, 1), (2, 0), (3, 0)]


@pytest.fixture(scope='module')
def msp():
    doc = ezdxf.new()
    return doc.modelspace()


@pytest.fixture
def polyline2d(msp):
    return msp.add_polyline2d(points=POINTS, format='xyb', dxfattribs={'layer': 'LAY', 'color': 1})


def test_polyline2d_virtual_entities(polyline2d):
    result = list(polyline2d.virtual_entities())
    assert len(result) == 3

    e = result[0]
    assert e.dxftype() == 'LINE'
    assert e.dxf.layer == 'LAY'
    assert e.dxf.color == 1
    assert e.dxf.start == (0, 0)
    assert e.dxf.end == (1, 0)

    e = result[1]
    assert e.dxftype() == 'ARC'
    assert e.dxf.layer == 'LAY'
    assert e.dxf.color == 1
    assert e.dxf.center == (1.5, 0)
    assert e.dxf.radius == 0.5
    assert math.isclose(e.dxf.start_angle, 180, abs_tol=1e-12)
    assert math.isclose(e.dxf.end_angle, 0, abs_tol=1e-12)

    assert e.start_point.isclose((1, 0))
    assert e.end_point.isclose((2, 0))

    e = result[2]
    assert e.dxftype() == 'LINE'
    assert e.dxf.layer == 'LAY'
    assert e.dxf.color == 1
    assert e.dxf.start == (2, 0)
    assert e.dxf.end == (3, 0)


def test_polyline2d_elevation(polyline2d):
    polyline = polyline2d.translate(1, 1, 1)
    assert polyline.dxf.elevation == (0, 0, 1)
    result = list(polyline.virtual_entities())
    assert len(result) == 3
    e = result[0]
    assert e.dxftype() == 'LINE'
    assert e.dxf.start == (1, 1, 1)
    assert e.dxf.end == (2, 1, 1)

    e = result[1]
    assert e.dxftype() == 'ARC'
    assert e.dxf.center == (2.5, 1, 1)
    assert e.dxf.radius == 0.5
    assert math.isclose(e.dxf.start_angle, 180, abs_tol=1e-12)
    assert math.isclose(e.dxf.end_angle, 0, abs_tol=1e-12)

    assert e.start_point.isclose((2, 1, 1))
    assert e.end_point.isclose((3, 1, 1))

    e = result[2]
    assert e.dxftype() == 'LINE'
    assert e.dxf.start == (3, 1, 1)
    assert e.dxf.end == (4, 1, 1)


def test_polyline2d_closed():
    # Create a circle by 2D POLYLINE:
    msp = VirtualLayout()
    polyline = msp.add_polyline2d(points=[(0, 0, 1), (1, 0, 1)], format='xyb')
    polyline.close(True)

    result = list(polyline.virtual_entities())
    assert len(result) == 2

    e = result[0]
    assert e.dxftype() == 'ARC'
    assert e.dxf.center == (0.5, 0)
    assert e.dxf.radius == 0.5
    assert math.isclose(e.dxf.start_angle, 180, abs_tol=1e-12)
    assert math.isclose(e.dxf.end_angle, 0, abs_tol=1e-12)

    e = result[1]
    assert e.dxftype() == 'ARC'
    assert e.dxf.center == (0.5, 0)
    assert e.dxf.radius == 0.5
    assert math.isclose(e.dxf.start_angle, 0, abs_tol=1e-12)
    assert math.isclose(abs(e.dxf.end_angle), 180, abs_tol=1e-12)


def test_polyline2d_explode(msp):
    # explode does not work with VirtualLayout()
    polyline = msp.add_polyline2d(POINTS, format='xyb')
    count = len(msp)
    result = polyline.explode()
    assert polyline.is_alive is False
    assert len(msp) == count + 2  # LINE, ARC, LINE
    assert msp[-1] is result[2]
    assert msp[-2] is result[1]
    assert msp[-3] is result[0]


def test_polyline3d_virtual_entities():
    msp = VirtualLayout()
    polyline3d = msp.add_polyline3d([(0, 0, 0), (1, 0, 0), (2, 2, 2)])
    result = list(polyline3d.virtual_entities())
    assert len(result) == 2
    line = result[0]
    assert line.dxftype() == 'LINE'
    assert line.dxf.start == (0, 0, 0)
    assert line.dxf.end == (1, 0, 0)
    line = result[1]
    assert line.dxftype() == 'LINE'
    assert line.dxf.start == (1, 0, 0)
    assert line.dxf.end == (2, 2, 2)


def test_polyline3d_closed():
    msp = VirtualLayout()
    polyline3d = msp.add_polyline3d([(0, 0, 0), (1, 0, 0), (2, 2, 2)], close=True)
    assert polyline3d.is_closed is True
    result = list(polyline3d.virtual_entities())
    assert len(result) == 3
    # The closing element is the first LINE entity.
    # This is an implementation detail and can change in the future!
    line = result[0]
    assert line.dxftype() == 'LINE'
    assert line.dxf.start == (2, 2, 2)
    assert line.dxf.end == (0, 0, 0)


def test_polyline3d_explode(msp):
    # explode does not work with VirtualLayout()
    polyline3d = msp.add_polyline3d([(0, 0, 0), (1, 0, 0), (2, 2, 2)])
    count = len(msp)
    result = polyline3d.explode()
    assert polyline3d.is_alive is False
    assert len(msp) == count + 1  # LINE, LINE
    assert msp[-1] is result[1]
    assert msp[-2] is result[0]


@pytest.fixture()
def polymesh():
    msp = VirtualLayout()
    polymesh = msp.add_polymesh((3, 3))
    for m in range(3):
        for n in range(3):
            polymesh.set_mesh_vertex((m, n), (m, n))
    return polymesh


def test_polymesh_virtual_entities(polymesh):
    result = list(polymesh.virtual_entities())
    assert len(result) == 4
    assert result[0].dxftype() == '3DFACE'
    # 1. columns, 2. rows
    # col=0, row=0
    assert result[0].dxf.vtx0 == (0, 0, 0)
    assert result[0].dxf.vtx2 == (1, 1, 0)
    # col=0, row=1
    assert result[1].dxf.vtx0 == (0, 1, 0)
    assert result[1].dxf.vtx2 == (1, 2, 0)
    # col=1, row=0
    assert result[2].dxf.vtx0 == (1, 0, 0)
    assert result[2].dxf.vtx2 == (2, 1, 0)
    # col=1, row=1
    assert result[3].dxf.vtx0 == (1, 1, 0)
    assert result[3].dxf.vtx2 == (2, 2, 0)


def test_closed_polymesh(polymesh):
    polymesh.close(m_close=True, n_close=True)
    assert polymesh.is_m_closed is True
    assert polymesh.is_n_closed is True
    result = list(polymesh.virtual_entities())
    assert len(result) == 9


def test_polyface_virtual_entities():
    from ezdxf.render.forms import cube

    msp = VirtualLayout()
    polyface = cube().render_polyface(msp)
    result = list(polyface.virtual_entities())

    assert len(result) == 6
    assert result[0].dxftype() == '3DFACE'
    vertices = set()
    for face in result:
        for vertex in face:
            vertices.add(vertex)
    assert len(vertices) == 8
    assert (-0.5, -0.5, -0.5) in vertices
    assert (0.5, 0.5, 0.5) in vertices
