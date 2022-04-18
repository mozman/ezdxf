#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec2
from ezdxf.math.clipping import (
    greiner_hormann_union,
    greiner_hormann_difference,
    greiner_hormann_intersection,
    line_intersection,
    IntersectionError,
)
from ezdxf.render.forms import circle, translate


class TestLineIntersection:
    def test_intersect_vertical_line(self):
        s1, s2 = Vec2(10, 1), Vec2(10, -7)
        c1, c2 = Vec2(-10, 3), Vec2(17, -7)
        point, *_ = line_intersection(s1, s2, c1, c2)
        assert point.x == 10
        assert point.isclose(Vec2(10.0, -4.4074), abs_tol=1e-4)

    def test_intersect_horizontal_line(self):
        s1, s2 = Vec2(-10, 10), Vec2(10, 10)
        c1, c2 = Vec2(-10, 20), Vec2(10, 0)
        point, *_ = line_intersection(s1, s2, c1, c2)
        assert point.y == 10
        assert point.isclose(Vec2(0.0, 10.0), abs_tol=1e-4)

    def test_intersect_orthogonal_lines(self):
        s1, s2 = Vec2(-10, 10), Vec2(10, 10)
        c1, c2 = Vec2(5, 0), Vec2(5, 20)
        point, us, uc = line_intersection(s1, s2, c1, c2)
        assert point.y == 10
        assert point.x == 5
        assert point.isclose(Vec2(5.0, 10.0), abs_tol=1e-4)
        assert us == pytest.approx(0.75)
        assert uc == pytest.approx(0.5)

    def test_intersect_parallel_vertical_lines(self):
        s1, s2 = Vec2(10, 1), Vec2(10, -7)
        c1, c2 = Vec2(12, -10), Vec2(12, 7)
        with pytest.raises(IntersectionError):
            line_intersection(s1, s2, c1, c2)

    def test_intersect_parallel_horizontal_lines(self):
        s1, s2 = Vec2(11, 0), Vec2(-11, 0)
        c1, c2 = Vec2(0, 0), Vec2(1, 0)
        with pytest.raises(IntersectionError):
            line_intersection(s1, s2, c1, c2)

    def test_intersect_real_colinear(self):
        s1, s2 = Vec2(0, 0), Vec2(4, 4)
        c1, c2 = Vec2(2, 2), Vec2(4, 0)
        point, *_ = line_intersection(s1, s2, c1, c2)
        assert point.isclose(Vec2(2, 2))

    @pytest.mark.parametrize(
        "p2", [(4, 0), (0, 4), (4, 4)], ids=["horiz", "vert", "diag"]
    )
    def test_intersect_coincident_lines(self, p2):
        s1, s2 = Vec2(0, 0), Vec2(p2)
        with pytest.raises(IntersectionError):
            line_intersection(s1, s2, s1, s2)

    def test_virtual_intersection(self):
        s1, s2 = Vec2(0, 0), Vec2(4, 4)
        c1, c2 = Vec2(3, 2), Vec2(5, 0)
        with pytest.raises(IntersectionError):
            line_intersection(s1, s2, c1, c2)

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
    return [(-1, -1), (1, -1), (1, 1), (-1, 1)]


@pytest.fixture
def overlapping():  # overlapping
    return [(0, 0), (2, 0), (2, 2), (0, 2)]


@pytest.fixture
def inside():  # complete inside
    return [(0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5)]


@pytest.fixture
def outside():  # complete outside
    return [(2, 2), (3, 2), (3, 3), (2, 3)]


UNION_OVERLAPPING = [
    Vec2(-1, -1),
    Vec2(1, -1),
    Vec2(1, 0),
    Vec2(2, 0),
    Vec2(2, 2),
    Vec2(0, 2),
    Vec2(0, 1),
    Vec2(-1, 1),
]

UNION_OUTSIDE = [
    Vec2(-1, -1),
    Vec2(1, -1),
    Vec2(1, 1),
    Vec2(2, 0),
    Vec2(2, 2),
    Vec2(0, 2),
    Vec2(0, 1),
    Vec2(-1, 1),
]


