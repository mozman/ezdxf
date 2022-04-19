#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec2
from ezdxf.math.clipping import (
    greiner_hormann_union,
    greiner_hormann_difference,
    greiner_hormann_intersection,
    line_intersection,
)
from ezdxf.render.forms import circle


class TestLineIntersection:
    """The Greiner/Hormann algorithm needs a special intersection function.

    Start and end points of a line are not intersection points!

    Which also leads to issues for joining adjacent but not intersecting
    polygons.

    """
    def test_start_point_is_not_an_intersection_point(self):
        s1, s2 = Vec2(1, 1), Vec2(3, 1)
        c1, c2 = Vec2(2, 1), Vec2(2, 2)
        assert line_intersection(s1, s2, c1, c2)[0] is None

    def test_end_point_is_not_an_intersection_point(self):
        s1, s2 = Vec2(1, 1), Vec2(3, 1)
        c1, c2 = Vec2(2, 2), Vec2(2, 1)
        assert line_intersection(s1, s2, c1, c2)[0] is None

    def test_corner_point_is_not_an_intersection_point(self):
        s1, s2 = Vec2(1, 1), Vec2(3, 1)
        c1, c2 = Vec2(1, 1), Vec2(1, 2)
        assert line_intersection(s1, s2, c1, c2)[0] is None

    def test_vertical_line_does_intersect_skewed_line(self):
        s1, s2 = Vec2(10, 1), Vec2(10, -7)
        c1, c2 = Vec2(-10, 3), Vec2(17, -7)
        point, *_ = line_intersection(s1, s2, c1, c2)
        assert point.x == 10
        assert point.isclose(Vec2(10.0, -4.4074), abs_tol=1e-4)

    def test_horizontal_line_does_intersect_skewed_line(self):
        s1, s2 = Vec2(-10, 10), Vec2(10, 10)
        c1, c2 = Vec2(-10, 20), Vec2(10, 0)
        point, *_ = line_intersection(s1, s2, c1, c2)
        assert point.y == 10
        assert point.isclose(Vec2(0.0, 10.0), abs_tol=1e-4)

    def test_orthogonal_lines_do_intersect(self):
        s1, s2 = Vec2(-10, 10), Vec2(10, 10)
        c1, c2 = Vec2(5, 0), Vec2(5, 20)
        point, us, uc = line_intersection(s1, s2, c1, c2)
        assert point.y == 10
        assert point.x == 5
        assert point.isclose(Vec2(5.0, 10.0), abs_tol=1e-4)
        assert us == pytest.approx(0.75)
        assert uc == pytest.approx(0.5)

    def test_parallel_vertical_lines_do_not_intersect(self):
        s1, s2 = Vec2(10, 1), Vec2(10, -7)
        c1, c2 = Vec2(12, -10), Vec2(12, 7)
        assert line_intersection(s1, s2, c1, c2)[0] is None

    def test_parallel_horizontal_lines_do_not_intersect(self):
        s1, s2 = Vec2(11, 0), Vec2(-11, 0)
        c1, c2 = Vec2(0, 0), Vec2(1, 0)
        assert line_intersection(s1, s2, c1, c2)[0] is None

    def test_collinear_lines_do_not_intersect(self):
        s1, s2 = Vec2(0, 0), Vec2(4, 4)
        c1, c2 = Vec2(2, 2), Vec2(4, 0)
        assert line_intersection(s1, s2, c1, c2)[0] is None

    @pytest.mark.parametrize(
        "p2", [(4, 0), (0, 4), (4, 4)], ids=["horiz", "vert", "diag"]
    )
    def test_coincident_lines_do_not_intersect(self, p2):
        s1, s2 = Vec2(0, 0), Vec2(p2)
        assert line_intersection(s1, s2, s1, s2)[0] is None

    def test_virtual_intersection_is_not_an_intersection(self):
        s1, s2 = Vec2(0, 0), Vec2(4, 4)
        c1, c2 = Vec2(3, 2), Vec2(5, 0)
        assert line_intersection(s1, s2, c1, c2)[0] is None

    def test_issue_128(self):
        s1, s2 = Vec2(175.0, 5.0), Vec2(175.0, 50.0)
        c1, c2 = Vec2(-10.1231, 30.1235), Vec2(300.2344, 30.1235)
        point, *_ = line_intersection(s1, s2, c1, c2)
        assert point.isclose(Vec2(175.0, 30.1235))

    def test_issue_664(self):
        s1 = Vec2(16399619.87946683, -199438.8133075837)
        s2 = Vec2(16399700.34999472, -199438.8133075837)
        c1 = Vec2(16399659.76235549, -199423.8133075837)
        c2 = Vec2(16399659.76235549, -199463.8133075837)
        point, *_ = line_intersection(s1, s2, c1, c2)
        assert point.isclose(Vec2(16399659.76235549, -199438.8133075837))


@pytest.fixture
def rect():
    return Vec2.list([(-1, -1), (1, -1), (1, 1), (-1, 1)])


@pytest.fixture
def overlapping():  # overlapping
    return Vec2.list([(0, 0), (2, 0), (2, 2), (0, 2)])


@pytest.fixture
def inside():  # complete inside
    return Vec2.list([(0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5)])


@pytest.fixture
def outside():  # complete outside
    return Vec2.list([(2, 2), (3, 2), (3, 3), (2, 3)])


