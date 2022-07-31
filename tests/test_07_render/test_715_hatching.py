#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from ezdxf.math import Vec2

import pytest
from ezdxf.render import hatching


class TestHatchBaseLine:
    @pytest.fixture
    def horizontal_baseline(self):
        return hatching.HatchBaseLine(
            Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1)
        )

    def test_positive_line_distance(self):
        line = hatching.HatchBaseLine(
            origin=Vec2((1, 2)), direction=Vec2(2, 0), offset=Vec2(2, 2)
        )
        assert line.normal_distance == pytest.approx(2.0)

    def test_negative_line_distance(self):
        line = hatching.HatchBaseLine(
            origin=Vec2((1, 2)), direction=Vec2(2, 0), offset=Vec2(2, -2)
        )
        assert line.normal_distance == pytest.approx(-2.0)

    def test_hatch_line_direction_error(self):
        with pytest.raises(hatching.HatchLineDirectionError):
            hatching.HatchBaseLine(Vec2(), direction=Vec2(), offset=Vec2(1, 0))

    def test_dense_hatching_error(self):
        with pytest.raises(hatching.DenseHatchingLinesError):
            hatching.HatchBaseLine(
                Vec2(), direction=Vec2(1, 0), offset=Vec2(1, 0)
            )
        with pytest.raises(hatching.DenseHatchingLinesError):
            hatching.HatchBaseLine(
                Vec2(), direction=Vec2(1, 0), offset=Vec2(-1, 0)
            )

    def test_no_offset_error(self):
        with pytest.raises(hatching.DenseHatchingLinesError):
            hatching.HatchBaseLine(
                Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 0)
            )

    def test_very_small_offset_error(self):
        with pytest.raises(hatching.DenseHatchingLinesError):
            hatching.HatchBaseLine(
                Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1e-6)
            )

    def test_intersect_triangle_0(self, horizontal_baseline):
        triangle = Vec2.list([(1, 0), (2, 0), (1, 1)])
        lines = list(
            horizontal_baseline.hatch_lines_intersecting_triangle(triangle)
        )
        assert len(lines) == 1

    def test_intersect_triangle_1(self, horizontal_baseline):
        triangle = Vec2.list([(1, 0.5), (2, 0.5), (1, 1.5)])
        lines = list(
            horizontal_baseline.hatch_lines_intersecting_triangle(triangle)
        )
        assert len(lines) == 1
        l0 = lines[0]
        assert l0.start.isclose((1.5, 1))
        assert l0.end.isclose((1, 1))


class TestHatchLine:
    @pytest.fixture
    def horizontal_baseline(self):
        return hatching.HatchBaseLine(
            Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1)
        )

    def test_intersect_line_collinear(self, horizontal_baseline):
        a = Vec2(3, 0)
        b = Vec2(10, 0)
        distance = 0
        hatch_line = horizontal_baseline.hatch_line(distance)
        ip = hatch_line.intersect_line(a, b, distance, distance)
        assert ip.type == hatching.IntersectionType.COLLINEAR
        assert ip.p0 is a
        assert ip.p1 is b

    def test_intersect_line_start(self, horizontal_baseline):
        a = Vec2(0, 0)
        b = Vec2(0, 10)

        hatch_line = horizontal_baseline.hatch_line(0)
        ip = hatch_line.intersect_line(a, b, 0, 10)
        assert ip.type == hatching.IntersectionType.START
        assert ip.p0 is a

    def test_intersect_line_end(self, horizontal_baseline):
        a = Vec2(0, 0)
        b = Vec2(0, 10)

        hatch_line = horizontal_baseline.hatch_line(10)
        ip = hatch_line.intersect_line(a, b, 0, 10)
        assert ip.type == hatching.IntersectionType.END
        assert ip.p0 is b

    @pytest.mark.parametrize("d", [-2, 0, 6])
    def test_intersect_line_regular(self, horizontal_baseline, d):
        a = Vec2(4, -3)
        b = Vec2(4, 7)
        dist_a = horizontal_baseline.signed_point_distance(a)
        dist_b = horizontal_baseline.signed_point_distance(b)

        hatch_line = horizontal_baseline.hatch_line(d)
        ip = hatch_line.intersect_line(a, b, dist_a, dist_b)
        assert ip.type == hatching.IntersectionType.REGULAR
        assert ip.p0.isclose((4, d))


if __name__ == "__main__":
    pytest.main([__file__])
