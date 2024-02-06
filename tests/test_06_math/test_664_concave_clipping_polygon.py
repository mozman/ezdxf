# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pytest

from ezdxf.math import Vec2
from ezdxf.math.clipping import ConcaveClippingPolygon2d

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
    return ConcaveClippingPolygon2d(SHAPE_C)


# see also test_613_is_point_in_polygon_2d
@pytest.mark.parametrize("point", POINTS_INSIDE)
def test_point_is_inside_polygon(point: Vec2, polygon: ConcaveClippingPolygon2d):
    assert polygon.is_inside(point) is True


# see also test_613_is_point_in_polygon_2d
@pytest.mark.parametrize("point", POINTS_OUTSIDE)
def test_point_is_outside_polygon(point: Vec2, polygon: ConcaveClippingPolygon2d):
    assert polygon.is_inside(point) is False


if __name__ == "__main__":
    pytest.main([__file__])
