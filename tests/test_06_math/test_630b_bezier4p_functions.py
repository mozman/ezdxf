# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
import pytest
import random

from ezdxf.math import (
    cubic_bezier_interpolation,
    Vec3,
    Vec2,
    Bezier3P,
    quadratic_to_cubic_bezier,
    Bezier4P,
    have_bezier_curves_g1_continuity,
    bezier_to_bspline,
    split_bezier,
    quadratic_bezier_from_3p,
    close_vectors,
    cubic_bezier_bbox,
    quadratic_bezier_bbox,
    intersection_ray_cubic_bezier_2d,
)


def test_vertex_interpolation():
    points = [(0, 0), (3, 1), (5, 3), (0, 8)]
    result = list(cubic_bezier_interpolation(points))
    assert len(result) == 3
    c1, c2, c3 = result
    p = c1.control_points
    assert p[0].isclose((0, 0))
    assert p[1].isclose((0.9333333333333331, 0.3111111111111111))
    assert p[2].isclose((1.8666666666666663, 0.6222222222222222))
    assert p[3].isclose((3, 1))

    p = c2.control_points
    assert p[0].isclose((3, 1))
    assert p[1].isclose((4.133333333333334, 1.3777777777777778))
    assert p[2].isclose((5.466666666666667, 1.822222222222222))
    assert p[3].isclose((5, 3))

    p = c3.control_points
    assert p[0].isclose((5, 3))
    assert p[1].isclose((4.533333333333333, 4.177777777777778))
    assert p[2].isclose((2.2666666666666666, 6.088888888888889))
    assert p[3].isclose((0, 8))


def test_invalid_bezier_interpolation():
    """At least 3 points are required."""
    assert len(list(cubic_bezier_interpolation([(0, 0)]))) == 0
    assert len(list(cubic_bezier_interpolation([(0, 0), (1, 0)]))) == 0


def test_quadratic_to_cubic_bezier():
    r = random.Random(0)

    def random_vec() -> Vec3:
        return Vec3(r.uniform(-10, 10), r.uniform(-10, 10), r.uniform(-10, 10))

    for i in range(1000):
        quadratic = Bezier3P((random_vec(), random_vec(), random_vec()))
        quadratic_approx = list(quadratic.approximate(10))
        cubic = quadratic_to_cubic_bezier(quadratic)
        cubic_approx = list(cubic.approximate(10))

        assert len(quadratic_approx) == len(cubic_approx)
        for p1, p2 in zip(quadratic_approx, cubic_approx):
            assert p1.isclose(p2)


# G1 continuity: normalized end-tangent == normalized start-tangent of next curve
B1 = Bezier4P([(0, 0), (1, 1), (2, 1), (3, 0)])

# B1/B2 has G1 continuity:
B2 = Bezier4P([(3, 0), (4, -1), (5, -1), (6, 0)])

# B1/B3 has no G1 continuity:
B3 = Bezier4P([(3, 0), (4, 1), (5, 1), (6, 0)])

# B1/B4 G1 continuity off tolerance:
B4 = Bezier4P([(3, 0), (4, -1.03), (5, -1.0), (6, 0)])

# B1/B5 has a gap between B1 end and B5 start:
B5 = Bezier4P([(4, 0), (5, -1), (6, -1), (7, 0)])


def test_g1_continuity_for_bezier_curves():
    assert have_bezier_curves_g1_continuity(B1, B2) is True
    assert have_bezier_curves_g1_continuity(B1, B3) is False
    assert (
        have_bezier_curves_g1_continuity(B1, B4, g1_tol=1e-4) is False
    ), "should be outside of tolerance "
    assert (
        have_bezier_curves_g1_continuity(B1, B5) is False
    ), "end- and start point should match"


D1 = Bezier4P([(0, 0), (1, 1), (3, 0), (3, 0)])
D2 = Bezier4P([(3, 0), (3, 0), (5, -1), (6, 0)])


