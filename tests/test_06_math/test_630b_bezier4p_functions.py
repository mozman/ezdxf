# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
import pytest
import random

from ezdxf.math import (
    cubic_bezier_interpolation, Vec3, Bezier3P, quadratic_to_cubic_bezier,
    Bezier4P, have_bezier_curves_g1_continuity, bezier_to_bspline,
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
    assert have_bezier_curves_g1_continuity(B1, B4, g1_tol=1e-4) is False, \
        "should be outside of tolerance "
    assert have_bezier_curves_g1_continuity(B1, B5) is False, \
        "end- and start point should match"


@pytest.mark.parametrize("b1,b2", [
    (B1, B2),  # G1 continuity, the common case
    (B1, B3),  # without G1 continuity is also a regular B-spline
    (B1, B5),  # regular B-spline, but first control point of B5 is lost
], ids=["G1", "without G1", "gap"])
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
