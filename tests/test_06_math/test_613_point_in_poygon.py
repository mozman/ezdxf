# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math.construct2d import is_point_in_polygon


def test_inside_horiz_box():
    square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    assert is_point_in_polygon((.5, .5), square) == 1


def test_outside_horiz_box():
    square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    assert is_point_in_polygon((-.5, .5), square) == -1
    assert is_point_in_polygon((1.5, .5), square) == -1
    assert is_point_in_polygon((0.5, -.5), square) == -1
    assert is_point_in_polygon((0.5, 1.5), square) == -1


def test_colinear_outside_horiz_box():
    square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    assert is_point_in_polygon((1.5, 0), square) == -1
    assert is_point_in_polygon((-.5, 0), square) == -1
    assert is_point_in_polygon((0, 1.5), square) == -1
    assert is_point_in_polygon((0, -.5), square) == -1


def test_corners_horiz_box():
    square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    assert is_point_in_polygon((0, 0), square) == 0
    assert is_point_in_polygon((0, 1), square) == 0
    assert is_point_in_polygon((1, 1), square) == 0
    assert is_point_in_polygon((0, 1), square) == 0


def test_inside_slanted_box():
    square = [(0, 0), (1, 1), (0, 2), (-1, 1)]
    assert is_point_in_polygon((0, 1), square) == 1


def test_outside_slanted_box():
    square = [(0, 0), (1, 1), (0, 2), (-1, 1)]
    assert is_point_in_polygon((-1, 0), square) == -1
    assert is_point_in_polygon((1, 0), square) == -1
    assert is_point_in_polygon((1, 2), square) == -1
    assert is_point_in_polygon((-1, 2), square) == -1


def test_corners_slanted_box():
    square = [(0, 0), (1, 1), (0, 2), (-1, 1)]
    assert is_point_in_polygon((0, 0), square) == 0
    assert is_point_in_polygon((1, 1), square) == 0
    assert is_point_in_polygon((0, 2), square) == 0
    assert is_point_in_polygon((-1, 1), square) == 0


def test_borders_slanted_box_stable():
    square = [(0, 0), (1, 1), (0, 2), (-1, 1)]
    assert is_point_in_polygon((0.5, 0.5), square) == 0
    assert is_point_in_polygon((0.5, 1.5), square) == 0
    assert is_point_in_polygon((-.5, 1.5), square) == 0
    assert is_point_in_polygon((-.5, 0.5), square) == 0


if __name__ == '__main__':
    pytest.main([__file__])
