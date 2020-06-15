# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import Vector
from ezdxf.math.bspline import(
    local_cubic_bspline_interpolation, estimate_cubic_spline_tangents_5p, estimate_cubic_spline_tangents_3p,
)

POINTS1 = [(1, 1), (2, 4), (4, 1), (7, 6)]
POINTS2 = [(1, 1), (2, 4), (4, 1), (7, 6), (5, 8), (3, 3), (1, 7)]


def test_estimate_tangents_3p():
    tangents = estimate_cubic_spline_tangents_3p(Vector.list(POINTS1))
    assert len(tangents) == 4


def test_estimate_tangents_5p():
    tangents = estimate_cubic_spline_tangents_5p(Vector.list(POINTS1))
    assert len(tangents) == 4


def _test_local_cubic_bspline_interpolation():
    points = Vector.list(POINTS1)
    tangents = estimate_cubic_spline_tangents_5p(points)
    control_points, knots = local_cubic_bspline_interpolation(points, tangents)
    assert len(control_points) == 4
    assert len(knots) == 10
