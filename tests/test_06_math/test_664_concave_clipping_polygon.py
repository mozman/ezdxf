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
def polygon_c():
    return CCP(SHAPE_C)


# see also test_613_is_point_in_polygon_2d
@pytest.mark.parametrize("point", POINTS_INSIDE)
def test_point_is_inside_polygon(point: Vec2, polygon_c: CCP):
    assert polygon_c.is_inside(point) is True


# see also test_613_is_point_in_polygon_2d
@pytest.mark.parametrize("point", POINTS_OUTSIDE)
def test_point_is_outside_polygon(point: Vec2, polygon_c: CCP):
    assert polygon_c.is_inside(point) is False


class TestLineClipping:
    def test_a_and_b_outside_no_intersections_v(self, polygon_c: CCP):
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
        result = polygon_c.clip_line(Vec2(0, 0), Vec2(0, 8))
        assert len(result) == 0

    def test_a_and_b_outside_no_intersections_h(self, polygon_c: CCP):
        # 3 .|.+-+.
        # 2 .|...|.
        # 1 .+---+.
        # 0 a.....b
        #   0123456
        result = polygon_c.clip_line(Vec2(0, 0), Vec2(6, 0))
        assert len(result) == 0

    def test_a_and_b_inside_no_intersections_h(self, polygon_c: CCP):
        # 3 .|.+-+.
        # 2 .|a.b|.
        # 1 .+---+.
        # 0 .......
        #   0123456
        result = polygon_c.clip_line(Vec2(2, 2), Vec2(4, 2))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((2, 2))
        assert e.isclose((4, 2))

    def test_a_outside_b_inside_1_intersection_v(self, polygon_c: CCP):
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 .|b..|.
        # 1 .+x--+.
        # 0 ..a....
        #   0123456
        result = polygon_c.clip_line(Vec2(2, 0), Vec2(2, 2))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((2, 1))
        assert e.isclose((2, 2))

    def test_a_outside_b_inside_1_intersection_h(self, polygon_c: CCP):
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 axb..|.
        # 1 .+---+.
        # 0 .......
        #   0123456
        result = polygon_c.clip_line(Vec2(0, 2), Vec2(2, 2))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((1, 2))
        assert e.isclose((2, 2))

    def test_a_inside_b_outside_1_intersection_v(self, polygon_c: CCP):
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 .|a..|.
        # 1 .+x--+.
        # 0 ..b....
        #   0123456
        result = polygon_c.clip_line(Vec2(2, 2), Vec2(2, 0))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((2, 2))
        assert e.isclose((2, 1))

    def test_a_inside_b_outside_1_intersection_h(self, polygon_c: CCP):
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 bxa..|.
        # 1 .+---+.
        # 0 .......
        #   0123456
        result = polygon_c.clip_line(Vec2(2, 2), Vec2(0, 2))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((2, 2))
        assert e.isclose((1, 2))

    def test_a_outside_b_outside_2_intersections(self, polygon_c: CCP):
        # 6 .|...|.
        # 5 .|.+-+.
        # 4 .|.|b..
        # 3 .|.+x+.
        # 2 .|...|.
        # 1 .+--x+.
        # 0 ....a..
        #   0123456
        result = polygon_c.clip_line(Vec2(4, 0), Vec2(4, 4))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((4, 1))
        assert e.isclose((4, 3))

    def test_a_outside_b_inside_3_intersections(self, polygon_c: CCP):
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
        result = polygon_c.clip_line(Vec2(4, 0), Vec2(4, 6))
        assert len(result) == 2
        s0, e0 = result[0]
        assert s0.isclose((4, 1))
        assert e0.isclose((4, 3))

        s1, e1 = result[1]
        assert s1.isclose((4, 5))
        assert e1.isclose((4, 6))

    def test_a_inside_b_outside_3_intersections(self, polygon_c: CCP):
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
        result = polygon_c.clip_line(Vec2(4, 2), Vec2(4, 8))
        assert len(result) == 2
        s0, e0 = result[0]
        assert s0.isclose((4, 2))
        assert e0.isclose((4, 3))

        s1, e1 = result[1]
        assert s1.isclose((4, 5))
        assert e1.isclose((4, 7))

    def test_line_intersection_at_vertex(self, polygon_c: CCP):
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 .|b..|.
        # 1 .x---+.
        # 0 a......
        #   0123456
        result = polygon_c.clip_line(Vec2(0, 0), Vec2(2, 2))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((1, 1))
        assert e.isclose((2, 2))

    def test_line_touches_at_vertex(self, polygon_c: CCP):
        # 4 .|.|...
        # 3 .|.3-2.
        # 2 a|...|.
        # 1 .x---1.
        # 0 ..b....
        #   0123456
        result = polygon_c.clip_line(Vec2(0, 2), Vec2(2, 0))
        assert len(result) == 0

    def test_line_is_colinear_to_outer_edge(self, polygon_c: CCP):
        # 4 .|.|...
        # 3 .|.3-2.
        # 2 .|...|.
        # 1 ax+++xb
        # 0 .......
        #   0123456
        result = polygon_c.clip_line(Vec2(0, 1), Vec2(6, 1))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((1, 1))
        assert e.isclose((5, 1))

    def test_line_is_colinear_to_inner_edge(self, polygon_c: CCP):
        """Colinear line segments are inside per definition."""
        # 4 .|.|...
        # 3 ax+x+xb
        # 2 .|...|.
        # 1 .0---1.
        # 0 .......
        #   0123456
        result = polygon_c.clip_line(Vec2(0, 3), Vec2(6, 3))
        assert len(result) == 2
        s, e = result[0]
        assert s.isclose((1, 3))
        assert e.isclose((3, 3))
        s, e = result[1]
        assert s.isclose((3, 3))
        assert e.isclose((5, 3))

    def test_line_is_colinear_to_inner_edge_reverse(self, polygon_c: CCP):
        """Colinear line segments are inside per definition."""
        # 4 .|.|...
        # 3 bx+x+xa
        # 2 .|...|.
        # 1 .0---1.
        # 0 .......
        #   0123456
        result = polygon_c.clip_line(Vec2(6, 3), Vec2(0, 3))
        assert len(result) == 2
        s, e = result[0]
        assert s.isclose((5, 3))
        assert e.isclose((3, 3))
        s, e = result[1]
        assert s.isclose((3, 3))
        assert e.isclose((1, 3))

    def test_line_is_equal_to_edge(self, polygon_c: CCP):
        # 4 .|.|...
        # 3 .|.+-+.
        # 2 .|...|.
        # 1 .a---b.
        # 0 .......
        #   0123456
        result = polygon_c.clip_line(Vec2(1, 1), Vec2(5, 1))
        assert len(result) == 1
        s, e = result[0]
        assert s.isclose((1, 1))
        assert e.isclose((5, 1))


