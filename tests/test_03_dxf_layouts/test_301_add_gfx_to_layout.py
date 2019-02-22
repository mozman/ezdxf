# Created: 25.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def msp():
    doc = ezdxf.new2()
    return doc.modelspace()


def test_create_line(msp):
    line = msp.add_line((0, 0), (1, 1))
    assert line.dxf.start == (0., 0.)
    assert line.dxf.end == (1., 1.)


def test_create_point(msp):
    point = msp.add_point((1, 2))
    assert point.dxf.location == (1, 2)


def test_create_circle(msp):
    circle = msp.add_circle((3, 3), 5)
    assert circle.dxf.center == (3., 3.)
    assert circle.dxf.radius == 5.


def test_create_arc(msp):
    arc = msp.add_arc((3, 3), 5, 30, 60)
    assert arc.dxf.center == (3., 3.)
    assert arc.dxf.radius == 5.
    assert arc.dxf.start_angle == 30.
    assert arc.dxf.end_angle == 60.


def test_create_trace(msp):
    trace = msp.add_trace([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert trace[0] == (0, 0)
    assert trace.dxf.vtx1 == (1, 0)
    assert trace[2] == (1, 1)
    assert trace.dxf.vtx3 == (0, 1)


def test_create_solid(msp):
    trace = msp.add_solid([(0, 0), (1, 0), (1, 1)])
    assert trace.dxf.vtx0 == (0, 0)
    assert trace[1] == (1, 0)
    assert trace.dxf.vtx2 == (1, 1)
    assert trace[3] == (1, 1)


def test_create_3dface(msp):
    trace = msp.add_3dface([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
    assert trace.dxf.vtx0 == (0, 0, 0)
    assert trace[1] == (1, 0, 0)
    assert trace.dxf.vtx2 == (1, 1, 0)
    assert trace[3] == (0, 1, 0)


def test_create_text(msp):
    text = msp.add_text('text')
    assert text.dxf.text == 'text'


def test_create_shape(msp):
    shape = msp.add_shape("TestShape", (1, 2), 3.0)
    assert shape.dxf.name == "TestShape"
    assert shape.dxf.insert == (1.0, 2.0)
    assert shape.dxf.size == 3
    assert shape.dxf.rotation == 0
    assert shape.dxf.xscale == 1
    assert shape.dxf.oblique == 0
