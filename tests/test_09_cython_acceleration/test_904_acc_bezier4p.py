#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
# Test only basic features of Cython implementation,
# Full testing and compatibility check with Python implementation
# is located in test suite 630.

import pytest

bezier = pytest.importorskip('ezdxf.acc.bezier4p')
Bezier4P = bezier.Bezier4P
from ezdxf.acc.vector import Vec3

POINTS = [(0, 0), (1, 0), (1, 1), (0, 1)]


def test_default_constructor():
    c = Bezier4P(POINTS)
    assert c.control_points == Vec3.tuple(POINTS)


@pytest.fixture
def curve():
    return Bezier4P(POINTS)


def test_point(curve):
    assert curve.point(0.5) == (0.75, 0.5)


def test_tangent(curve):
    assert curve.tangent(0.5) == (0.0, 1.5)


def test_approximate(curve):
    points = curve.approximate(10)
    assert len(points) == 11


def test_flattening(curve):
    points = curve.flattening(0.01)
    assert len(points) == 17


def test_approximated_length(curve):
    assert curve.approximated_length(32) == 1.999232961352048


def test_reverse(curve):
    r = curve.reverse()
    assert r.control_points == Vec3.tuple(reversed(POINTS))


if __name__ == '__main__':
    pytest.main([__file__])
