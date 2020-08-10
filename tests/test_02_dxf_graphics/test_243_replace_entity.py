# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entities.dxfgfx import add_entity, replace_entity
from ezdxf.entities import Point


@pytest.fixture(scope='module')
def msp():
    return ezdxf.new().modelspace()


@pytest.fixture(scope='module')
def db(msp):
    return msp.entitydb


def test_add_entity(msp, db):
    point = msp.add_point((0, 0))
    new_point = Point.new(dxfattribs={'location': (3, 3)})
    add_entity(new_point, msp)
    assert point in msp
    assert point.dxf.handle in db
    assert new_point in msp
    assert new_point.dxf.handle in db
    assert point.dxf.handle != new_point.dxf.handle


def test_replace_entity(msp, db):
    point = msp.add_point((0, 0))
    handle = point.dxf.handle

    new_point = Point.new(dxfattribs={'location': (3, 3)})
    replace_entity(point, new_point, msp)
    assert point.is_alive is False
    assert new_point in msp
    assert new_point.dxf.handle in db
    assert new_point.dxf.handle == handle


def test_replace_entity_without_layout(msp, db):
    point = Point.new(dxfattribs={'location': (3, 3)})
    db.add(point)
    handle = point.dxf.handle

    assert point not in msp
    assert point.dxf.handle in db

    new_point = Point.new(dxfattribs={'location': (3, 3)})
    replace_entity(point, new_point, msp)
    assert point.is_alive is False
    assert new_point not in msp
    assert new_point.dxf.handle in db
    assert new_point.dxf.handle == handle


def test_convert_circle_to_ellipse(msp, db):
    circle = msp.add_circle(center=(3, 3), radius=2)
    ellipse = circle.to_ellipse(msp, replace=False)
    assert circle.dxf.handle in db
    assert ellipse.dxftype() == 'ELLIPSE'
    assert ellipse.dxf.handle in db
    assert circle in msp
    assert ellipse in msp


def test_replace_circle_by_ellipse(msp, db):
    circle = msp.add_circle(center=(3, 3), radius=2)
    circle_handle = circle.dxf.handle
    ellipse = circle.to_ellipse(msp, replace=True)
    assert circle.is_alive is False
    assert ellipse.dxftype() == 'ELLIPSE'
    assert ellipse.dxf.handle in db
    assert ellipse.dxf.handle == circle_handle
    assert ellipse in msp


def test_convert_circle_to_spline(msp, db):
    circle = msp.add_circle(center=(3, 3), radius=2)
    spline = circle.to_spline(msp, replace=False)
    assert circle.dxf.handle in db
    assert spline.dxftype() == 'SPLINE'
    assert spline.dxf.handle in db
    assert circle in msp
    assert spline in msp


def test_replace_circle_by_spline(msp, db):
    circle = msp.add_circle(center=(3, 3), radius=2)
    circle_handle = circle.dxf.handle
    spline = circle.to_spline(msp, replace=True)
    assert circle.is_alive is False
    assert spline.dxftype() == 'SPLINE'
    assert spline.dxf.handle in db
    assert spline.dxf.handle == circle_handle
    assert spline in msp


def test_convert_ellipse_to_spline(msp, db):
    ellipse = msp.add_ellipse(center=(3, 3), major_axis=(2, 0), ratio=0.5)
    spline = ellipse.to_spline(msp, replace=False)
    assert ellipse.dxf.handle in db
    assert spline.dxftype() == 'SPLINE'
    assert spline.dxf.handle in db
    assert ellipse in msp
    assert spline in msp


def test_replace_ellipse_by_spline(msp, db):
    ellipse = msp.add_ellipse(center=(3, 3), major_axis=(2, 0), ratio=0.5)
    ellipse_handle = ellipse.dxf.handle
    spline = ellipse.to_spline(msp, replace=True)
    assert ellipse.is_alive is False
    assert spline.dxftype() == 'SPLINE'
    assert spline.dxf.handle in db
    assert spline.dxf.handle == ellipse_handle
    assert spline in msp


if __name__ == '__main__':
    pytest.main([__file__])
