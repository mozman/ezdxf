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
