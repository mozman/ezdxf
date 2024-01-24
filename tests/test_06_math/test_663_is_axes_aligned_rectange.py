# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.math import is_axes_aligned_rectangle_2d, Vec2

@pytest.mark.parametrize(
    "points",
    [
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # ccw start horizontal
        [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],  # ccw start horizontal closed
        [(1, 0), (1, 1), (0, 1), (0, 0)],  # ccw start vertical
        [(1, 0), (1, 1), (0, 1), (0, 0), (1, 0)],  # ccw start vertical closed
        [(0, 1), (1, 1), (1, 0), (0, 0)],  # cw start horizontal
        [(0, 0), (0, 1), (1, 1), (1, 0)],  # cw start vertical
    ],
)
def test_is_aligned_rectangle(points):
    assert is_axes_aligned_rectangle_2d(Vec2.list(points)) is True


@pytest.mark.parametrize(
    "points",
    [
        [(0, 0), (1, 0), (1, 1)],  # less than 4 vertices
        [(0, 0), (1, 0), (1, 1), (0.1, 1)],  # nearly aligned quadliteral
        [
            (0, 0),
            (1, 0),
            (1.1, 1),
            (0.1, 1),
        ],  # parallelogram, opposed sides have the same length
    ],
)
def test_is_not_aligned_rectangle(points):
    assert is_axes_aligned_rectangle_2d(Vec2.list(points)) is False


if __name__ == '__main__':
    pytest.main([__file__])