#              11111
#    012345678901234
# 10 ...............
# 9  .7---6...3---2.
# 8  .|...|...|...|.
# 7  .|...|...|...|.
# 6  .|...|...|...|.
# 5  .|...5---4...|.
# 4  .|...........|.
# 3  .|...........|.
# 2  .|...........|.
# 1  .0-----------1.
# 0  ...............
#              11111
#    012345678901234
SHAPE_U = Vec2.list(
    # 0       1        2        3       4       5       6       7
    [(1, 1), (13, 1), (13, 9), (9, 9), (9, 5), (5, 5), (5, 9), (1, 9)]
)


@pytest.fixture(scope="module")
def polygon_u():
    return CCP(SHAPE_U)


class TestPolylineClipping:
    def test_polyline_outside(self, polygon_u: CCP):
        result = polygon_u.clip_polyline(
            Vec2.list([(0, 0), (14, 0), (14, 10), (0, 10)])
        )
        assert len(result) == 0

    def test_polyline_inside_no_intersection(self, polygon_u: CCP):
        # 6  .|...|...|...|.
        # 5  .|...5---4...|.
        # 4  .|d+++++++++c|.
        # 3  .|..........+|.
        # 2  .|a+++++++++b|.
        # 1  .0-----------1.
        # 0  ...............
        #              11111
        #    012345678901234
        #                                            a       b        c        d
        result = polygon_u.clip_polyline(Vec2.list([(2, 2), (12, 2), (12, 4), (2, 4)]))
        assert len(result) == 1
        polyline = result[0]
        assert len(polyline) == 4
        assert polyline[0].isclose((2, 2))
        assert polyline[2].isclose((12, 4))

    def test_polyline_inside_with_intersection(self, polygon_u: CCP):
        # 7  .|...|...|...|.
        # 6  .|d++x...x++c|.
        # 5  .|...5---4..+|.
        # 4  .|..........+|.
        # 3  .|..........+|.
        # 2  .|a+++++++++b|.
        # 1  .0-----------1.
        # 0  ...............
        #              11111
        #    012345678901234
        #                                            a       b        c        d
        result = polygon_u.clip_polyline(Vec2.list([(2, 2), (12, 2), (12, 6), (2, 6)]))
        assert len(result) == 2
        p1, p2 = result
        assert p1[0].isclose((2, 2))
        assert p1[1].isclose((12, 2))
        assert p1[2].isclose((12, 6))
        assert p1[3].isclose((9, 6))

        assert p2[0].isclose((5, 6))
        assert p2[1].isclose((2, 6))

    def test_polyline_crossing_border(self, polygon_u: CCP):
        # 7  .|...|...|...|.
        # 6  .|d++x...x++c|.
        # 5  .|...5---4..+|.
        # 4  .|..........+|.
        # 3  .|..........+|.
        # 2  .|..........+|.
        # 1  .0----------x1.
        # 0  ..a+++++++++b..
        #              11111
        #    012345678901234
        #                                            a       b        c        d
        result = polygon_u.clip_polyline(Vec2.list([(2, 0), (12, 0), (12, 6), (2, 6)]))
        assert len(result) == 2
        p1, p2 = result
        assert p1[0].isclose((12, 1))
        assert p1[1].isclose((12, 6))
        assert p1[2].isclose((9, 6))

        assert p2[0].isclose((5, 6))
        assert p2[1].isclose((2, 6))

    def test_polyline_along_the_border_1(self, polygon_u: CCP):
        # 10 ...............
        # 9  .d+++x...x+++c.
        # 8  .|...|...|...+.
        # 7  .|...|...|...+.
        # 6  .|...|...|...+.
        # 5  .|...5---4...+.
        # 4  .|...........+.
        # 3  .|...........+.
        # 2  .|...........+.
        # 1  .a+++++++++++b.
        # 0  ...............
        #              11111
        #    012345678901234
        #                                            a       b        c        d
        result = polygon_u.clip_polyline(Vec2.list([(1, 1), (13, 1), (13, 9), (1, 9)]))
        assert len(result) == 2
        p1, p2 = result
        assert p1[0].isclose((1, 1))
        assert p1[1].isclose((13, 1))
        assert p1[2].isclose((13, 9))
        assert p1[3].isclose((9, 9))

        assert p2[0].isclose((5, 9))
        assert p2[1].isclose((1, 9))

    def test_polyline_along_the_border_2(self, polygon_u: CCP):
        # 6  .|...|...|...|.
        # 5  .d+++x+++x+++c.
        # 4  .|...........+.
        # 3  .|...........+.
        # 2  .|...........+.
        # 1  .a+++++++++++b.
        # 0  ...............
        #              11111
        #    012345678901234
        #                                            a       b        c        d
        result = polygon_u.clip_polyline(Vec2.list([(1, 1), (13, 1), (13, 5), (1, 5)]))
        assert len(result) == 1
        p1 = result[0]
        assert p1[0].isclose((1, 1))
        assert p1[1].isclose((13, 1))
        assert p1[2].isclose((13, 5))
        assert p1[3].isclose((9, 5))
        assert p1[4].isclose((5, 5))
        assert p1[5].isclose((1, 5))


