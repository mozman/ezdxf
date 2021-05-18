# Copyright (c) 2010-2021, Manfred Moitzi
# License: MIT License
import pytest
from math import isclose, radians
from ezdxf.math import xround, Vec2
from ezdxf.math.construct2d import *


def test_left_of_line():
    assert is_point_left_of_line(Vec2(-1, 0), Vec2(0, 0), Vec2(0.1, 1)) is True
    assert is_point_left_of_line(Vec2(1, 0), Vec2(0, 0), Vec2(0, -1)) is True
    assert is_point_left_of_line(Vec2(-1, -1), Vec2(0, 0), Vec2(0.1, 1)) is True


def test_point_to_line_relation_left():
    assert point_to_line_relation(Vec2(-1, 0), Vec2(0, 0), Vec2(0.1, 1)) == -1
    assert point_to_line_relation(Vec2(1, 0), Vec2(0, 0), Vec2(0, -1)) == -1
    assert point_to_line_relation(Vec2(-1, -1), Vec2(0, 0), Vec2(0.1, 1)) == -1


def test_left_of_line_or_on_the_line():
    # vertical line
    assert is_point_left_of_line(Vec2(1, 0), Vec2(0, 0), Vec2(0, 1),
                                 colinear=True) is False
    assert is_point_left_of_line(Vec2(0, 0.5), Vec2(0, 0), Vec2(0, 1),
                                 colinear=True) is True
    assert is_point_left_of_line(Vec2(-1, 0.5), Vec2(0, 0), Vec2(0, 1),
                                 colinear=True) is True
    # horizontal line
    assert is_point_left_of_line(Vec2(0, 1), Vec2(0, 0), Vec2(1, 0),
                                 colinear=True) is True
    assert is_point_left_of_line(Vec2(0, 0), Vec2(0, 0), Vec2(1, 0),
                                 colinear=True) is True
    assert is_point_left_of_line(Vec2(0, -1), Vec2(0, 0), Vec2(1, 0),
                                 colinear=True) is False
    # 45 deg line
    assert is_point_left_of_line(Vec2(0, 0), Vec2(0, 0), Vec2(1, 1),
                                 colinear=True) is True
    assert is_point_left_of_line(Vec2(0.5, 0.5), Vec2(0, 0), Vec2(1, 1),
                                 colinear=True) is True
    assert is_point_left_of_line(Vec2(1, 1), Vec2(0, 0), Vec2(1, 1),
                                 colinear=True) is True
    assert is_point_left_of_line(Vec2(.5, .49), Vec2(0, 0), Vec2(1, 1),
                                 colinear=True) is False


def test_point_ot_line_relation_on_line():
    # vertical line
    assert point_to_line_relation(Vec2(0, 2), Vec2(0, 0), Vec2(0, 1)) == 0
    assert point_to_line_relation(Vec2(0, -1), Vec2(0, 0), Vec2(0, 1)) == 0
    assert point_to_line_relation(Vec2(0, 0.5), Vec2(0, 0), Vec2(0, 1)) == 0
    # horizontal line
    assert point_to_line_relation(Vec2(1, 0), Vec2(0, 0), Vec2(1, 0)) == 0
    assert point_to_line_relation(Vec2(-1, 0), Vec2(0, 0), Vec2(1, 0)) == 0
    assert point_to_line_relation(Vec2(0, 0), Vec2(0, 0), Vec2(1, 0)) == 0
    # 45 deg line
    assert point_to_line_relation(Vec2(0, 0), Vec2(0, 0), Vec2(1, 1)) == 0
    assert point_to_line_relation(Vec2(0.5, 0.5), Vec2(0, 0), Vec2(1, 1)) == 0
    assert point_to_line_relation(Vec2(1, 1), Vec2(0, 0), Vec2(1, 1)) == 0
    assert point_to_line_relation(Vec2(-.5, -.5), Vec2(0, 0), Vec2(1, 1)) == 0


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
    assert enclosing_angles(radians(45), start_angle=radians(45),
                            end_angle=radians(45), ccw=True) is True
    assert enclosing_angles(radians(45), start_angle=radians(45),
                            end_angle=radians(45), ccw=False) is True

    assert enclosing_angles(radians(90), start_angle=radians(45),
                            end_angle=radians(135), ccw=True) is True
    assert enclosing_angles(radians(90), start_angle=radians(45),
                            end_angle=radians(135), ccw=False) is False

    assert enclosing_angles(radians(0), start_angle=radians(45),
                            end_angle=radians(135), ccw=True) is False
    assert enclosing_angles(radians(0), start_angle=radians(45),
                            end_angle=radians(135), ccw=False) is True

    assert enclosing_angles(radians(45), start_angle=radians(50),
                            end_angle=radians(40), ccw=True) is False
    assert enclosing_angles(radians(45), start_angle=radians(50),
                            end_angle=radians(40), ccw=False) is True

    assert enclosing_angles(radians(90), start_angle=radians(135),
                            end_angle=radians(45), ccw=True) is False
    assert enclosing_angles(radians(90), start_angle=radians(135),
                            end_angle=radians(45), ccw=False) is True

    assert enclosing_angles(radians(270), start_angle=radians(135),
                            end_angle=radians(45), ccw=True) is True
    assert enclosing_angles(radians(270), start_angle=radians(135),
                            end_angle=radians(45), ccw=False) is False


def test_no_points():
    assert closest_point((0, 0), []) is None


def test_one_points():
    assert closest_point((0, 0), [(1, 1)]) == (1, 1)


def test_two_points():
    assert closest_point((0, 0), [(0, 0, 1), (1, 1, 1)]) == (0, 0, 1)


def test_more_points():
    assert closest_point((0, 0),
                         [(0, 0, 1), (1, 1, 1), (2, 2, 2), (0, 0, -.5)]) == (
               0, 0, -.5)


def test_linspace():
    assert list(linspace(1, 4, num=4)) == [1, 2, 3, 4]
    assert list(linspace(1, 4, num=1)) == [1]
    assert list(linspace(1, 4, num=0)) == []
    assert list(linspace(1, 5, num=4, endpoint=False)) == [1, 2, 3, 4]
    assert list(linspace(2, -2, num=5)) == [2, 1, 0, -1, -2]
    with pytest.raises(ValueError):
        list(linspace(1, 4, num=-1))


def test_reflect_angle_x_deg():
    for a, expected in [(0, 180), (45, 135), (90, 90), (135, 45), (180, 0),
                        (225, 315), (270, 270), (315, 225), (360, 180), ]:
        assert isclose(reflect_angle_x_deg(a), expected)


def test_reflect_angle_y_deg():
    for a, expected in [(0, 0), (45, 315), (90, 270), (135, 225), (180, 180),
                        (225, 135), (270, 90), (315, 45), (360, 0), ]:
        assert isclose(reflect_angle_y_deg(a), expected)


def test_area():
    assert area([(4, 6), (4, -4), (8, -4), (8, -8), (-4, -8), (-4, 6)]) == 128
