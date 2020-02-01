# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import intersection_line_line_xy, Vec2


def vec2(x, y):
    return Vec2((x, y))


def test_intersect_virtual():
    ray1 = (vec2(10, 1), vec2(20, 10))
    ray2 = (vec2(17, -7), vec2(-10, 3))

    point = intersection_line_line_xy(ray1, ray2)
    assert point.isclose(vec2(5.7434, -2.8309), abs_tol=1e-4)


def test_intersect_with_vertical():
    ray1 = (vec2(10, 1), vec2(10, -7))
    ray2 = (vec2(-10, 3), vec2(17, -7))
    point = intersection_line_line_xy(ray1, ray2)
    assert point.x == 10
    assert point.isclose(vec2(10., -4.4074), abs_tol=1e-4)


def testintersect_with_horizontal():
    ray1 = (vec2(-10, 10), vec2(10, 10))
    ray2 = (vec2(-10, 20), vec2(10, 0))
    point = intersection_line_line_xy(ray1, ray2)
    assert point.y == 10
    assert point.isclose(vec2(0.0, 10.0), abs_tol=1e-4)


def test_intersect_with_vertical_and_horizontal():
    ray1 = (vec2(-10, 10), vec2(10, 10))
    ray2 = (vec2(5, 0), vec2(5, 20))
    point = intersection_line_line_xy(ray1, ray2)
    assert point.y == 10
    assert point.x == 5
    assert point.isclose(vec2(5.0, 10.0), abs_tol=1e-4)


def test_intersect_parallel_vertical():
    ray1 = (vec2(10, 1), vec2(10, -7))
    ray2 = (vec2(12, -10), vec2(12, 7))
    assert intersection_line_line_xy(ray1, ray2) is None


def test_intersect_parallel_horizontal():
    ray3 = (vec2(11, 0), vec2(-11, 0))
    ray4 = (vec2(0, 0), vec2(1, 0))
    assert intersection_line_line_xy(ray3, ray4) is None


def test_intersect_normal_vertical():
    ray = (vec2(10, 1), vec2(10, -7))
    ortho = (vec2(0, 3), vec2(10, 3))
    point = intersection_line_line_xy(ray, ortho)
    assert point.isclose(vec2(10, 3))


def test_intersect_real():
    line1 = (vec2(0, 0), vec2(4, 4))
    line2 = (vec2(3, 2), vec2(5, 0))
    point = intersection_line_line_xy(line1, line2, virtual=False)
    assert point is None


def test_intersect_real_colinear():
    line1 = (vec2(0, 0), vec2(4, 4))
    line2 = (vec2(2, 2), vec2(4, 0))  # intersection point, is endpoint of ray2
    point = intersection_line_line_xy(line1, line2, virtual=False)
    assert point.isclose(vec2(2, 2))


if __name__ == '__main__':
    pytest.main([__file__])