UNION_OVERLAPPING = Vec2.list(
    [
        (-1, -1),
        (1, -1),
        (1, 0),
        (2, 0),
        (2, 2),
        (0, 2),
        (0, 1),
        (-1, 1),
    ]
)

UNION_OUTSIDE = Vec2.list(
    [
        (-1, -1),
        (1, -1),
        (1, 1),
        (2, 0),
        (2, 2),
        (0, 2),
        (0, 1),
        (-1, 1),
    ]
)


class TestBooleanUnion:
    def test_overlapping_polygons_are_united(self, rect, overlapping):
        """The existence of real intersection points is the basic requirement
        to get the union operator to work.
        """
        polygons = greiner_hormann_union(rect, overlapping)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 9
        assert result[0] == result[-1], "expected closed polygon"
        assert set(UNION_OVERLAPPING) == set(result)

    def test_vertex_order_is_not_important(self, rect, overlapping):
        """The vertex order (clockwise or counter clockwise) is not important.
        """
        rect.reverse()
        result = greiner_hormann_union(rect, overlapping)[0]
        assert set(UNION_OVERLAPPING) == set(result)

        overlapping.reverse()
        result = greiner_hormann_union(rect, overlapping)[0]
        assert set(UNION_OVERLAPPING) == set(result)

    def test_a_polygon_inside_another_polygon_is_ignored(self, rect, inside):
        """This polygons do not have any intersection points and therefore no
        union is calculated - which could interpreted as the expected result.
        """
        polygons = greiner_hormann_union(rect, inside)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        assert result[0] == result[-1], "expected closed polygon"
        assert set(rect) == set(result)

    def test_a_failed_union_returns_the_first_polygon(self, rect, outside):
        polygons = greiner_hormann_union(rect, outside)
        result = polygons[0]
        assert set(rect) == set(result)

    def test_disconnected_polygons_cannot_be_united(self, rect):
        result = greiner_hormann_union(rect, circle(16, 3))[0]
        assert set(rect) == set(result)

    def test_overlapping_but_collinear_edges_cannot_be_united(self, rect):
        """As shown in the intersection tests, collinear lines do not intersect,
        and this algorithm relies on intersections to produce a union.
        """
        offset = Vec2(1.5, 0)
        rect2 = [offset + v for v in rect]
        polygons = greiner_hormann_union(rect, rect2)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        # no intersection == no union
        # the union operator returns the source polygon:
        assert set(rect) == set(result)

    def test_polygons_with_a_shared_edge_cannot_be_united(self, rect):
        """As shown in the intersection tests, collinear lines do not intersect,
        and this algorithm relies on intersections to produce a union.
        """
        offset = Vec2(2, 0)
        rect2 = [offset + v for v in rect]
        polygons = greiner_hormann_union(rect, rect2)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        # no intersection == no union
        # the union operator returns the source polygon:
        assert set(rect) == set(result)


DIFF_OVERLAPPING = [
    Vec2(-1, -1),
    Vec2(1, -1),
    Vec2(1, 0),
    Vec2(0, 0),
    Vec2(0, 1),
    Vec2(-1, 1),
]


class TestBooleanDifference:
    def test_difference_of_overlapping_polygons(self, rect, overlapping):
        """The existence of real intersection points is the basic requirement
        to get the difference operator to work.
        """
        polygons = greiner_hormann_difference(rect, overlapping)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 7
        assert result[0] == result[-1], "expected closed polygon"
        assert set(DIFF_OVERLAPPING) == set(result)

    def test_polygon_inside_polygon(self, rect, inside):
        """This polygons do not have any intersection points and therefore no
        difference is calculated - which is NOT the expected result.
        """
        polygons = greiner_hormann_difference(rect, inside)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        assert set(rect) == set(result)

    def test_polygon_inside_polygon_reverse_difference(self, rect, inside):
        """This polygons do not have any intersection points and therefore no
        difference is calculated - which is NOT the expected result.
        """
        result = greiner_hormann_difference(inside, rect)[0]
        assert len(result) == 5
        assert set(inside) == set(result)

    def test_polygon_outside_polygon(self, rect, outside):
        """This polygons do not have any intersection points and therefore no
        difference is calculated - which could interpreted as the expected result.
        """
        polygons = greiner_hormann_difference(rect, outside)
        result = polygons[0]
        assert set(rect) == set(result)


INTERSECT_OVERLAPPING = [
    Vec2(0, 0),
    Vec2(1, 0),
    Vec2(1, 1),
    Vec2(0, 1),
]


class TestBooleanIntersection:
    def test_intersection_of_overlapping_polygons(self, rect, overlapping):
        """The existence of real intersection points is the basic requirement
        to get the intersection operator to work.
        """
        polygons = greiner_hormann_intersection(rect, overlapping)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        assert result[0] == result[-1], "expected closed polygon"
        assert set(INTERSECT_OVERLAPPING) == set(result)

    def test_polygon_inside_polygon(self, rect, inside):
        """This polygons do not have any intersection points and therefore no
        intersection is calculated - which is NOT the expected result.
        """
        polygons = greiner_hormann_intersection(rect, inside)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        assert set(rect) == set(result)

    def test_polygon_outside_polygon(self, rect, outside):
        """This polygons do not have any intersection points and therefore no
        intersection is calculated - which could interpreted as the expected result.
        """
        polygons = greiner_hormann_intersection(rect, outside)
        result = polygons[0]
        assert set(rect) == set(result)


if __name__ == "__main__":
    pytest.main([__file__])
