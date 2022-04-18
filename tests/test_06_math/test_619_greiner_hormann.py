#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec2
from ezdxf.math.clipping import (
    greiner_hormann_intersection,
    line_intersection,
    IntersectionError,
)
from ezdxf.render.forms import circle


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
    return [(1, 1), (2, 1), (2, 2), (1, 2)]


class TestBooleanIntersection:
    def test_subject_do_overlap_clipping_rect(self, rect, overlapping):
        polygons = greiner_hormann_intersection(rect, overlapping)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 5
        assert result[0] == result[-1]
        assert Vec2(0, 0) in result
        assert Vec2(1, 0) in result
        assert Vec2(1, 1) in result
        assert Vec2(0, 1) in result

    def test_subject_is_inside_rect(self, rect, inside):
        polygons = greiner_hormann_intersection(rect, inside)
        assert len(polygons) == 1
        result = polygons[0]
        assert len(result) == 4
        for v in inside:
            assert Vec2(v) in result

    def test_clockwise_oriented_clipping_rect(self, rect, inside):
        rect.reverse()
        polygons = greiner_hormann_intersection(rect, inside)
        result = polygons[0]
        assert len(result) == 4
        for v in inside:
            assert Vec2(v) in result

    def test_subject_is_outside_rect(self, rect, outside):
        polygons = greiner_hormann_intersection(rect, outside)
        result = polygons[0]
        assert len(result) == 0

    def test_circle_outside_rect(self, rect):
        c = circle(16, 3)
        polygons = greiner_hormann_intersection(rect, c)
        result = polygons[0]
        assert len(result) == 4
        for v in rect:
            assert Vec2(v) in result

    def test_circle_inside_rect(self, rect):
        c = Vec2.list(circle(16, 0.7))
        polygons = greiner_hormann_intersection(rect, c)
        result = polygons[0]
        assert len(result) == 16
        for v in c:
            assert Vec2(v) in result

    def test_rect_outside_circle(self, rect):
        c = circle(16, 0.7)
        polygons = greiner_hormann_intersection(rect, c)
        result = polygons[0]
        assert len(result) == 16
        for v in c:
            assert Vec2(v) in result

    def test_rect_inside_circle(self, rect):
        c = circle(16, 3)
        polygons = greiner_hormann_intersection(rect, c)
        result = polygons[0]
        assert len(result) == 4
        for v in rect:
            assert Vec2(v) in result


if __name__ == "__main__":
    pytest.main([__file__])
