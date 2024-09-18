#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec2, BoundingBox2d
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
        s1, s2 = Vec2(0, 0), Vec2(2, 2)
        c1, c2 = Vec2(3, 3), Vec2(4, 4)
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
        """The vertex order (clockwise or counter clockwise) is not important."""
        rect.reverse()
        result = greiner_hormann_union(rect, overlapping)[0]
        assert set(UNION_OVERLAPPING) == set(result)

        overlapping.reverse()
        result = greiner_hormann_union(rect, overlapping)[0]
        assert set(UNION_OVERLAPPING) == set(result)

    def test_a_polygon_inside_another_polygon_is_ignored(self, rect, inside):
        """This polygons do not have any intersection points and therefore no
        union is calculated.
        """
        assert len(greiner_hormann_union(rect, inside)) == 0

    def test_a_failed_union_returns_an_empty_list(self, rect, outside):
        assert len(greiner_hormann_union(rect, outside)) == 0

    def test_disconnected_polygons_cannot_be_united(self, rect):
        assert len(greiner_hormann_union(rect, circle(16, 3))) == 0

    def test_overlapping_but_collinear_edges_cannot_be_united(self, rect):
        """As shown in the intersection tests, collinear lines do not intersect,
        and this algorithm relies on intersections to produce a union.
        """
        offset = Vec2(1.5, 0)
        rect2 = [offset + v for v in rect]
        assert len(greiner_hormann_union(rect, rect2)) == 0

    def test_polygons_with_a_shared_edge_cannot_be_united(self, rect):
        """As shown in the intersection tests, collinear lines do not intersect,
        and this algorithm relies on intersections to produce a union.
        """
        offset = Vec2(2, 0)
        rect2 = [offset + v for v in rect]
        assert len(greiner_hormann_union(rect, rect2)) == 0


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
        difference is calculated - which is NOT the expected result
        (expected a rect with a hole)
        """
        assert len(greiner_hormann_difference(rect, inside)) == 0

    def test_polygon_inside_polygon_reverse_difference(self, rect, inside):
        """This polygons do not have any intersection points and therefore no
        difference is calculated - which IS the expected result
        (subtracting the bigger rect from the smaller rect returns nothing)
        """
        assert len(greiner_hormann_difference(inside, rect)) == 0

    def test_polygon_outside_polygon(self, rect, outside):
        """This polygons do not have any intersection points and therefore no
        difference is calculated - which is NOT the expected result
        (expected rect)
        """
        assert len(greiner_hormann_difference(rect, outside)) == 0


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
        intersection is calculated - which is NOT the expected result
        (expected the inside rect)
        """
        assert len(greiner_hormann_intersection(rect, inside)) == 0

    def test_polygon_outside_polygon(self, rect, outside):
        """This polygons do not have any intersection points and therefore no
        intersection is calculated - which could interpreted as the expected
        result.
        """
        assert len(greiner_hormann_intersection(rect, outside)) == 0


DATA_1094 = [
    Vec2.list(
        [
            [-18.900001889999952, 1450.7000002308125],
            [-18.900001889999952, 1470.7351470734998],
            [1278.90012789, 1470.7351470734998],
            [1278.90012789, 1450.70001562087],
            [1503.6001841952093, 1450.7000156208703],
            [1503.6001841952093, 1388.3850000081884],
            [1503.6001841952093, 1388.3850000081884],
            [1647.3246376764234, 1388.3850000081884],
            [1647.3246376764234, 1548.1475422037274],
            [1831.0471719722357, 1548.1475422037274],
            [1831.0471719722357, 1388.3850000081884],
            [1831.0471719722357, 1388.3850000081884],
            [1980.6216566984945, 1388.3850000081884],
            [1980.6216566984945, 1224.6149999918116],
            [1831.0471719722357, 1224.6149999918116],
            [1831.0471719722357, 1160.3525263520064],
            [1647.3246376764234, 1160.3525263520064],
            [1647.3246376764234, 1160.3525263520064],
            [1647.3246376764234, 1224.6149999918116],
            [1647.3246376764234, 1224.6149999918116],
            [1503.6001841952093, 1224.6149999918116],
            [1503.6001841952093, 1162.2999997691875],
            [1278.90012789, 1162.2999997691877],
            [1278.90012789, 1162.2999997691877],
            [1278.90012789, 286.7000156208702],
            [1503.6001841952093, 286.70001562087026],
            [1503.6001841952093, 224.3850000081885],
            [1503.6001841952093, 224.3850000081885],
            [1647.3246376764234, 224.3850000081885],
            [1647.3246376764234, 384.1475422037275],
            [1831.0471719722357, 384.1475422037275],
            [1831.0471719722357, 224.3850000081885],
            [1831.0471719722357, 224.3850000081885],
            [1980.6216566984945, 224.3850000081885],
            [1980.6216566984945, 60.61499999181149],
            [1831.0471719722357, 60.614999991811544],
            [1831.0471719722357, -3.6474736479937064],
            [1647.3246376764234, -3.6474736479937064],
            [1647.3246376764234, -3.6474736479937064],
            [1647.3246376764234, 60.61499999181149],
            [1647.3246376764234, 60.61499999181149],
            [1503.6001841952093, 60.61499999181149],
            [1503.6001841952093, -1.7000002308124635],
            [1278.90012789, -1.7000002308124635],
            [1278.90012789, -1.7000002308124635],
            [1278.90012789, -21.735002173499993],
            [-18.900001890000045, -21.735002173499993],
            [-18.900001890000045, -21.735002173499993],
            [-18.900001890000045, -1.7000156208705448],
            [-243.6001841952094, -1.7000156208702606],
            [-243.6001841952094, -1.7000156208702606],
            [-243.6001841952094, 60.61499999181149],
            [-243.6001841952094, 60.61499999181149],
            [-237.7502641782885, 60.61499999181149],
            [-237.7502641782885, 224.3850000081885],
            [-243.6001841952094, 224.3850000081885],
            [-243.6001841952094, 286.70000023081246],
            [-18.900001890000027, 286.7000002308125],
            [-18.900001890000027, 286.7000002308125],
            [-18.90000188999997, 1162.2999843791297],
            [-243.6001841952094, 1162.2999843791297],
            [-243.6001841952094, 1162.2999843791297],
            [-243.6001841952094, 1450.7000002308125],
            [-18.900001889999952, 1450.7000002308125],
        ]
    ),
    Vec2.list(
        [
            [-392.2502641782885, 1224.6149999918116],
            [-237.7502641782885, 1224.6149999918116],
            [-237.7502641782885, 1388.3850000081884],
            [-392.2502641782885, 1388.3850000081884],
            [-392.2502641782885, 1224.6149999918116],
        ]
    ),
]


def test_issue_1094_is_inside_polygon_function_was_incorrect():
    data = DATA_1094
    box_expected = BoundingBox2d(data[0] + data[1])
    result = greiner_hormann_union(data[0], data[1])

    assert len(result) == 1
    box_result = BoundingBox2d(result[0])
    assert box_result.extmin.isclose(box_expected.extmin)
    assert box_result.extmax.isclose(box_expected.extmax)


if __name__ == "__main__":
    pytest.main([__file__])
