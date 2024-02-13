# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
# pylint: disable=redefined-outer-name  # pytest-fixtures!
from __future__ import annotations
import pytest

from ezdxf.math import Vec2, BoundingBox2d
from ezdxf.math.clipping import InvertedClippingPolygon2d as ICP
from ezdxf.math.clipping import (
    find_closest_vertices,
    make_inverted_clipping_polygon,
)


@pytest.mark.parametrize(
    "extmin,extmax,expected",
    [
        [(0, 0), (1, 1), (0, 0)],
        [(8, 1), (9, 2), (1, 1)],
        [(8, 8), (9, 9), (2, 2)],
        [(1, 8), (2, 9), (3, 3)],
    ],
    ids=["lower-left", "lower-right", "upper-right", "upper-left"],
)
def test_find_closest_vertices(extmin, extmax, expected):
    outer = BoundingBox2d([(0, 0), (10, 10)]).rect_vertices()
    inner = BoundingBox2d([extmin, extmax]).rect_vertices()
    assert find_closest_vertices(inner, outer) == expected


# 9  7........6
# 8  ......3-2.
# 7  ......|.|.
# 6  ......0-1.
# 5  ..........
# 4  ..........
# 3  ..........
# 2  ..........
# 1  ..........
# 0  4........5
#    0123456789
def test_make_inverted_clipping_polygon():
    #                                4       6
    outer_boundary = BoundingBox2d([(0, 0), (9, 9)])
    #                           0       1       2       3
    inner_polygon = Vec2.list([(6, 6), (8, 6), (8, 8), (6, 8)])
    result = make_inverted_clipping_polygon(inner_polygon, outer_boundary)
    assert len(result) == 11
    # closest vertices are: 2-6 where the the inner polygon will be connected
    # to the outer boundary
    for num, point in enumerate(
        [
            (8, 8),  # 2: start inner path at closest vertex pair
            (6, 8),  # 3: walk in counter clockwise order
            (6, 6),  # 0
            (8, 6),  # 1
            (8, 8),  # 2: close inner path
            (9, 9),  # 6: connect to outer boundary
            (9, 0),  # 5: walk in clockwise order
            (0, 0),  # 4
            (0, 9),  # 7
            (9, 9),  # 6: closer outer boundary
            (8, 8),  # 2: connect to inner polygon
        ]
    ):
        assert result[num] == point


# The connection between inner polygon and outer bounds, is created
# automatically at setup! This creates a closed concave clipping shape.
#
#    0123456789
# 9  ..........
# 8  .+------5.
# 7  .|......|.
# 6  .|.3--2.|.
# 5  .|.|..|.|.
# 4  .|.|..|.|.
# 3  .|.0--1.|.
# 2  .|/.....|.
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
