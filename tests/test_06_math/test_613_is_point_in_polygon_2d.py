# Copyright (c) 2020-2024, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import Vec2, is_convex_polygon_2d
from ezdxf.math._construct import is_point_in_polygon_2d  # Python version
from ezdxf.acc import USE_C_EXT

is_point_in_polygon_cy = is_point_in_polygon_2d

if USE_C_EXT:
    try:  # Cython version
        from ezdxf.acc.construct import is_point_in_polygon_2d as is_point_in_polygon_cy
    except ImportError:
        pass


def test_inside_horizontal_box():
    square = Vec2.list([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert is_point_in_polygon_2d(Vec2(0.5, 0.5), square) == 1


def test_outside_horizontal_box():
    square = Vec2.list([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert is_point_in_polygon_2d(Vec2(-0.5, 0.5), square) == -1
    assert is_point_in_polygon_2d(Vec2(1.5, 0.5), square) == -1
    assert is_point_in_polygon_2d(Vec2(0.5, -0.5), square) == -1
    assert is_point_in_polygon_2d(Vec2(0.5, 1.5), square) == -1


def test_colinear_outside_horizontal_box():
    square = Vec2.list([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert is_point_in_polygon_2d(Vec2(1.5, 0), square) == -1
    assert is_point_in_polygon_2d(Vec2(-0.5, 0), square) == -1
    assert is_point_in_polygon_2d(Vec2(0, 1.5), square) == -1
    assert is_point_in_polygon_2d(Vec2(0, -0.5), square) == -1


def test_corners_horizontal_box():
    square = Vec2.list([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert is_point_in_polygon_2d(Vec2(0, 0), square) == 0
    assert is_point_in_polygon_2d(Vec2(0, 1), square) == 0
    assert is_point_in_polygon_2d(Vec2(1, 1), square) == 0
    assert is_point_in_polygon_2d(Vec2(0, 1), square) == 0


def test_inside_slanted_box():
    square = Vec2.list([(0, 0), (1, 1), (0, 2), (-1, 1)])
    assert is_point_in_polygon_2d(Vec2(0, 1), square) == 1


def test_outside_slanted_box():
    square = Vec2.list([(0, 0), (1, 1), (0, 2), (-1, 1)])
    assert is_point_in_polygon_2d(Vec2(-1, 0), square) == -1
    assert is_point_in_polygon_2d(Vec2(1, 0), square) == -1
    assert is_point_in_polygon_2d(Vec2(1, 2), square) == -1
    assert is_point_in_polygon_2d(Vec2(-1, 2), square) == -1


def test_corners_slanted_box():
    square = Vec2.list([(0, 0), (1, 1), (0, 2), (-1, 1)])
    assert is_point_in_polygon_2d(Vec2(0, 0), square) == 0
    assert is_point_in_polygon_2d(Vec2(1, 1), square) == 0
    assert is_point_in_polygon_2d(Vec2(0, 2), square) == 0
    assert is_point_in_polygon_2d(Vec2(-1, 1), square) == 0


def test_borders_slanted_box_stable():
    square = Vec2.list([(0, 0), (1, 1), (0, 2), (-1, 1)])
    assert is_point_in_polygon_2d(Vec2(0.5, 0.5), square) == 0
    assert is_point_in_polygon_2d(Vec2(0.5, 1.5), square) == 0
    assert is_point_in_polygon_2d(Vec2(-0.5, 1.5), square) == 0
    assert is_point_in_polygon_2d(Vec2(-0.5, 0.5), square) == 0


# Test concave polygon:
#
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

SHAPE_C_CCW = Vec2.list(
    # 0       1       2       3       4       5       6       7
    [(1, 1), (5, 1), (5, 3), (3, 3), (3, 5), (5, 5), (5, 7), (1, 7)]
)
SHAPE_C_CW = list(reversed(SHAPE_C_CCW))

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


#   0123456
# 8 .......
# 7 .+-6-+.
# 6 .|...5.
# 5 .|.+4+.
# 4 .7.3...
# 3 .|.+2+.
# 2 .|...1.
# 1 .+-0-+.
# 0 .......
#   0123456

POINTS_ON_BOUNDARY = Vec2.list(
    # 0       1       2       3       4       5       6       7
    [(1, 3), (5, 2), (4, 3), (3, 4), (4, 5), (5, 6), (3, 7), (1, 4)]
)


def test_shape_c_is_not_convex():
    assert is_convex_polygon_2d(SHAPE_C_CCW) is False
    assert is_convex_polygon_2d(SHAPE_C_CW) is False


@pytest.mark.parametrize("point", POINTS_INSIDE)
def test_is_inside_ccw_polygon(point: Vec2):
    assert is_point_in_polygon_2d(point, SHAPE_C_CCW) == 1


@pytest.mark.parametrize("point", POINTS_ON_BOUNDARY)
def test_is_on_boundary_ccw_polygon(point: Vec2):
    assert is_point_in_polygon_2d(point, SHAPE_C_CCW) == 0


@pytest.mark.parametrize("point", POINTS_OUTSIDE)
def test_is_outside_ccw_polygon(point: Vec2):
    assert is_point_in_polygon_2d(point, SHAPE_C_CCW) == -1


@pytest.mark.parametrize("point", POINTS_INSIDE)
def test_is_inside_cw_polygon(point: Vec2):
    assert is_point_in_polygon_2d(point, SHAPE_C_CW) == 1


@pytest.mark.parametrize("point", POINTS_ON_BOUNDARY)
def test_is_on_boundary_cw_polygon(point: Vec2):
    assert is_point_in_polygon_2d(point, SHAPE_C_CW) == 0


@pytest.mark.parametrize("point", POINTS_OUTSIDE)
def test_is_outside_cw_polygon(point: Vec2):
    assert is_point_in_polygon_2d(point, SHAPE_C_CW) == -1


@pytest.mark.skipif(
    is_point_in_polygon_cy is is_point_in_polygon_2d,
    reason="no Cython implementation available",
)
class TestCythonImplementation:
    @pytest.mark.parametrize("point", POINTS_INSIDE)
    def test_is_inside_ccw_polygon(self, point: Vec2):
        assert is_point_in_polygon_cy(point, SHAPE_C_CCW) == 1

    @pytest.mark.parametrize("point", POINTS_ON_BOUNDARY)
    def test_is_on_boundary_ccw_polygon(self, point: Vec2):
        assert is_point_in_polygon_cy(point, SHAPE_C_CCW) == 0

    @pytest.mark.parametrize("point", POINTS_OUTSIDE)
    def test_is_outside_ccw_polygon(self, point: Vec2):
        assert is_point_in_polygon_cy(point, SHAPE_C_CCW) == -1


if __name__ == "__main__":
    pytest.main([__file__])
