# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
# pylint: disable=redefined-outer-name  # pytest-fixtures!
from __future__ import annotations
import pytest

from ezdxf.math import Vec2
from ezdxf.math.clipping import ConcaveClippingPolygon2d as CCP

#   0123456
# 8 .......
# 7 .7---6.
# 6 .|...|.
# 5 .|.4-5.
# 4 .|.|...
# 3 .|.3-2.
# 2 .|...|.
# 1 .0---1.
# 0 .......
#   0123456

SHAPE_C = Vec2.list(
    # 0       1       2       3       4       5       6       7
    [(1, 1), (5, 1), (5, 3), (3, 3), (3, 5), (5, 5), (5, 7), (1, 7)]
)

#   0123456
# 8 .......
# 7 .+---+.
# 6 .|678|.
# 5 .|5+-+.
# 4 .|4|...
# 3 .|3+-+.
# 2 .|012|.
# 1 .+---+.
# 0 .......
#   0123456

POINTS_INSIDE = Vec2.list(
    # 0       1       2       3       4       5       6       7       8
    [(2, 2), (3, 2), (4, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 6), (4, 6)]
)

#   0123456
# 8 b.c.d.e
# 7 .+---+.
# 6 9|...|a
# 5 .|.+-+.
# 4 6|.|7.8
# 3 .|.+-+.
# 2 4|...|5
# 1 .+---+.
# 0 0.1.2.3
#   0123456

POINTS_OUTSIDE = Vec2.list(
    [
        (0, 0),  # 0
        (2, 0),  # 1
        (4, 0),  # 2
        (6, 0),  # 3
        (0, 2),  # 4
        (6, 2),  # 5
        (0, 4),  # 6
        (4, 4),  # 7
        (6, 2),  # 8
        (0, 6),  # 9
        (6, 6),  # a
        (0, 8),  # b
        (2, 8),  # c
        (4, 8),  # d
        (6, 8),  # e
    ]
)


@pytest.fixture(scope="module")
def polygon():
    return CCP(SHAPE_C)


# see also test_613_is_point_in_polygon_2d
@pytest.mark.parametrize("point", POINTS_INSIDE)
def test_point_is_inside_polygon(point: Vec2, polygon: CCP):
    assert polygon.is_inside(point) is True


# see also test_613_is_point_in_polygon_2d
@pytest.mark.parametrize("point", POINTS_OUTSIDE)
def test_point_is_outside_polygon(point: Vec2, polygon: CCP):
    assert polygon.is_inside(point) is False


class TestLineClipping:
    def test_a_and_b_outside_no_intersections_v(self, polygon: CCP):
        # 8 b......
        # 7 .+---+.
        # 6 .|...|.
        # 5 .|.+-+.
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 .|...|.
        # 1 .+---+.
        # 0 a......
        #   0123456
        result = polygon.clip_line(Vec2(0, 0), Vec2(0, 8))
        assert len(result) == 0

    def test_a_and_b_outside_no_intersections_h(self, polygon: CCP):
        # 3 .|.+-+.
        # 2 .|...|.
        # 1 .+---+.
        # 0 a.....b
        #   0123456
        result = polygon.clip_line(Vec2(0, 0), Vec2(6, 0))
        assert len(result) == 0

    def test_a_outside_b_inside_1_intersection_v(self, polygon: CCP):
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 .|b..|.
        # 1 .+x--+.
        # 0 ..a....
        #   0123456
        result = polygon.clip_line(Vec2(2, 0), Vec2(2, 2))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((2, 1))
        assert e.isclose((2, 2))

    def test_a_outside_b_inside_1_intersection_h(self, polygon: CCP):
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 axb..|.
        # 1 .+---+.
        # 0 .......
        #   0123456
        result = polygon.clip_line(Vec2(0, 2), Vec2(2, 2))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((1, 2))
        assert e.isclose((2, 2))

    def test_a_inside_b_outside_1_intersection_v(self, polygon: CCP):
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 .|a..|.
        # 1 .+x--+.
        # 0 ..b....
        #   0123456
        result = polygon.clip_line(Vec2(2, 2), Vec2(2, 0))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((2, 2))
        assert e.isclose((2, 1))

    def test_a_inside_b_outside_1_intersection_h(self, polygon: CCP):
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 bxa..|.
        # 1 .+---+.
        # 0 .......
        #   0123456
        result = polygon.clip_line(Vec2(2, 2), Vec2(0, 2))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((2, 2))
        assert e.isclose((1, 2))

    def test_a_outside_b_outside_2_intersections(self, polygon: CCP):
        # 6 .|...|.
        # 5 .|.+-+.
        # 4 .|.|b..
        # 3 .|.+x+.
        # 2 .|...|.
        # 1 .+--x+.
        # 0 ....a..
        #   0123456
        result = polygon.clip_line(Vec2(4, 0), Vec2(4, 4))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((4, 1))
        assert e.isclose((4, 3))

    def test_a_outside_b_inside_3_intersections(self, polygon: CCP):
        # 8 .......
        # 7 .+---+.
        # 6 .|..b|.
        # 5 .|.+x+.
        # 4 .|.|...
        # 3 .|.+x+.
        # 2 .|...|.
        # 1 .+--x+.
        # 0 ....a..
        #   0123456
        result = polygon.clip_line(Vec2(4, 0), Vec2(4, 6))
        assert len(result) == 2
        s0, e0 = result[0]
        assert s0.isclose((4, 1))
        assert e0.isclose((4, 3))

        s1, e1 = result[1]
        assert s1.isclose((4, 5))
        assert e1.isclose((4, 6))

    def test_a_inside_b_outside_3_intersections(self, polygon: CCP):
        # 8 ....b..
        # 7 .+--x+.
        # 6 .|...|.
        # 5 .|.+x+.
        # 4 .|.|...
        # 3 .|.+x+.
        # 2 .|..a|.
        # 1 .+---+.
        # 0 .......
        #   0123456
        result = polygon.clip_line(Vec2(4, 2), Vec2(4, 8))
        assert len(result) == 2
        s0, e0 = result[0]
        assert s0.isclose((4, 2))
        assert e0.isclose((4, 3))

        s1, e1 = result[1]
        assert s1.isclose((4, 5))
        assert e1.isclose((4, 7))


if __name__ == "__main__":
    pytest.main([__file__])
