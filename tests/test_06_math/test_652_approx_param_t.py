#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import (
    ApproxParamT,
    Bezier3P,
    Bezier4P,
    BSpline,
    open_uniform_knot_vector,
    Vec2,
)


class TestGenericFeatures:
    @pytest.fixture
    def curve(self):
        return Bezier3P(Vec2.list([(0, 0), (1, 2), (2, 4)]))

    def test_access_to_construction_polyline(self, curve):
        approx = ApproxParamT(curve, segments=100)
        assert approx.polyline.length == pytest.approx(4.472135954999586)

    def test_get_max_t(self, curve):
        approx = ApproxParamT(curve, segments=100)
        assert approx.max_t == 1.0


class TestQuadraticBezier:
    @pytest.fixture(scope="class")
    def approx(self):
        return ApproxParamT(Bezier3P(Vec2.list([(0, 0), (1, 2), (2, 4)])))

    def test_start_param(self, approx):
        assert approx.param_t(0) == pytest.approx(0.0)

    def test_end_param(self, approx):
        assert approx.param_t(approx.polyline.length) == pytest.approx(1.0)

    def test_certain_distance(self, approx):
        t = 0.4472135954999581
        assert approx.param_t(2.0) == pytest.approx(t)
        assert approx.distance(t) == pytest.approx(2.0)


class TestCubicBezier:
    @pytest.fixture(scope="class")
    def approx(self):
        return ApproxParamT(Bezier4P(Vec2.list([(0, 0), (1, 2), (2, 4), (3, 1)])))

    def test_start_param(self, approx):
        assert approx.param_t(0) == pytest.approx(0.0)

    def test_end_param(self, approx):
        assert approx.param_t(approx.polyline.length) == pytest.approx(1.0)

    def test_certain_distance(self, approx):
        t = 0.31949832059570293
        assert approx.param_t(2.0) == pytest.approx(t)
        assert approx.distance(t) == pytest.approx(2.0)


class TestCubicSpline:
    @pytest.fixture(scope="class")
    def spline(self):
        points = [(0, 0), (1, 2), (2, 4), (3, 1), (4, 2)]
        # by default knot values are normalized in the range [0, 1],
        # this creates a not normalized knot vector in the range [0, 2]:
        knots = open_uniform_knot_vector(count=len(points), order=4)
        return BSpline(
            [(0, 0), (1, 2), (2, 4), (3, 1), (4, 2)],
            knots=knots,
        )

    @pytest.fixture(scope="class")
    def approx(self, spline):
        return ApproxParamT(spline, max_t=spline.max_t)

    def test_max_t_is_not_1(self, spline):
        """This class should test a different parameter range!"""
        assert spline.max_t == pytest.approx(2.0)

    def test_start_param(self, approx):
        assert approx.param_t(0) == pytest.approx(0.0)
        assert approx.distance(0.0) == pytest.approx(0.0)

    def test_end_param(self, approx):
        length = approx.polyline.length
        assert approx.param_t(length) == pytest.approx(2.0)
        assert approx.distance(2.0) == pytest.approx(length)

    def test_certain_distance(self, approx):
        t = 0.6692720686599521
        assert approx.param_t(3.0) == pytest.approx(t)
        assert approx.distance(t) == pytest.approx(3.0)


if __name__ == "__main__":
    pytest.main([__file__])
