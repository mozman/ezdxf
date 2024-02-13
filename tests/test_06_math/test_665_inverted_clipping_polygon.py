# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
# pylint: disable=redefined-outer-name  # pytest-fixtures!
from __future__ import annotations
import pytest

from ezdxf.math import Vec2, BoundingBox2d
from ezdxf.math.clipping import InvertedClippingPolygon2d as ICP

# The connection between inner polygon and outer bounds, is created 
# automatically at setup! This creates a closed concave clipping shape.
# 
#    0123456789
# 9  ..........
# 8  .+------5.
# 7  .|\.....|. 
# 6  .|.3--2.|. automatically at setup! This creates a closed concave clipping shape.
# 5  .|.|..|.|.
# 4  .|.|..|.|.
# 3  .|.0--1.|.
# 2  .|......|.
# 1  .4------+.
# 0  ..........
#    0123456789
INNER_POLYGON = Vec2.list(
    # 0       1       2       3
    [(3, 3), (6, 3), (6, 6), (3, 6)]
)


@pytest.fixture(scope="module")
def inverted_polygon():
    #                                         4       5
    return ICP(INNER_POLYGON, BoundingBox2d([(1, 1), (8, 8)]))


#    0123456789
# 9  ..........
# 8  .+------5.
# 7  .|d....c|.
# 6  .|.3--2.|.
# 5  .|.|..|.|.
# 4  .|.|..|.|.
# 3  .|.0--1.|.
# 2  .|a....b|.
# 1  .4------+.
# 0  ..........
#    0123456789
#                           a       b       c       d
POINTS_INSIDE = Vec2.list([(2, 2), (7, 2), (7, 7), (2, 7)])

#    0123456789
# 9  g...f....e
# 8  .+------5.
# 7  .|......|.
# 6  .|.3--2.|.
# 5  .|.|..|.|.
# 4  h|.|i.|.|d
# 3  .|.0--1.|.
# 2  .|......|.
# 1  .4------+.
# 0  a...b....c
#    0123456789

POINTS_OUTSIDE = Vec2.list(
    # a       b       c       d       e       f       g       h       i
    [(0, 0), (4, 0), (9, 0), (9, 4), (9, 9), (4, 9), (0, 9), (0, 4), (4, 4)]
)


@pytest.mark.parametrize("point", POINTS_INSIDE)
def test_point_is_inside_polygon(point: Vec2, inverted_polygon: ICP):
    assert inverted_polygon.is_inside(point) is True


@pytest.mark.parametrize("point", POINTS_OUTSIDE)
def test_point_is_outside_polygon(point: Vec2, inverted_polygon: ICP):
    assert inverted_polygon.is_inside(point) is False


if __name__ == "__main__":
    pytest.main([__file__])
