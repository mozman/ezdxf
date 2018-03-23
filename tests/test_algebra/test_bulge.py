# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from ezdxf.algebra.bulge import bulge_radius


def test_bulge_radius():
    assert bulge_radius((0, 0), (1, 0), 1) == .5
    assert bulge_radius((0, 0), (1, 0), -1) == .5
