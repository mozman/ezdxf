# Created: 14.11.2010
# Copyright (c) 2010, Manfred Moitzi
# License: MIT License
from ezdxf.algebra.base import *


def test_rotate_2s():
    result = rotate_2d((5, 0), HALF_PI)
    assert is_close(result[0], 0.)
    assert is_close(result[1], 5.)


def test_normalize_angle():
    angle = 2
    huge_angle = angle + 16 * HALF_PI
    assert is_close(normalize_angle(huge_angle), 2.)


def test_is_vertical_angle():
    assert is_vertical_angle(HALF_PI) is True
    assert is_vertical_angle(2 * HALF_PI) is False


def test_get_angle():
    assert is_close(get_angle((0., 0.), (0., 1.)), HALF_PI)
    assert is_close(get_angle((0., 0.), (1., 1.)), HALF_PI / 2.)


def test_right_of_line():
    assert right_of_line((1, 0), (0, 0), (0, 1)) is True
    assert left_of_line((1, 0), (0, 0), (0, 1)) is False
    assert right_of_line((1, 1), (0, 0), (-1, 0)) is True


def test_left_of_line():
    assert left_of_line((-1, 0), (0, 0), (0.1, 1)) is True
    assert left_of_line((1, 0), (0, 0), (0, -1)) is True
    assert left_of_line((-1, -1), (0, 0), (0.1, 1)) is True
    assert right_of_line((-1, 0), (0, 0), (-1, .1)) is False


def test_is_close_points():
    assert is_close_points((1, 1, 1), (1, 1, 1)) is True
    assert is_close_points((1, 1, 0), (1, 1)) is True
    assert is_close_points((1, 1, 1), (1, 1)) is False
    assert is_close_points((1, 1, 1), (1, 1, 1.0000000001)) is True