class TestPolygonClipping:
    """Based on the paper "Efficient Clipping of Arbitrary Polygons" by
    Günther Greiner and Kai Hormann.

    Tests see test_619_greiner_hormann.py
    """

    @pytest.mark.parametrize(
        "vertices",
        [
            [],
            [Vec2()],
            [Vec2(), Vec2()],
            [Vec2(), Vec2(), Vec2()],
        ],
        ids=["#0", "#1", "#2", "#3"],
    )
    def test_too_few_vertices(self, vertices, polygon_u: CCP):
        assert len(polygon_u.clip_polygon(vertices)) == 0

    def test_polygon_inside_no_intersection(self, polygon_u: CCP):
        # 6  .|...|...|...|.
        # 5  .|...5---4...|.
        # 4  .|d+++++++++c|.
        # 3  .|+.........+|.
        # 2  .|a+++++++++b|.
        # 1  .0-----------1.
        # 0  ...............
        #              11111
        #    012345678901234
        #                                           a       b        c        d
        result = polygon_u.clip_polygon(Vec2.list([(2, 2), (12, 2), (12, 4), (2, 4)]))
        # returns the subject polygon [a, b, c, d]
        assert len(result) == 1
        polygon = result[0]
        assert len(polygon) == 4
        assert polygon[0].isclose((2, 2))
        assert polygon[2].isclose((12, 4))

    @pytest.mark.xfail(reason="edge case not covered")
    def test_polygon_outside_no_intersection(self, polygon_u: CCP):
        # 10 d.............c
        # 9  .7---6...3---2.
        # 8  .|...|...|...|.
        # 7  .|...|...|...|.
        # 6  .|...|...|...|.
        # 5  .|...5---4...|.
        # 4  .|...........|.
        # 3  .|...........|.
        # 2  .|...........|.
        # 1  .0-----------1.
        # 0  a.............b
        #              11111
        #    012345678901234
        #                                           a       b        c         d
        result = polygon_u.clip_polygon(Vec2.list([(0, 0), (14, 0), (14, 10), (0, 10)]))
        # returns the clipping polygon [0, 1, 2, 3, 4, 5, 6, 7]
        assert len(result) == 1
        polygon = result[0]
        assert len(polygon) == 8
        assert polygon[0] == Vec2(1, 1)
        assert polygon[7] == Vec2(1, 9)

    def test_polygon_inside_with_intersection(self, polygon_u: CCP):
        # 7  .|d++x...x++c|.
        # 6  .|+..+...+..+|.
        # 5  .|+..5+++4..+|.
        # 4  .|+.........+|.
        # 3  .|+.........+|.
        # 2  .|a+++++++++b|.
        # 1  .0-----------1.
        # 0  ...............
        #              11111
        #    012345678901234
        #                                           a       b        c        d
        result = polygon_u.clip_polygon(Vec2.list([(2, 2), (12, 2), (12, 7), (2, 7)]))
        assert len(result) == 1
        polygon = result[0]
        assert len(polygon) == 9
        # returns a closed polygon!
        assert polygon[0].isclose(polygon[-1]) is True

    def test_polygon_colinear_edges(self, polygon_u: CCP):
        # 5  .d+++5+++4++c|.
        # 4  .+..........+|.
        # 3  .+..........+|.
        # 2  .a++++++++++b|.
        # 1  .0-----------1.
        # 0  ...............
        #              11111
        #    012345678901234
        #                                           a       b        c        d
        result = polygon_u.clip_polygon(Vec2.list([(1, 2), (12, 2), (12, 5), (1, 5)]))
        # The Greiner-Hormann algorithm has issues with intersection points on polygon
        # edges.
        assert len(result) == 1
        polygon = result[0]
        # intersection points (4) and (5) are missing!
        assert len(polygon) == 4
        # returns an open polygon!
        assert polygon[0].isclose(polygon[-1]) is False


if __name__ == "__main__":
    pytest.main([__file__])
