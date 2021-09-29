#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
# Test only basic features of Cython implementation,
# Full testing and compatibility check with Python implementation
# is located in test suite 630a.

import pytest
import math

bezier = pytest.importorskip("ezdxf.acc.bezier4p")
Bezier4P = bezier.Bezier4P
from ezdxf.acc.vector import Vec3
from ezdxf.acc.matrix44 import Matrix44

# check functions:
from ezdxf.math._bezier4p import (
    cubic_bezier_arc_parameters,
    cubic_bezier_from_arc,
    cubic_bezier_from_ellipse,
)
from ezdxf.math.ellipse import ConstructionEllipse

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


def test_transform(curve):
    m = Matrix44.translate(1, 1, 0)
    r = curve.transform(m)
    assert r.control_points == Vec3.tuple([(1, 1), (2, 1), (2, 2), (1, 2)])


@pytest.mark.parametrize(
    "s, e",
    [
        (0, math.pi),
        (math.pi, math.tau),
        (0, math.tau),
    ],
)
def test_correctness_arc_parameters(s, e):
    expected = list(cubic_bezier_arc_parameters(s, e))
    result = list(bezier.cubic_bezier_arc_parameters(s, e))
    assert result == expected


@pytest.mark.parametrize(
    "s, e",
    [
        (0, 180),
        (180, 360),
        (0, 360),
    ],
)
def test_correctness_bezier_from_arc(s, e):
    expected = list(
        cubic_bezier_from_arc(
            center=Vec3(1, 2),
            start_angle=s,
            end_angle=e,
        )
    )
    result = list(
        bezier.cubic_bezier_from_arc(
            center=Vec3(1, 2),
            start_angle=s,
            end_angle=e,
        )
    )
    for e, r in zip(expected, result):
        assert e.control_points == r.control_points


@pytest.mark.parametrize(
    "s, e",
    [
        (0, math.pi),
        (math.pi, math.tau),
        (0, math.tau),
    ],
)
def test_correctness_bezier_from_ellipse(s, e):
    ellipse = ConstructionEllipse(
        center=(1, 2),
        major_axis=(2, 0),
        ratio=0.5,
        start_param=s,
        end_param=e,
    )
    expected = list(cubic_bezier_from_ellipse(ellipse))
    result = list(bezier.cubic_bezier_from_ellipse(ellipse))
    for e, r in zip(expected, result):
        assert e.control_points == r.control_points


if __name__ == "__main__":
    pytest.main([__file__])
