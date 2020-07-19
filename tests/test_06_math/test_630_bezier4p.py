# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.math import ConstructionEllipse, Matrix44, Vector, Vec2
from ezdxf.math.bezier4p import (
    Bezier4P, cubic_bezier_arc_parameters, cubic_bezier_interpolation, cubic_bezier_from_arc, cubic_bezier_from_ellipse
)

DEFPOINTS2D = [(0., 0.), (3., 0.), (7., 10.), (10., 10.)]
DEFPOINTS3D = [(0.0, 0.0, 0.0), (10., 20., 20.), (30., 10., 25.), (40., 10., 25.)]


def test_accepts_2d_points():
    curve = Bezier4P(DEFPOINTS2D)
    for index, chk in enumerate(Vec2.generate(POINTS2D)):
        assert curve.point(index * .1).isclose(chk)


def test_objects_are_immutable():
    curve = Bezier4P(DEFPOINTS3D)
    with pytest.raises(TypeError):
        curve.control_points[0] = (1, 2, 3)


def test_2d_tangent_computation():
    dbcurve = Bezier4P(DEFPOINTS2D)
    for index, chk in enumerate(Vec2.generate(TANGENTS2D)):
        assert dbcurve.tangent(index * .1).isclose(chk)


def test_cubic_bezier_arc_parameters_computation():
    parts = list(cubic_bezier_arc_parameters(0, math.tau))
    assert len(parts) == 4

    chk = 4.0 * (math.sqrt(2) - 1.0) / 3.0
    sp, cp1, cp2, ep = parts[0]
    assert sp.isclose((1, 0))
    assert cp1.isclose((1, chk))
    assert cp2.isclose((chk, 1))
    assert ep.isclose((0, 1))

    sp, cp1, cp2, ep = parts[1]
    assert sp.isclose((0, 1))
    assert cp1.isclose((-chk, 1))
    assert cp2.isclose((-1, chk))
    assert ep.isclose((-1, 0))

    sp, cp1, cp2, ep = parts[2]
    assert sp.isclose((-1, 0))
    assert cp1.isclose((-1, -chk))
    assert cp2.isclose((-chk, -1))
    assert ep.isclose((0, -1))

    sp, cp1, cp2, ep = parts[3]
    assert sp.isclose((0, -1))
    assert cp1.isclose((chk, -1))
    assert cp2.isclose((1, -chk))
    assert ep.isclose((1, 0))


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


def test_from_circular_arc():
    curves = list(cubic_bezier_from_arc(end_angle=90))
    assert len(curves) == 1

    bezier4p = curves[0]
    cpoints = bezier4p.control_points
    assert len(cpoints) == 4
    assert cpoints[0].isclose((1, 0, 0))
    assert cpoints[1].isclose((1.0, 0.5522847498307933, 0.0))
    assert cpoints[2].isclose((0.5522847498307935, 1.0, 0.0))
    assert cpoints[3].isclose((0, 1, 0))


def test_rational_spline_from_elliptic_arc():
    ellipse = ConstructionEllipse(
        center=(1, 1),
        major_axis=(2, 0),
        ratio=0.5,
        start_param=0,
        end_param=math.pi / 2,
    )
    curves = list(cubic_bezier_from_ellipse(ellipse))
    assert len(curves) == 1

    p1, p2, p3, p4 = curves[0].control_points
    assert p1.isclose((3, 1, 0))
    assert p2.isclose((3.0, 1.5522847498307932, 0))
    assert p3.isclose((2.104569499661587, 2.0, 0))
    assert p4.isclose((1, 2, 0))


def test_reverse():
    curve = Bezier4P(DEFPOINTS2D)
    vertices = list(curve.approximate(10))
    rev_curve = curve.reverse()
    rev_vertices = list(rev_curve.approximate(10))
    assert list(reversed(vertices)) == rev_vertices


def test_transform_interface():
    curve = Bezier4P(DEFPOINTS3D)
    new = curve.transform(Matrix44.translate(1, 2, 3))
    assert new.control_points[0] == Vector(DEFPOINTS3D[0]) + (1, 2, 3)
    assert new.control_points[0] != curve.control_points[0], 'expected a new object'


def test_transform_returns_always_3d_curves():
    curve = Bezier4P(DEFPOINTS2D)
    new = curve.transform(Matrix44.translate(1, 2, 3))
    assert len(new.control_points[0]) == 3
    assert new.control_points[0] == Vector(DEFPOINTS2D[0]) + (1, 2, 3)
    assert new.control_points[0] != curve.control_points[0], 'expected a new object'


POINTS2D = [
    (0.000, 0.000),
    (0.928, 0.280),
    (1.904, 1.040),
    (2.916, 2.160),
    (3.952, 3.520),
    (5.000, 5.000),
    (6.048, 6.480),
    (7.084, 7.840),
    (8.096, 8.960),
    (9.072, 9.720),
    (10.00, 10.00),
]

TANGENTS2D = [
    (9.0, 0.0),
    (9.5400000000000009, 5.3999999999999995),
    (9.9600000000000009, 9.6000000000000014),
    (10.26, 12.600000000000001),
    (10.440000000000001, 14.4),
    (10.5, 15.0),
    (10.44, 14.399999999999999),
    (10.260000000000002, 12.600000000000001),
    (9.9599999999999973, 9.5999999999999925),
    (9.5399999999999974, 5.399999999999995),
    (9.0, 0.0),
]
