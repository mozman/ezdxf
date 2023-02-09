#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
# Test only basic features of Cython implementation,
# Full testing and compatibility check with Python implementation
# is located in test suite 632.

import pytest

bezier = pytest.importorskip("ezdxf.acc.bezier3p")
Bezier3P = bezier.Bezier3P
from ezdxf.acc.vector import Vec3
from ezdxf.acc.matrix44 import Matrix44

# check functions:

POINTS = [(0.0, 0.0), (5.0, 5.0), (10.0, 0.0)]


def test_default_constructor():
    c = Bezier3P(POINTS)
    assert c.control_points == Vec3.tuple(POINTS)


@pytest.fixture
def curve():
    return Bezier3P(POINTS)


def test_point(curve):
    assert curve.point(0.5) == (5.0, 2.5)


def test_tangent(curve):
    assert curve.tangent(0.5) == (10.0, 0)


def test_approximate(curve):
    points = curve.approximate(10)
    assert len(points) == 11


def test_flattening(curve):
    points = curve.flattening(0.01)
    assert len(points) == 17


def test_approximated_length(curve):
    assert curve.approximated_length(32) == pytest.approx(11.47678475868991)


def test_reverse(curve):
    r = curve.reverse()
    assert r.control_points == Vec3.tuple(reversed(POINTS))


def test_transform(curve):
    m = Matrix44.translate(1, 1, 0)
    r = curve.transform(m)
    assert r.control_points == Vec3.tuple([(1, 1), (6, 6), (11, 1)])


if __name__ == "__main__":
    pytest.main([__file__])
