#  Copyright (c) 2021-2024, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import pytest
from ezdxf.math import Vec2
from ezdxf.math.clipping import (
    ConvexClippingPolygon2d,
    ClippingRect2d,
    Clipping,
)
from ezdxf.render.forms import circle


class TestClipSingleLineAtConvexBoundary:
    @pytest.fixture(scope="class", params=["polygon", "rect"])
    def clipper(self, request):
        if request.param == "polygon":
            return ConvexClippingPolygon2d(Vec2.list([(0, 0), (2, 0), (2, 2), (0, 2)]))
        else:
            return ClippingRect2d(Vec2(0, 0), Vec2(2, 2))

    def test_no_clipping(self, clipper):
        assert len(clipper.clip_line(Vec2(-1, 3), Vec2(3, 3))) == 0  # above
        assert len(clipper.clip_line(Vec2(-1, -1), Vec2(3, -1))) == 0  # below
        assert len(clipper.clip_line(Vec2(-1, 0), Vec2(-1, 2))) == 0  # left
        assert len(clipper.clip_line(Vec2(3, 0), Vec2(3, 2))) == 0  # right

    def test_regular_clip_inside_outside(self, clipper: Clipping):
        s, e = clipper.clip_line(Vec2(1, 1), Vec2(3, 1))[0]
        assert s.isclose((1, 1))
        assert e.isclose((2, 1))

    def test_regular_clip_outside_inside(self, clipper: Clipping):
        s, e = clipper.clip_line(Vec2(3, 1), Vec2(1, 1))[0]
        assert s.isclose((2, 1))
        assert e.isclose((1, 1))

    def test_crossing_horizontal_left_to_right(self, clipper: Clipping):
        s, e = clipper.clip_line(Vec2(-1, 1), Vec2(3, 1))[0]
        assert s.isclose((0, 1))
        assert e.isclose((2, 1))

    def test_crossing_horizontal_right_to_left(self, clipper: Clipping):
        s, e = clipper.clip_line(Vec2(3, 1), Vec2(-1, 1))[0]
        assert s.isclose((2, 1))
        assert e.isclose((0, 1))

    def test_crossing_vertical(self, clipper: Clipping):
        s, e = clipper.clip_line(Vec2(1, -1), Vec2(1, 3))[0]
        assert s.isclose((1, 0))
        assert e.isclose((1, 2))

    def test_crossing_diagonal(self, clipper: Clipping):
        s, e = clipper.clip_line(Vec2(-1, 0), Vec2(2, 3))[0]
        assert s.isclose((0, 1))
        assert e.isclose((1, 2))

    def test_crossing_diagonal_edge_to_edge(self, clipper: Clipping):
        s, e = clipper.clip_line(Vec2(0, 0), Vec2(2, 2))[0]
        assert s.isclose((0, 0))
        assert e.isclose((2, 2))

    @pytest.mark.parametrize("y", [0, 2], ids=["bottom", "top"])
    def test_colinear_horizontal_edge(self, clipper: Clipping, y: int):
        s, e = clipper.clip_line(Vec2(-1, y), Vec2(3, y))[0]
        assert s.isclose((0, y))
        assert e.isclose((2, y))

    @pytest.mark.parametrize("x", [0, 2], ids=["left", "right"])
    def test_colinear_vertical_edge(self, clipper: Clipping, x: int):
        s, e = clipper.clip_line(Vec2(x, -1), Vec2(x, 3))[0]
        assert s.isclose((x, 0))
        assert e.isclose((x, 2))


class TestClipPolylineAtConvexBoundary:
    @pytest.fixture(scope="class", params=["polygon", "rect"])
    def clipper(self, request):
        if request.param == "polygon":
            return ConvexClippingPolygon2d(Vec2.list([(0, 0), (8, 0), (8, 2), (0, 2)]))
        else:
            return ClippingRect2d(Vec2(0, 0), Vec2(8, 2))

    def test_crossing_zigzag(self, clipper: Clipping):
        p0, p1 = clipper.clip_polyline(Vec2.list([(0, -1), (4, 3), (8, -1)]))
        assert p0[0].isclose((1, 0))
        assert p0[1].isclose((3, 2))
        assert p1[0].isclose((5, 2))
        assert p1[1].isclose((7, 0))


class TestClipPolygonAtConvexBoundary:
    @pytest.fixture(scope="class", params=["polygon", "rect"])
    def clipper(self, request):
        if request.param == "polygon":
            return ConvexClippingPolygon2d(
                Vec2.list([(-1, -1), (1, -1), (1, 1), (-1, 1)])
            )
        else:
            return ClippingRect2d(Vec2(-1, -1), Vec2(1, 1))

    @pytest.fixture
    def rect(self):
        return Vec2.list([(-1, -1), (1, -1), (1, 1), (-1, 1)])

    @pytest.fixture
    def overlapping(self):  # overlapping
        return Vec2.list([(0, 0), (2, 0), (2, 2), (0, 2)])

    @pytest.fixture
    def inside(self):  # complete inside
        return Vec2.list([(0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5)])

    @pytest.fixture
    def outside(self):  # complete outside
        return Vec2.list([(1, 1), (2, 1), (2, 2), (1, 2)])

    def test_subject_do_overlap_clipping_rect(
        self, clipper: Clipping, overlapping: list[Vec2]
    ):
        result = clipper.clip_polygon(overlapping)[0]
        assert len(result) == 4
        assert Vec2(0, 0) in result
        assert Vec2(1, 0) in result
        assert Vec2(1, 1) in result
        assert Vec2(0, 1) in result

    def test_subject_is_inside_rect(self, clipper: Clipping, inside: list[Vec2]):
        result = clipper.clip_polygon(inside)[0]
        assert len(result) == 4
        for v in inside:
            assert any(r.isclose(v) for r in result) is True

    def test_clockwise_oriented_clipping_rect(
        self, rect: list[Vec2], inside: list[Vec2]
    ):
        rect.reverse()
        clipper = ConvexClippingPolygon2d(rect)
        result = clipper.clip_polygon(inside)[0]
        assert len(result) == 4
        for v in inside:
            assert any(r.isclose(v) for r in result) is True

    def test_subject_is_outside_rect(self, clipper: Clipping, outside: list[Vec2]):
        result = clipper.clip_polygon(outside)[0]
        assert len(result) == 0

    def test_circle_outside_rect(self, clipper: Clipping, rect: list[Vec2]):
        c = Vec2.list(circle(16, 3))
        result = clipper.clip_polygon(c)[0]
        assert len(result) == 4
        for v in rect:
            assert any(r.isclose(v) for r in result) is True

    def test_circle_inside_rect(self, clipper: Clipping):
        c = Vec2.list(circle(16, 0.7))
        result = clipper.clip_polygon(c)[0]
        assert len(result) == 16
        for v in c:
            assert any(r.isclose(v) for r in result) is True

    def test_rect_outside_circle(self, rect: list[Vec2]):
        c = Vec2.list(circle(16, 0.7))
        clipper = ConvexClippingPolygon2d(c)
        result = clipper.clip_polygon(rect)[0]
        assert len(result) == 16
        for v in c:
            assert any(r.isclose(v) for r in result) is True

    def test_rect_inside_circle(self, rect: list[Vec2]):
        c = Vec2.list(circle(16, 3))
        clipper = ConvexClippingPolygon2d(c)
        result = clipper.clip_polygon(rect)[0]
        assert len(result) == 4
        for v in rect:
            assert any(r.isclose(v) for r in result) is True


if __name__ == "__main__":
    pytest.main([__file__])
