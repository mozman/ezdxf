# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import pytest
import math
import ezdxf
from ezdxf.entities.lwpolyline import LWPolyline

POINTS = [(0, 0), (1, 0, 1), (2, 0), (3, 0)]


@pytest.fixture
def lwpolyline():
    entity = LWPolyline.new(dxfattribs={'layer': 'LAY', 'color': 1})
    entity.set_points(POINTS, format='xyb')
    return entity


@pytest.fixture(scope='module')
def msp():
    doc = ezdxf.new()
    return doc.modelspace()


def test_virtual_entities(lwpolyline):
    result = list(lwpolyline.virtual_entities())
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


def test_virtual_entities_elevation(lwpolyline):
    lwpolyline = lwpolyline.translate(1, 1, 1)
    assert lwpolyline.dxf.elevation == 1
    result = list(lwpolyline.virtual_entities())
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


def test_closed_polyline():
    lwpolyline = LWPolyline.new()
    # Create a circle by LWPOLYLINE:
    lwpolyline.set_points([(0, 0, 1), (1, 0, 1)], format='xyb')
    lwpolyline.close(True)

    result = list(lwpolyline.virtual_entities())
    assert len(result) == 2

    e = result[0]
    assert e.dxftype() == 'ARC'
    assert e.dxf.center.isclose((0.5, 0))
    assert e.dxf.radius == 0.5
    assert math.isclose(e.dxf.start_angle, 180, abs_tol=1e-12)
    assert math.isclose(e.dxf.end_angle, 0, abs_tol=1e-12)

    e = result[1]
    assert e.dxftype() == 'ARC'
    assert e.dxf.center.isclose((0.5, 0))
    assert e.dxf.radius == 0.5
    assert math.isclose(e.dxf.start_angle, 0, abs_tol=1e-12)
    assert math.isclose(abs(e.dxf.end_angle), 180, abs_tol=1e-12)


def test_explode_entities(msp):
    lwpolyline = msp.add_lwpolyline(POINTS, format='xyb')
    assert len(msp) == 1
    result = lwpolyline.explode()
    assert lwpolyline.is_alive is False
    assert len(msp) == 3  # LINE, ARC, LINE
    assert len(result) == 3
    assert msp[-1] is result[2]
    assert msp[-2] is result[1]
    assert msp[-3] is result[0]
