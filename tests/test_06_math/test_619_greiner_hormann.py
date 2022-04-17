#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec2
from ezdxf.math.clipping import greiner_hormann_intersection
from ezdxf.render.forms import circle


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


class TestIntersection:
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
