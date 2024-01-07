#  Copyright (c) 2023-2024, Manfred Moitzi
#  License: MIT License
import pytest
import math

from ezdxf.tools.clipping_portal import ClippingRect, MultiClip
from ezdxf.math import Vec2
from ezdxf import npshapes


class TestClippingRect:
    def test_clipping_points(self):
        clipper = ClippingRect([(-1, -1), (1, 1)])
        assert clipper.clip_point(Vec2(3, 3)) is None
        assert clipper.clip_point(Vec2(0.5, 0.5)).isclose((0.5, 0.5))  # type: ignore

    def test_clipping_lines(self):
        clipper = ClippingRect([(-1, -1), (1, 1)])
        cropped_segments = clipper.clip_line(Vec2(-3, 0), Vec2(3, 0))
        assert len(cropped_segments) == 1

        points = cropped_segments[0]
        assert len(points) == 2
        start, end = points
        assert start.isclose((-1, 0))
        assert end.isclose((1, 0))

    def test_clip_polyline(self):
        clipper = ClippingRect([(-2, -2), (2, 2)])
        polyline = npshapes.NumpyPoints2d(Vec2.list([(0, 1), (3, 0), (0, -1)]))
        polygons = clipper.clip_polygon(polyline)
        assert len(polygons) == 1
        assert len(polygons[0]) == 4


class TestMultiClip:
    @pytest.fixture
    def multi_clip(self) -> MultiClip:
        return MultiClip(
            [
                ClippingRect([(0, 0), (1, 1)]),
                ClippingRect([(2, 0), (3, 1)]),
            ]
        )

    def test_extents(self, multi_clip: MultiClip) -> None:
        bbox = multi_clip.bbox()
        assert bbox.extmin.isclose((0, 0))
        assert bbox.extmax.isclose((3, 1))

    def test_remove_empty_clipping_shapes(self):
        r0 = ClippingRect([(0.5, 0.5), (0.5, 0.5)])
        r1 = ClippingRect([(0, 0), (3, 1)])
        multi_clip = MultiClip([r0, r1])
        shapes = multi_clip.shapes_in_range(multi_clip.bbox())
        assert len(shapes) == 1
        assert shapes[0] is r1

    @pytest.mark.parametrize(
        "point",
        Vec2.list([(0.5, 0.5), (2.5, 0.5), (0, 0), (1, 1), (2, 0), (3, 1)]),
    )
    def test_point_inside(self, multi_clip: MultiClip, point: Vec2) -> None:
        assert point.isclose(multi_clip.clip_point(point))

    @pytest.mark.parametrize(
        "point",
        Vec2.list([(-1, 0.5), (1.5, 0.5), (3.5, 0)]),
    )
    def test_point_outside(self, multi_clip: MultiClip, point: Vec2) -> None:
        assert multi_clip.clip_point(point) is None

    def test_clip_line_1(self, multi_clip: MultiClip) -> None:
        parts = list(multi_clip.clip_line(Vec2(0.5, 0.5), Vec2(2.5, 0.5)))
        assert len(parts) == 2
        assert math.isclose(sum(v0.distance(v1) for v0, v1 in parts), 1.0)

    def test_clip_line_2(self, multi_clip: MultiClip) -> None:
        parts = list(multi_clip.clip_line(Vec2(-0.5, 0.5), Vec2(3.5, 0.5)))
        assert len(parts) == 2
        assert math.isclose(sum(v0.distance(v1) for v0, v1 in parts), 2.0)


if __name__ == "__main__":
    pytest.main([__file__])
