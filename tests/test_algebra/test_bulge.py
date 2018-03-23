# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from ezdxf.algebra.bulge import bulge_radius, bulge_center


def test_bulge_radius():
    assert bulge_radius((0, 0), (1, 0), 1) == .5
    assert bulge_radius((0, 0), (1, 0), -1) == .5


def test_bulge_center():
    assert bulge_center((0, 0), (1, 0), 1) == (0.5, 0)
    assert bulge_center((0, 0), (1, 0), -1) == (0.5, 0)
