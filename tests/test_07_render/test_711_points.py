#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.render import point
from ezdxf.entities import Point
from ezdxf.math.shape import Shape2d

def pnt(location=(0, 0), angle: float = 0):
    return Point.new(dxfattribs={
        'angle': angle,
        'location': location,
    })


def test_dimensionless_point():
    loc = (2, 3)
    p = pnt(location=loc)
    result = point.render(p, pdmode=0)
    line = result[0]
    assert line.dxftype() == 'LINE'
    assert line.dxf.start.isclose(loc)
    assert line.dxf.end.isclose(loc)


def test_none_point():
    p = pnt()
    result = point.render(p, pdmode=1)
    assert len(result) == 0


def test_cross_point():
    p = pnt()
    result = point.render(p, pdmode=2)
    line1, line2 = result
    assert line1.dxf.start == (-1, 0)
    assert line1.dxf.end == (+1, 0)
    assert line2.dxf.start == (0, -1)
    assert line2.dxf.end == (0, +1)


def test_x_cross_point():
    p = pnt()
    result = point.render(p, pdmode=3)
    line1, line2 = result
    assert line1.dxf.start == (-1, -1)
    assert line1.dxf.end == (+1, +1)
    assert line2.dxf.start == (-1, +1)
    assert line2.dxf.end == (+1, -1)


def test_tick_point():
    p = pnt()
    result = point.render(p, pdmode=4)
    line1 = result[0]
    assert line1.dxf.start == (0, 0)
    assert line1.dxf.end == (0, 0.5)


def test_square_point():
    p = pnt()
    result = point.render(p, pdmode=65)
    line1, line2, line3, line4 = result
    lower_left = (-0.5, -0.5)
    assert line1.dxf.start == lower_left
    lower_right = (0.5, -0.5)
    assert line1.dxf.end == lower_right
    assert line2.dxf.start == lower_right
    upper_right = (0.5, 0.5)
    assert line2.dxf.end == upper_right
    assert line3.dxf.start == upper_right
    upper_left = (-0.5, 0.5)
    assert line3.dxf.end == upper_left
    assert line4.dxf.start == upper_left
    assert line4.dxf.end == lower_left


def test_circle_point():
    p = pnt()
    result = point.render(p, pdmode=33)
    circle = result[0]
    assert circle.dxf.center == (0, 0)
    assert circle.dxf.radius == 0.5


def test_rotated_cross_point():
    expected = Shape2d([(-1, 0), (1, 0), (0, -1), (0, 1)])
    expected.rotate(-30)  # count-clockwise rotation
    s1, e1, s2, e2 = expected.vertices

    p = pnt(angle=30)  # clockwise angle!!
    result = point.render(p, pdmode=2)
    line1, line2 = result
    assert line1.dxf.start.isclose(s1)
    assert line1.dxf.end.isclose(e1)
    assert line2.dxf.start.isclose(s2)
    assert line2.dxf.end.isclose(e2)


if __name__ == '__main__':
    pytest.main([__file__])
