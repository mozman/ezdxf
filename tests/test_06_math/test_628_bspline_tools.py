#  Copyright (c) 2025, Manfred Moitzi
#  License: MIT License
import pytest

import math
from ezdxf.math import BSpline
from ezdxf.math.bspline import to_homogeneous_points, from_homogeneous_points
import numpy as np

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


class TestDegreeElevationNonRationalBSpline:
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


class TestDegreeElevationRationalBSpline:
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


class TestPointInversion:
    @pytest.fixture(scope="class")
    def spline(self):
        return BSpline(CONTROL_POINTS)

    def test_start_point(self, spline):
        assert math.isclose(0, spline.point_inversion((0, 0)))

    def test_end_point(self, spline):
        result = spline.point_inversion(CONTROL_POINTS[-1])
        assert math.isclose(spline.max_t, result)

    def test_many_points(self, spline):
        t = np.linspace(0, spline.max_t, 13)
        points = spline.points(t)
        assert all(
            math.isclose(spline.point_inversion(p), u) for p, u in zip(points, t)
        )


class TestSplineMeasurement:
    # measurements done in BricsCAD v25
    total_length = 7.7842
    mid_length = total_length / 2
    mid_param = 0.6251460418169124

    @pytest.fixture(scope="class")
    def spline(self):
        return BSpline(CONTROL_POINTS)

    def test_measure_length(self, spline):
        mtool = spline.measure(100)
        # measurement diverges less than 1%
        assert mtool.length / self.total_length > 0.99

    def test_measure_length_by_0_segments(self, spline):
        with pytest.raises(ValueError):
            spline.measure(0)

    def test_get_param_for_mid_point(self, spline):
        mtool = spline.measure(100)
        t = mtool.param_at(self.mid_length)
        # measurement diverges less than 1%
        assert 0.99 < t / self.mid_param <= 1.0

    def test_params_out_of_range(self, spline):
        mtool = spline.measure(100)
        assert mtool.param_at(-1) == 0.0
        assert mtool.param_at(100) == spline.max_t

    def test_distance_from_start(self, spline):
        mtool = spline.measure(100)
        ratio = mtool.distance(self.mid_param) / self.mid_length
        # measurement diverges less than 1%
        assert 0.99 < ratio <= 1.00

    def test_distance_out_of_range(self, spline):
        mtool = spline.measure(100)
        assert mtool.distance(-1) == 0.0
        assert mtool.distance(100) == mtool.length

    def test_divide(self, spline):
        mtool = spline.measure(100)
        params = mtool.divide(7)
        assert len(params) == 6
        assert params[0] != 0.0
        assert params[-1] != spline.max_t

    def test_extents(self, spline):
        mtool = spline.measure()
        assert mtool.extmin.isclose((0, -2))
        assert mtool.extmax.isclose((5, 1.19263675))


def test_split_spline():
    spline = BSpline(CONTROL_POINTS)
    mid_t = spline.measure().divide(2)[0]
    sp1, sp2 = spline.split(mid_t)
    l1 = sp1.measure().length
    l2 = sp2.measure().length
    assert abs(l1 - l2) < 0.01


if __name__ == "__main__":
    pytest.main([__file__])
