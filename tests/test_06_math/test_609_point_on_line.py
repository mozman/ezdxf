# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import Vec2, distance_point_line_2d, is_point_on_line_2d


def test_distance_point_horiz_line():
    start, end = Vec2(0, 0), Vec2(10, 0)
    assert distance_point_line_2d(Vec2(5, 2), start, end) == 2
    assert distance_point_line_2d(Vec2(5, -3), start, end) == 3
    assert distance_point_line_2d(Vec2(0, 0), start, end) == 0


def test_distance_point_vertical_line():
    start, end = Vec2(0, 0), Vec2(0, 10)
    assert distance_point_line_2d(Vec2(2, 0), start, end) == 2
    assert distance_point_line_2d(Vec2(-3, 0), start, end) == 3
    assert distance_point_line_2d(Vec2(0, 0), start, end) == 0


def test_is_point_on_horiz_line():
    assert is_point_on_line_2d(Vec2(-1, 0), Vec2(0, 0), Vec2(1, 0)) is True
    assert is_point_on_line_2d(Vec2(-1, 0), Vec2(0, 0), Vec2(1, .0001)) is False
    assert is_point_on_line_2d(Vec2(-1, 0), Vec2(0, 0), Vec2(1, 0), ray=False) is False


def test_is_point_on_vertical_line():
    assert is_point_on_line_2d(Vec2(0, -1), Vec2(0, 0), Vec2(0, 1)) is True
    assert is_point_on_line_2d(Vec2(0, -1), Vec2(0, 0), Vec2(0.00001, 1)) is False
    assert is_point_on_line_2d(Vec2(0, -1), Vec2(0, 0), Vec2(0, 1), ray=False) is False


def test_is_point_on_diag_line():
    assert is_point_on_line_2d(Vec2(-1, -1), Vec2(0, 0), Vec2(1, 1)) is True
    assert is_point_on_line_2d(Vec2(-1, -1), Vec2(0, 0), Vec2(1, 1), ray=False) is False


if __name__ == '__main__':
    pytest.main([__file__])