def test_g1_continuity_for_degenerated_bezier_curves():
    assert have_bezier_curves_g1_continuity(D1, B2) is False
    assert have_bezier_curves_g1_continuity(B1, D2) is False
    assert have_bezier_curves_g1_continuity(D1, D2) is False


@pytest.mark.parametrize("curve", [D1, D2])
def test_flatten_degenerated_bezier_curves(curve):
    # Degenerated Bezier curves behave like regular curves!
    assert len(list(curve.flattening(0.1))) > 4


@pytest.mark.parametrize(
    "b1,b2",
    [
        (B1, B2),  # G1 continuity, the common case
        (B1, B3),  # without G1 continuity is also a regular B-spline
        (B1, B5),  # regular B-spline, but first control point of B5 is lost
    ],
    ids=["G1", "without G1", "gap"],
)
def test_bezier_curves_to_bspline(b1, b2):
    bspline = bezier_to_bspline([b1, b2])
    # Remove duplicate control point between two adjacent curves:
    expected = list(b1.control_points) + list(b2.control_points)[1:]
    assert bspline.degree == 3, "should be a cubic B-spline"
    assert bspline.control_points == tuple(expected)


def test_quality_of_bezier_to_bspline_conversion_1():
    # This test shows the close relationship between cubic Bézier- and
    # cubic B-spline curves.
    points0 = B1.approximate(10)
    points1 = bezier_to_bspline([B1]).approximate(10)
    for p0, p1 in zip(points0, points1):
        assert p0.isclose(p1) is True, "conversion should be perfect"


def test_quality_of_bezier_to_bspline_conversion_2():
    # This test shows the close relationship between cubic Bézier- and
    # cubic B-spline curves.
    # Remove duplicate point between the two curves:
    points0 = list(B1.approximate(10)) + list(B2.approximate(10))[1:]
    points1 = bezier_to_bspline([B1, B2]).approximate(20)
    for p0, p1 in zip(points0, points1):
        assert p0.isclose(p1) is True, "conversion should be perfect"


def test_bezier_curves_to_bspline_error():
    with pytest.raises(ValueError):
        bezier_to_bspline([])  # one or more curves expected


class TestSplitBezier:
    @pytest.fixture
    def points3(self):
        return Vec2.list([(0, 0), (0, 1), (1.5, 0.75), (2, 2)])

    @pytest.mark.parametrize("t", [-1, 2])
    def test_t_validation(self, points3, t):
        with pytest.raises(ValueError):
            split_bezier(points3, t)

    def test_control_point_validation(self):
        with pytest.raises(ValueError):
            split_bezier([Vec2(0, 0)], 0.5)

    def test_split_cubic_bezier(self, points3):
        left, right = split_bezier(points3, 0.5)
        assert (
            close_vectors(
                left,
                [(0.0, 0.0), (0.0, 0.5), (0.375, 0.6875), (0.8125, 0.90625)],
            )
            is True
        )

        assert (
            close_vectors(
                right,
                [(2.0, 2.0), (1.75, 1.375), (1.25, 1.125), (0.8125, 0.90625)],
            )
            is True
        )


def test_quadratic_bezier_from_3_points():
    qbez = quadratic_bezier_from_3p((0, 0), (3, 2), (6, 0))
    assert qbez.point(0.5).isclose((3, 2))


def test_cubic_bezier_from_3_points():
    cbez = quadratic_bezier_from_3p((0, 0), (3, 2), (6, 0))
    assert cbez.point(0.5).isclose((3, 2))


