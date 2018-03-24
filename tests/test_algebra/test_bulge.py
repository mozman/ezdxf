# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import math
from ezdxf.algebra.bulge import bulge_radius, bulge_center, arc_to_bulge, bulge_3_points, bulge_to_arc
from ezdxf.algebra import is_close


def test_bulge_radius():
    assert bulge_radius((0, 0), (1, 0), 1) == .5
    assert bulge_radius((0, 0), (1, 0), -1) == .5


def test_bulge_center():
    assert bulge_center((0, 0), (1, 0), 1) == (0.5, 0)
    assert bulge_center((0, 0), (1, 0), -1) == (0.5, 0)


def test_arc_to_bulge():
    start, end, bulge = arc_to_bulge(center=(.5, 0), start_angle=math.pi, end_angle=0, radius=.5)
    assert start == (0., 0., 0.)
    assert end == (1., 0., 0.)
    assert is_close(bulge, 1.)


def test_bulge_3_points():
    assert is_close(bulge_3_points(start_point=(0, 0), end_point=(1, 0), point=(.5, -.5)), 1.)


def test_bulge_to_arc():
    center, start_angle, end_angle, radius = bulge_to_arc(start_point=(0, 0), end_point=(1, 0), bulge=-1)
    assert center == (.5, 0., 0.)
    assert is_close(start_angle, 0)
    assert is_close(end_angle, math.pi)
    assert radius == .5
