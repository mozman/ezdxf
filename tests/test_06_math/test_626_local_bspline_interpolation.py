# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from ezdxf.math import (
    Vec3,
    estimate_tangents,
    local_cubic_bspline_interpolation,
)
from ezdxf.math.bspline import local_cubic_bspline_interpolation_from_tangents


POINTS1 = [(1, 1), (2, 4), (4, 1), (7, 6)]
POINTS2 = [(1, 1), (2, 4), (4, 1), (7, 6), (5, 8), (3, 3), (1, 7)]


def test_estimate_tangents_3p():
    tangents = estimate_tangents(Vec3.list(POINTS1), method="3-points")
    assert len(tangents) == 4


def test_estimate_tangents_5p():
    tangents = estimate_tangents(Vec3.list(POINTS1), method="5-points")
    assert len(tangents) == 4


def test_local_cubic_bspline_interpolation_from_tangents():
    points = Vec3.list(POINTS1)
    tangents = estimate_tangents(points)
    control_points, knots = local_cubic_bspline_interpolation_from_tangents(
        points, tangents
    )
    assert len(control_points) == 8
    assert len(knots) == 8 + 4  # count + order


def test_local_cubic_bspline_interpolation():
    bspline = local_cubic_bspline_interpolation(POINTS1, method="5-points")
    assert bspline.degree == 3
    assert len(bspline.control_points) == 8
    assert len(bspline.knots()) == 8 + 4  # count + order
