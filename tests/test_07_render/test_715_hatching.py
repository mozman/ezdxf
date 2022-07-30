#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from ezdxf.math import Vec2

import pytest
from ezdxf.render import hatching


class TestHatchBaseLine:
    @pytest.fixture
    def horizontal_pattern(self):
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

    def test_horizontal_pattern_0(self, horizontal_pattern):
        triangle = Vec2.list([(1, 0), (2, 0), (1, 1)])
        lines = list(
            horizontal_pattern.hatch_lines_intersecting_triangle(triangle)
        )
        assert len(lines) == 1

    def test_horizontal_pattern_1(self, horizontal_pattern):
        triangle = Vec2.list([(1, 0.5), (2, 0.5), (1, 1.5)])
        lines = list(
            horizontal_pattern.hatch_lines_intersecting_triangle(triangle)
        )
        assert len(lines) == 1
        l0 = lines[0]
        assert l0.start.isclose((1.5, 1))
        assert l0.end.isclose((1, 1))


if __name__ == "__main__":
    pytest.main([__file__])
