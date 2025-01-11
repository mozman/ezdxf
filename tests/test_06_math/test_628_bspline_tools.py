#  Copyright (c) 2025, Manfred Moitzi
#  License: MIT License
import pytest

import math
from ezdxf.math import BSpline
from ezdxf.math.bspline import to_homogeneous_points, from_homogeneous_points


CONTROL_POINTS = [(0, 0), (1, -1), (2, 0), (3, 2), (4, 0), (5, -2)]
WEIGHTS = [1, 2, 3, 3, 2, 1]

# visually checked in BricsCAD
EXPECTED_POINTS = [
    (0.0, 0.0, 0.0),
    (0.75, -0.75, 0.0),
    (1.25, -0.75, 0.0),
    (1.9583333333333335, 0.04166666666666663, 0.0),
    (2.5, 1.0, 0.0),
    (3.041666666666666, 1.583333333333333, 0.0),
    (3.75, 0.5, 0.0),
    (4.25, -0.5, 0.0),
    (5.0, -2.0, 0.0),
]
EXPECTED_KNOTS = [
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.3333333333333333,
    0.3333333333333333,
    0.6666666666666666,
    0.6666666666666666,
    1.0,
    1.0,
    1.0,
    1.0,
    1.0,
]

EXPECTED_POINTS_RATIONAL = [
    (0.0, 0.0, 0.0),
    (0.8571428571428571, -0.8571428571428571, 0.0),
    (1.3333333333333333, -0.6666666666666666, 0.0),
    (2.0, 0.08695652173913043, 0.0),
    (2.5, 1.0, 0.0),
    (2.999999999999999, 1.6521739130434785, 0.0),
    (3.6666666666666665, 0.6666666666666666, 0.0),
    (4.142857142857143, -0.2857142857142857, 0.0),
    (5.0, -2.0, 0.0),
]

EXPECTED_WEIGHTS = [1.0, 1.75, 2.25, 2.875, 3.0, 2.8749999999999996, 2.25, 1.75, 1.0]


class TestNonRationalBSpline:
    @pytest.fixture(scope="class")
    def result(self):
        spline = BSpline(CONTROL_POINTS)
        return spline.degree_elevation(1)

    def test_degree_is_elevated(self, result: BSpline):
        assert result.degree == 4

    def test_clamped_start_and_end_points_are_preserved(self, result: BSpline):
        assert result.control_points[0].isclose(CONTROL_POINTS[0])
        assert result.control_points[-1].isclose(CONTROL_POINTS[-1])

    def test_expected_control_points(self, result: BSpline):
        assert (
            all(cp.isclose(e) for cp, e in zip(result.control_points, EXPECTED_POINTS))
            is True
        )

    def test_expected_knot_values(self, result: BSpline):
        assert (
            all(math.isclose(k, e) for k, e in zip(result.knots(), EXPECTED_KNOTS))
            is True
        )

    def test_elevation_0_times(self):
        spline = BSpline(CONTROL_POINTS)
        assert spline.degree_elevation(0) is spline
        assert spline.degree_elevation(-1) is spline


class TestRationalBSpline:
    @pytest.fixture(scope="class")
    def result(self):
        spline = BSpline(CONTROL_POINTS, weights=WEIGHTS)
        return spline.degree_elevation(1)

    def test_degree_is_elevated(self, result: BSpline):
        assert result.degree == 4

    def test_clamped_start_and_end_points_are_preserved(self, result: BSpline):
        assert result.control_points[0].isclose(CONTROL_POINTS[0])
        assert result.control_points[-1].isclose(CONTROL_POINTS[-1])

    def test_expected_control_points(self, result: BSpline):
        assert (
            all(
                cp.isclose(e)
                for cp, e in zip(result.control_points, EXPECTED_POINTS_RATIONAL)
            )
            is True
        )

    def test_expected_knot_values(self, result: BSpline):
        assert (
            all(math.isclose(k, e) for k, e in zip(result.knots(), EXPECTED_KNOTS))
            is True
        )

    def test_expected_weights(self, result: BSpline):
        assert (
            all(math.isclose(w, e) for w, e in zip(result.weights(), EXPECTED_WEIGHTS))
            is True
        )


class TestHomogeneousPoints:
    def test_to_hg_points(self):
        bsp = BSpline(CONTROL_POINTS, weights=WEIGHTS)
        hp = to_homogeneous_points(bsp)
        assert len(hp) == len(CONTROL_POINTS)
        assert len(hp[0]) == 4
        assert tuple(hp[1]) == (2, -2, 0, 2)

    def test_to_hg_points_non_rational(self):
        bsp = BSpline(CONTROL_POINTS)
        hp = to_homogeneous_points(bsp)
        assert len(hp) == len(CONTROL_POINTS)
        assert len(hp[0]) == 4
        assert tuple(hp[1]) == (1, -1, 0, 1)

    def test_revert_hg_points(self):
        bsp = BSpline(CONTROL_POINTS, weights=WEIGHTS)
        hp = to_homogeneous_points(bsp)
        points, weights = from_homogeneous_points(hp)
        assert len(points) == len(CONTROL_POINTS)
        assert len(weights) == len(WEIGHTS)
        assert all(v.isclose(e) for v, e in zip(points, CONTROL_POINTS)) is True
        assert all(math.isclose(w, e) for w, e in zip(weights, WEIGHTS)) is True


if __name__ == "__main__":
    pytest.main([__file__])
