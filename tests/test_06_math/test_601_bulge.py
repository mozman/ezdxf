# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import math
from ezdxf.math import (
    bulge_radius, bulge_center, arc_to_bulge, bulge_3_points, bulge_to_arc,
)


def test_bulge_radius():
    assert bulge_radius((0, 0), (1, 0), 1) == .5
    assert bulge_radius((0, 0), (1, 0), -1) == .5


def test_bulge_center():
    assert bulge_center((0, 0), (1, 0), 1).isclose((0.5, 0))
    assert bulge_center((0, 0), (1, 0), -1).isclose((0.5, 0))


def test_arc_to_bulge():
    start, end, bulge = arc_to_bulge(center=(.5, 0), start_angle=math.pi,
                                     end_angle=0, radius=.5)
    assert start.isclose((0., 0., 0.))
    assert end.isclose((1., 0., 0.))
    assert math.isclose(bulge, 1.)


def test_bulge_3_points():
    assert math.isclose(
        bulge_3_points(start_point=(0, 0), end_point=(1, 0), point=(.5, -.5)),
        1.)


def test_bulge_to_arc():
    center, start_angle, end_angle, radius = bulge_to_arc(start_point=(0, 0),
                                                          end_point=(1, 0),
                                                          bulge=-1)
    assert center.isclose((.5, 0., 0.))
    assert math.isclose(start_angle, 0, abs_tol=1e-15)
    assert math.isclose(end_angle, math.pi)
    assert radius == .5