class TestBooleanUnion:
    def test_overlapping_rectangles(self, rect, overlapping):
        polygons = greiner_hormann_union(rect, overlapping)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 9
        assert result[0] == result[-1], "expected closed polygon"
        assert set(UNION_OVERLAPPING) == set(result)

    def test_polygon_orientation_is_not_important(self, rect, overlapping):
        rect.reverse()
        result = greiner_hormann_union(rect, overlapping)[0]
        assert set(UNION_OVERLAPPING) == set(result)

        overlapping.reverse()
        result = greiner_hormann_union(rect, overlapping)[0]
        assert set(UNION_OVERLAPPING) == set(result)

    def test_subject_inside_rect(self, rect, inside):
        polygons = greiner_hormann_union(rect, inside)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        assert result[0] == result[-1], "expected closed polygon"
        assert set(rect) == set(result)

    def test_subject_is_outside_rect(self, rect, outside):
        """Returns the subject polygon `p1`."""
        polygons = greiner_hormann_union(rect, outside)
        result = polygons[0]
        assert set(rect) == set(result)

    def test_circle_outside_rect(self, rect):
        """Returns the subject polygon `p1`."""
        result = greiner_hormann_union(rect, circle(16, 3))[0]
        assert set(rect) == set(result)

    def test_overlapping_adjacent_rects(self, rect):
        """Algorithm returns weired results for this case!

        Collinear edges seem to be an issue.
        """
        offset = Vec2(1.5, 0)
        rect2 = [offset + v for v in rect]
        polygons = greiner_hormann_union(rect, rect2)
        assert len(polygons) == 2  # and what now? This result is weired!

    def test_non_overlapping_adjacent_rects(self, rect):
        """Algorithm does not recognize non overlapping adjacent figures!"""
        offset = Vec2(2, 0)
        rect2 = [offset + v for v in rect]
        polygons = greiner_hormann_union(rect, rect2)
        result = polygons[0]
        assert len(result) == 5
        # No union of the two rectangles is done, I expected more from this
        # algorithm!?
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
    def test_overlapping_rectangles(self, rect, overlapping):
        polygons = greiner_hormann_difference(rect, overlapping)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 7
        assert result[0] == result[-1], "expected closed polygon"
        assert set(DIFF_OVERLAPPING) == set(result)

    def test_polygon_orientation_is_not_important(self, rect, overlapping):
        rect.reverse()
        result = greiner_hormann_difference(rect, overlapping)[0]
        assert set(DIFF_OVERLAPPING) == set(result)

        overlapping.reverse()
        result = greiner_hormann_difference(rect, overlapping)[0]
        assert set(DIFF_OVERLAPPING) == set(result)

    def test_subject_inside_rect(self, rect, inside):
        """This algorthm can not handle holes:

        This returns always the "subject" polygon p1.

        """
        polygons = greiner_hormann_difference(rect, inside)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        assert set(rect) == set(result)

    def test_subject_inside_rect_reverse_difference(self, rect, inside):
        """This algorthm can not handle holes:

        This returns always the "subject" polygon p1.

        """
        result = greiner_hormann_difference(inside, rect)[0]
        assert len(result) == 5
        assert set(inside) == set(result)

    def test_subject_is_outside_rect(self, rect, outside):
        """Returns the subject polygon `p1`."""
        polygons = greiner_hormann_difference(rect, outside)
        result = polygons[0]
        assert set(rect) == set(result)

    def test_circle_outside_rect(self, rect):
        """Returns the subject polygon `p1`."""
        result = greiner_hormann_difference(rect, circle(16, 3))[0]
        assert set(rect) == set(result)


INTERSECT_OVERLAPPING = [
    Vec2(0, 0),
    Vec2(1, 0),
    Vec2(1, 1),
    Vec2(0, 1),
]


class TestBooleanIntersection:
    def test_overlapping_rectangles(self, rect, overlapping):
        polygons = greiner_hormann_intersection(rect, overlapping)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        assert result[0] == result[-1], "expected closed polygon"
        assert set(INTERSECT_OVERLAPPING) == set(result)

    def test_polygon_orientation_is_not_important(self, rect, overlapping):
        rect.reverse()
        result = greiner_hormann_intersection(rect, overlapping)[0]
        assert set(INTERSECT_OVERLAPPING) == set(result)

        overlapping.reverse()
        result = greiner_hormann_intersection(rect, overlapping)[0]
        assert set(INTERSECT_OVERLAPPING) == set(result)

    def test_subject_inside_rect(self, rect, inside):
        """This algorthm can not handle holes:

        This returns always the "subject" polygon p1.

        """
        polygons = greiner_hormann_intersection(rect, inside)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        assert set(rect) == set(result)

    def test_subject_is_outside_rect(self, rect, outside):
        """Returns the subject polygon `p1`."""
        polygons = greiner_hormann_intersection(rect, outside)
        result = polygons[0]
        assert set(rect) == set(result)

    def test_circle_outside_rect(self, rect):
        """Returns the subject polygon `p1`."""
        result = greiner_hormann_intersection(rect, circle(16, 3))[0]
        assert set(rect) == set(result)


if __name__ == "__main__":
    pytest.main([__file__])
