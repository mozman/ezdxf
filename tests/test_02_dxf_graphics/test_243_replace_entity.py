# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entities.dxfgfx import add_entity, replace_entity
from ezdxf.entities import Point


@pytest.fixture(scope='module')
def msp():
    return ezdxf.new().modelspace()


def test_add_entity(msp):
    point = msp.add_point((0, 0))
    new_point = Point.new(dxfattribs={'location': (3, 3)}, doc=point.doc)
    add_entity(point, new_point)
    assert point in msp
    assert point.dxf.handle in point.entitydb
    assert new_point in msp
    assert new_point.dxf.handle in new_point.entitydb
    assert point.dxf.handle != new_point.dxf.handle


def test_add_entity_without_layout(msp):
    point = Point.new(dxfattribs={'location': (3, 3)}, doc=msp.doc)
    msp.entitydb.add(point)
    assert point not in msp
    assert point.dxf.handle in point.entitydb

    new_point = Point.new(dxfattribs={'location': (3, 3)}, doc=msp.doc)
    add_entity(point, new_point)
    assert new_point not in msp
    assert new_point.dxf.handle in new_point.entitydb
    assert point.dxf.handle != new_point.dxf.handle


def test_replace_entity(msp):
    point = msp.add_point((0, 0))
    handle = point.dxf.handle

    new_point = Point.new(dxfattribs={'location': (3, 3)}, doc=point.doc)
    replace_entity(point, new_point)
    assert point.is_alive is False
    assert new_point in msp
    assert new_point.dxf.handle in new_point.entitydb
    assert new_point.dxf.handle == handle


def test_replace_entity_without_layout(msp):
    point = Point.new(dxfattribs={'location': (3, 3)}, doc=msp.doc)
    msp.entitydb.add(point)
    handle = point.dxf.handle

    assert point not in msp
    assert point.dxf.handle in point.entitydb

    new_point = Point.new(dxfattribs={'location': (3, 3)}, doc=msp.doc)
    replace_entity(point, new_point)
    assert point.is_alive is False
    assert new_point not in msp
    assert new_point.dxf.handle in new_point.entitydb
    assert new_point.dxf.handle == handle


def test_convert_circle_to_ellipse(msp):
    circle = msp.add_circle(center=(3, 3), radius=2)
    ellipse = circle.to_ellipse(replace=False)
    assert circle.dxf.handle in circle.entitydb
    assert ellipse.dxftype() == 'ELLIPSE'
    assert ellipse.dxf.handle in ellipse.entitydb
    assert circle in msp
    assert ellipse in msp


def test_replace_circle_by_ellipse(msp):
    circle = msp.add_circle(center=(3, 3), radius=2)
    circle_handle = circle.dxf.handle
    ellipse = circle.to_ellipse(replace=True)
    assert circle.is_alive is False
    assert ellipse.dxftype() == 'ELLIPSE'
    assert ellipse.dxf.handle in ellipse.entitydb
    assert ellipse.dxf.handle == circle_handle
    assert ellipse in msp


def test_convert_circle_to_spline(msp):
    circle = msp.add_circle(center=(3, 3), radius=2)
    spline = circle.to_spline(replace=False)
    assert circle.dxf.handle in circle.entitydb
    assert spline.dxftype() == 'SPLINE'
    assert spline.dxf.handle in spline.entitydb
    assert circle in msp
    assert spline in msp


def test_replace_circle_by_spline(msp):
    circle = msp.add_circle(center=(3, 3), radius=2)
    circle_handle = circle.dxf.handle
    spline = circle.to_spline(replace=True)
    assert circle.is_alive is False
    assert spline.dxftype() == 'SPLINE'
    assert spline.dxf.handle in spline.entitydb
    assert spline.dxf.handle == circle_handle
    assert spline in msp


def test_convert_ellipse_to_spline(msp):
    ellipse = msp.add_ellipse(center=(3, 3), major_axis=(2, 0), ratio=0.5)
    spline = ellipse.to_spline(replace=False)
    assert ellipse.dxf.handle in ellipse.entitydb
    assert spline.dxftype() == 'SPLINE'
    assert spline.dxf.handle in spline.entitydb
    assert ellipse in msp
    assert spline in msp


def test_replace_ellipse_by_spline(msp):
    ellipse = msp.add_ellipse(center=(3, 3), major_axis=(2, 0), ratio=0.5)
    ellipse_handle = ellipse.dxf.handle
    spline = ellipse.to_spline(replace=True)
    assert ellipse.is_alive is False
    assert spline.dxftype() == 'SPLINE'
    assert spline.dxf.handle in spline.entitydb
    assert spline.dxf.handle == ellipse_handle
    assert spline in msp


if __name__ == '__main__':
    pytest.main([__file__])

