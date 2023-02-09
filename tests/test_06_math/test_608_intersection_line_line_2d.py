# Copyright (c) 2020-2022 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import intersection_line_line_2d, Vec2


def vec2(x, y):
    return Vec2((x, y))


def test_intersect_virtual():
    ray1 = (vec2(10, 1), vec2(20, 10))
    ray2 = (vec2(17, -7), vec2(-10, 3))

    point = intersection_line_line_2d(ray1, ray2)
    assert point.isclose(vec2(5.7434, -2.8309), abs_tol=1e-4)


def test_intersect_with_vertical():
    ray1 = (vec2(10, 1), vec2(10, -7))
    ray2 = (vec2(-10, 3), vec2(17, -7))
    point = intersection_line_line_2d(ray1, ray2)
    assert point.x == 10
    assert point.isclose(vec2(10.0, -4.4074), abs_tol=1e-4)


def test_intersect_with_horizontal():
    ray1 = (vec2(-10, 10), vec2(10, 10))
    ray2 = (vec2(-10, 20), vec2(10, 0))
    point = intersection_line_line_2d(ray1, ray2)
    assert point.y == 10
    assert point.isclose(vec2(0.0, 10.0), abs_tol=1e-4)


def test_intersect_with_vertical_and_horizontal():
    ray1 = (vec2(-10, 10), vec2(10, 10))
    ray2 = (vec2(5, 0), vec2(5, 20))
    point = intersection_line_line_2d(ray1, ray2)
    assert point.y == 10
    assert point.x == 5
    assert point.isclose(vec2(5.0, 10.0), abs_tol=1e-4)


def test_intersect_parallel_vertical():
    ray1 = (vec2(10, 1), vec2(10, -7))
    ray2 = (vec2(12, -10), vec2(12, 7))
    assert intersection_line_line_2d(ray1, ray2) is None


def test_intersect_parallel_horizontal():
    ray3 = (vec2(11, 0), vec2(-11, 0))
    ray4 = (vec2(0, 0), vec2(1, 0))
    assert intersection_line_line_2d(ray3, ray4) is None


def test_intersect_normal_vertical():
    ray = (vec2(10, 1), vec2(10, -7))
    ortho = (vec2(0, 3), vec2(10, 3))
    point = intersection_line_line_2d(ray, ortho)
    assert point.isclose(vec2(10, 3))


def test_intersection_by_line_end_points():
    hor = (vec2(1, 1), vec2(3, 1))
    vert = (vec2(2, 1), vec2(2, 5))
    point = intersection_line_line_2d(hor, vert)
    assert point.isclose(vec2(2, 1))

    vert = (vec2(2, 5), vec2(2, 1))
    point = intersection_line_line_2d(hor, vert)
    assert point.isclose(vec2(2, 1))


def test_intersect_real():
    line1 = (vec2(0, 0), vec2(4, 4))
    line2 = (vec2(3, 2), vec2(5, 0))
    point = intersection_line_line_2d(line1, line2, virtual=False)
    assert point is None


def test_intersect_real_colinear():
    line1 = (vec2(0, 0), vec2(4, 4))
    line2 = (vec2(2, 2), vec2(4, 0))  # intersection point, is endpoint of ray2
    point = intersection_line_line_2d(line1, line2, virtual=False)
    assert point.isclose(vec2(2, 2))


@pytest.mark.parametrize(
    "p2", [(4, 0), (0, 4), (4, 4)], ids=["horiz", "vert", "diag"]
)
def test_intersect_coincident_lines(p2):
    line1 = (Vec2(0, 0), Vec2(p2))
    point = intersection_line_line_2d(line1, line1, virtual=False)
    assert point is None


def test_issue_128():
    line1 = (vec2(175.0, 5.0), vec2(175.0, 50.0))
    line2 = (vec2(-10.1231, 30.1235), vec2(300.2344, 30.1235))
    point = intersection_line_line_2d(line1, line2, virtual=False)
    assert point is not None
    assert point.isclose(vec2(175.0, 30.1235))


def test_issue_664():
    from ezdxf.math import ConstructionLine
    p1 = Vec2(16399619.87946683, -199438.8133075837)
    p2 = Vec2(16399700.34999472, -199438.8133075837)
    p3 = Vec2(16399659.76235549, -199423.8133075837)
    p4 = Vec2(16399659.76235549, -199463.8133075837)
    expected = Vec2(16399659.76235549, -199438.8133075837)

    point = intersection_line_line_2d(
        (p1, p2), (p3, p4), virtual=False
    )
    assert point.isclose(expected)

    cl1 = ConstructionLine(p1, p2)
    cl2 = ConstructionLine(p3, p4)
    assert cl1.intersect(cl2).isclose(expected)


if __name__ == "__main__":
    pytest.main([__file__])
