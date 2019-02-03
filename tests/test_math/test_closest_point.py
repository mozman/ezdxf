# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from ezdxf.math.points import closest_point


def test_no_points():
    assert closest_point((0, 0), []) is None


def test_one_points():
    assert closest_point((0, 0), [(1, 1)]) == (1, 1)


def test_two_points():
    assert closest_point((0, 0), [(0, 0, 1), (1, 1, 1)]) == (0, 0, 1)


def test_more_points():
    assert closest_point((0, 0), [(0, 0, 1), (1, 1, 1), (2, 2, 2), (0, 0, -.5)]) == (0, 0, -.5)

