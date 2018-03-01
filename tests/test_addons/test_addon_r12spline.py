# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.addons import R12Spline


CONTROL_POINTS = [(8.55, 2.96), (8.55, -.03), (2.75, -.03), (2.76, 3.05), (4.29, 1.78), (6.79, 3.05)]


@pytest.fixture(scope='module')
def msp():
    return ezdxf.new('R12').modelspace()


def test_r12_quadratic_spline(msp):
    spline = R12Spline(CONTROL_POINTS, degree=2, closed=False)
    polyline = spline.render(msp, segments=40)
    assert polyline.dxftype() == 'POLYLINE'
    assert polyline.dxf.layer == '0'
    assert len(polyline) == 41 + len(CONTROL_POINTS)
    assert polyline.is_closed is False


def test_r12_cubic_spline(msp):
    spline = R12Spline(CONTROL_POINTS, degree=3, closed=False)
    polyline = spline.render(msp, segments=40)
    assert polyline.dxftype() == 'POLYLINE'
    assert polyline.dxf.layer == '0'
    assert len(polyline) == 41 + len(CONTROL_POINTS)
    assert polyline.is_closed is False


def test_r12_cubic_spline_closed(msp):
    spline = R12Spline(CONTROL_POINTS, degree=3, closed=True)
    polyline = spline.render(msp, segments=40)
    assert polyline.dxftype() == 'POLYLINE'
    assert polyline.dxf.layer == '0'
    assert len(polyline) == 41 + len(CONTROL_POINTS)
    assert polyline.is_closed is True