class TestBezierCurveBoundingBox:
    def test_linear_curve(self):
        bbox = cubic_bezier_bbox(Bezier4P([(0, 0), (1, 1), (2, 2), (3, 3)]))
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (3, 3, 0)

    def test_reverse_linear_curve(self):
        bbox = cubic_bezier_bbox(Bezier4P([(3, 3), (2, 2), (-2, -2), (-3, -3)]))
        assert bbox.extmin == (-3, -3, 0)
        assert bbox.extmax == (3, 3, 0)

    def test_cubic_bezier_curve_with_one_extrema(self):
        curve = Bezier4P([(0, 0), (0, 1), (2, 1), (2, 0)])
        bbox = cubic_bezier_bbox(curve)
        assert bbox.extmax.y == pytest.approx(0.75)

    def test_cubic_bezier_curve_with_two_extrema(self):
        curve = Bezier4P([(0, 0), (0, 1), (2, -1), (2, 0)])
        bbox = cubic_bezier_bbox(curve)
        assert bbox.extmin.y == pytest.approx(-0.28867513459481287)
        assert bbox.extmax.y == pytest.approx(+0.28867513459481287)

    def test_closed_3d_cubic_bezier_curve(self):
        curve = Bezier4P([(0, 0, -1), (2, 3, 0), (-2, 3, 0), (0, 0, -1)])
        bbox = cubic_bezier_bbox(curve)
        assert bbox.extmin.x == pytest.approx(-0.5773502691896258)
        assert bbox.extmin.z == pytest.approx(-1.0)
        assert bbox.extmax.x == pytest.approx(+0.5773502691896258)
        assert bbox.extmax.y == pytest.approx(+2.25)
        assert bbox.extmax.z == pytest.approx(-0.25)

    def test_quadratic_bezier_curve_box(self):
        curve = Bezier3P([(0, 0), (1, 1), (2, 0)])
        bbox = quadratic_bezier_bbox(curve)
        assert bbox.extmax.y == pytest.approx(0.5)


class TestRayCubicBezierCurve2dIntersection:
    @pytest.fixture(scope="class")
    def curve(self):
        return Bezier4P([(0, -2), (2, 6), (4, -6), (6, 2)])

    def test_no_intersection(self, curve):
        assert (
            len(intersection_ray_cubic_bezier_2d((0, -6), (1, -6), curve)) == 0
        )

    def test_one_intersection_point(self, curve):
        points = intersection_ray_cubic_bezier_2d((3, -6), (3, 6), curve)
        assert len(points) == 1
        assert points[0].isclose((3, 0))

    def test_two_intersection_points(self, curve):
        points = intersection_ray_cubic_bezier_2d(
            (-1.4, -2.5), (7.1, 3.9), curve
        )
        assert len(points) == 2
        expected = (
            (0.18851028511733303, -1.3039451970881237),
            (2.5249135145844264, 0.4552289992165126),
        )
        assert all(p.isclose(e) for e, p in zip(expected, points)) is True

    def test_three_intersection_points(self, curve):
        points = intersection_ray_cubic_bezier_2d((0, 0), (1, 0), curve)
        assert len(points) == 3
        expected = (
            (0.6762099922755492, 0.0),
            (3.0, 0.0),
            (5.323790007724451, 0.0),
        )
        assert all(p.isclose(e) for e, p in zip(expected, points)) is True

    def test_collinear_ray_and_curve(self):
        curve = Bezier4P([(0, 0), (1, 0), (2, 0), (3, 0)])
        ip = intersection_ray_cubic_bezier_2d((0, 0), (1, 0), curve)
        assert len(ip) == 1
        assert ip[0].isclose((0, 0))  # ???

    @pytest.mark.parametrize("x", [0, 0.5, 1, 3])
    def test_linear_ray_and_curve(self, x):
        curve = Bezier4P([(0, 0), (1, 0), (2, 0), (3, 0)])
        # ray defined in +y direction
        ip = intersection_ray_cubic_bezier_2d((x, -1), (x, 0), curve)
        assert len(ip) == 1
        assert ip[0].isclose((x, 0))
        # ray defined in -y direction
        ip = intersection_ray_cubic_bezier_2d((x, 2), (x, 1), curve)
        assert len(ip) == 1
        assert ip[0].isclose((x, 0))
