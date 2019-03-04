# Created: 14.11.2010
# Copyright (c) 2010, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.math import xround
from ezdxf.math.construct2d import *
from ezdxf.math.points import closest_point
from math import isclose, radians


def test_normalize_angle():
    angle = 2
    huge_angle = angle + 16 * HALF_PI
    assert isclose(normalize_angle(huge_angle), 2.)


def test_left_of_line():
    assert left_of_line((-1, 0), (0, 0), (0.1, 1)) is True
    assert left_of_line((1, 0), (0, 0), (0, -1)) is True
    assert left_of_line((-1, -1), (0, 0), (0.1, 1)) is True


def test_left_of_line_or_on_the_line():
    # vertical line
    assert left_of_line((1, 0), (0, 0), (0, 1), online=True) is False
    assert left_of_line((0, 0.5), (0, 0), (0, 1), online=True) is True
    assert left_of_line((-1, 0.5), (0, 0), (0, 1), online=True) is True

    # horizontal line
    assert left_of_line((0, 1), (0, 0), (1, 0), online=True) is True
    assert left_of_line((0, 0), (0, 0), (1, 0), online=True) is True
    assert left_of_line((0, -1), (0, 0), (1, 0), online=True) is False
    # 45 deg line
    assert left_of_line((0, 0), (0, 0), (1, 1), online=True) is True
    assert left_of_line((0.5, 0.5), (0, 0), (1, 1), online=True) is True
    assert left_of_line((1, 1), (0, 0), (1, 1), online=True) is True
    assert left_of_line((.5, .49), (0, 0), (1, 1), online=True) is False


def test_is_close_points():
    with pytest.raises(TypeError):
        is_close_points((1, 1, 0), (1, 1))

    assert is_close_points((1, 1, 1), (1, 1, 1)) is True
    assert is_close_points((1, 1, 1), (1, 1, 1.0000000001)) is True


def test_xround():
    assert xround(9.999, 0.) == 10
    assert xround(9.999, 0.5) == 10
    assert xround(9.75, 0.5) == 10
    assert xround(9.74, 0.5) == 9.5
    assert xround(9.74, 0.25) == 9.75
    assert xround(9.626, 0.25) == 9.75
    assert xround(9.624, 0.25) == 9.50
    assert xround(9.624, 0.1) == 9.6
    assert xround(9.624, 0.01) == 9.62
    assert xround(9.626, 0.01) == 9.63
    assert xround(9.626, 0.05) == 9.65

    assert xround(19.1, 1.) == 19
    assert xround(19.1, 2.) == 20
    assert xround(18.9, 2.) == 18
    assert xround(18.9, 5.) == 20
    assert xround(18.9, 10) == 20
    assert xround(1234, 10) == 1230
    assert xround(1236, 10) == 1240


def test_enclosing_angles():
    assert enclosing_angles(radians(45), start_angle=radians(45), end_angle=radians(45), ccw=True) is True
    assert enclosing_angles(radians(45), start_angle=radians(45), end_angle=radians(45), ccw=False) is True

    assert enclosing_angles(radians(90), start_angle=radians(45), end_angle=radians(135), ccw=True) is True
    assert enclosing_angles(radians(90), start_angle=radians(45), end_angle=radians(135), ccw=False) is False

    assert enclosing_angles(radians(0), start_angle=radians(45), end_angle=radians(135), ccw=True) is False
    assert enclosing_angles(radians(0), start_angle=radians(45), end_angle=radians(135), ccw=False) is True

    assert enclosing_angles(radians(45), start_angle=radians(50), end_angle=radians(40), ccw=True) is False
    assert enclosing_angles(radians(45), start_angle=radians(50), end_angle=radians(40), ccw=False) is True

    assert enclosing_angles(radians(90), start_angle=radians(135), end_angle=radians(45), ccw=True) is False
    assert enclosing_angles(radians(90), start_angle=radians(135), end_angle=radians(45), ccw=False) is True

    assert enclosing_angles(radians(270), start_angle=radians(135), end_angle=radians(45), ccw=True) is True
    assert enclosing_angles(radians(270), start_angle=radians(135), end_angle=radians(45), ccw=False) is False


def test_no_points():
    assert closest_point((0, 0), []) is None


def test_one_points():
    assert closest_point((0, 0), [(1, 1)]) == (1, 1)


def test_two_points():
    assert closest_point((0, 0), [(0, 0, 1), (1, 1, 1)]) == (0, 0, 1)


def test_more_points():
    assert closest_point((0, 0), [(0, 0, 1), (1, 1, 1), (2, 2, 2), (0, 0, -.5)]) == (0, 0, -.5)
