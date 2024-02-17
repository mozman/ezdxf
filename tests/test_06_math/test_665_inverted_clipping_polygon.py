# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pytest

from ezdxf.math import Vec2, BoundingBox2d
from ezdxf.math.clipping import InvertedClippingPolygon2d as ICP
from ezdxf.math.clipping import (
    find_closest_vertices,
    make_inverted_clipping_polygon,
)

# The InvertedClippingPolygon2d is based on the ConcaveClippingPolygon2d,
# so not all clipping tests are replicated here. See test_664.


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
    # closest vertices are: 2<->6 where the the inner polygon will be connected
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


class TestLineClipping:
    # just test the basics to see if the implementation runs, more tests in test_664.
    def test_basic_clipping(self, inverted_polygon: ICP):
        """Does the inside/outside detection work for inverted polygons?"""
        # 5  .|.|..|.|.
        # 4  ax=x..x=xb
        # 3  .|.0--1.|.
        # 2  .|/.....|.
        # 1  .4------+.
        # 0  ..........
        #    0123456789
        result = inverted_polygon.clip_line(Vec2(0, 4), Vec2(9, 4))
        assert len(result) == 2
        l1, l2 = result
        assert l1[0].isclose((1, 4))
        assert l1[1].isclose((3, 4))
        assert l2[0].isclose((6, 4))
        assert l2[1].isclose((8, 4))

    def test_connection_line_create_intersection_point(self, inverted_polygon: ICP):
        """A line should be clipped at the diagonal connection line between 4<->0.
        There are two clipping lines 4->0 and 4<-0. The zero-length segment between the
        real segments should not be returned.
        """
        # 5  .|.|..|.|.
        # 4  .|.|..|.|.
        # 3  .|.0--1.|.
        # 2  axx=====xb
        # 1  .4------+.
        # 0  ..........
        #    0123456789
        result = inverted_polygon.clip_line(Vec2(0, 2), Vec2(9, 2))
        assert len(result) == 2
        l1, l2 = result
        assert l1[0].isclose((1, 2))
        assert l1[1].isclose((2, 2))
        # zero-length segment (2, 2) -> (2, 2) is ignored or outside!
        assert l2[0].isclose((2, 2))
        assert l2[1].isclose((8, 2))

    def test_colinear_line(self, inverted_polygon: ICP):
        """Colinear line segments are inside per definition."""
        # 5  .|.|..|.|.
        # 4  .|.|..|.|.
        # 3  ax=x==x=xb
        # 2  .|/.....|.
        # 1  .4------+.
        # 0  ..........
        #    0123456789
        result = inverted_polygon.clip_line(Vec2(0, 3), Vec2(9, 3))
        assert len(result) == 3
        l1, l2, l3 = result
        assert l1[0].isclose((1, 3))
        assert l1[1].isclose((3, 3))
        # zero-length segment (3, 3) -> (3, 3) is ignored or outside!
        assert l2[0].isclose((3, 3))
        assert l2[1].isclose((6, 3))
        assert l3[0].isclose((6, 3))
        assert l3[1].isclose((8, 3))


class TestPolygonClipping:
    # just test the basics to see if the implementation runs, more tests in test_664.
    def test_polygon_outside(self, inverted_polygon: ICP):
        # 9  ..........
        # 8  .+------5.
        # 7  .|......|.
        # 6  .|.3--2.|.
        # 5  .|.|dc|.|.
        # 4  .|.|ab|.|.
        # 3  .|.0--1.|.
        # 2  .|/.....|.
        # 1  .4------+.
        # 0  ..........
        #    0123456789

        result = inverted_polygon.clip_polygon(
            #           a       b       c       d
            Vec2.list([(4, 4), (5, 4), (5, 5), (4, 5)])
        )
        assert len(result) == 0

    def test_polygon_clipping(self, inverted_polygon: ICP):
        # 5  .|.|..|.|.
        # 4  .|.|..|.|.
        # 3  .|.0--1.|.
        # 2  .|/d--c.|.
        # 1  .4-x--x-+.
        # 0  ...a--b...
        #    0123456789

        result = inverted_polygon.clip_polygon(
            #           a       b       c       d
            Vec2.list([(3, 0), (6, 0), (6, 2), (3, 2)])
        )
        assert len(result) == 1
        clipped_polygon = result[0]
        # The clipped polygon doesn't have to be closed, future implementation may 
        # change and the results of the Greiner-Horman algorithm for "edge-cases" are 
        # not consistent!
        assert len(clipped_polygon) in (4, 5)
        if len(clipped_polygon) == 5:
            assert clipped_polygon[0].isclose(clipped_polygon[-1])
        bbox = BoundingBox2d(clipped_polygon)
        assert bbox.extmin.isclose((3, 1))  # lower-left clipped vertex
        assert bbox.extmax.isclose((6, 2))  # vertex c


if __name__ == "__main__":
    pytest.main([__file__])
