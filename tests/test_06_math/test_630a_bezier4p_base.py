# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.math import Vec3, Vec2, Matrix44, ConstructionEllipse
# Import from 'ezdxf.math._bezier4p' to test Python implementation
from ezdxf.math._bezier4p import Bezier4P
from ezdxf.math._bezier4p import cubic_bezier_arc_parameters
from ezdxf.math._bezier4p import cubic_bezier_from_arc
from ezdxf.math._bezier4p import cubic_bezier_from_ellipse
from ezdxf.acc import USE_C_EXT

curve_classes = [Bezier4P]
arc_params_funcs = [cubic_bezier_arc_parameters]
arc_funcs = [cubic_bezier_from_arc]
ellipse_funcs = [cubic_bezier_from_ellipse]

if USE_C_EXT:
    from ezdxf.acc.bezier4p import Bezier4P as CBezier4P
    from ezdxf.acc.bezier4p import \
        cubic_bezier_arc_parameters as cython_arc_parameters
    from ezdxf.acc.bezier4p import cubic_bezier_from_arc as cython_arc_func
    from ezdxf.acc.bezier4p import \
        cubic_bezier_from_ellipse as cython_ellipse_func

    curve_classes.append(CBezier4P)
    arc_params_funcs.append(cython_arc_parameters)
    arc_funcs.append(cython_arc_func)
    ellipse_funcs.append(cython_ellipse_func)

DEFPOINTS2D = [(0., 0.), (3., 0.), (7., 10.), (10., 10.)]
DEFPOINTS3D = [(0.0, 0.0, 0.0), (10., 20., 20.), (30., 10., 25.),
               (40., 10., 25.)]


@pytest.fixture(params=curve_classes)
def bezier(request):
    return request.param


@pytest.fixture(params=arc_params_funcs)
def arc_params(request):
    return request.param


@pytest.fixture(params=arc_funcs)
def arc(request):
    return request.param


@pytest.fixture(params=ellipse_funcs)
def ellipse(request):
    return request.param


def test_accepts_2d_points(bezier):
    curve = bezier(DEFPOINTS2D)
    for index, chk in enumerate(Vec2.generate(POINTS2D)):
        assert curve.point(index * .1).isclose(chk)


def test_objects_are_immutable(bezier):
    curve = bezier(DEFPOINTS3D)
    with pytest.raises(TypeError):
        curve.control_points[0] = (1, 2, 3)


def test_2d_tangent_computation(bezier):
    dbcurve = bezier(DEFPOINTS2D)
    for index, chk in enumerate(Vec2.generate(TANGENTS2D)):
        assert dbcurve.tangent(index * .1).isclose(chk)


def test_approximate(bezier):
    curve = bezier([(0, 0), (0, 1), (1, 1), (1, 0)])
    with pytest.raises(ValueError):
        list(curve.approximate(0))
    assert list(curve.approximate(1)) == [(0, 0), (1, 0)]
    assert list(curve.approximate(2)) == [(0, 0), (0.5, 0.75), (1, 0)]


def test_reverse(bezier):
    curve = bezier(DEFPOINTS2D)
    vertices = list(curve.approximate(10))
    rev_curve = curve.reverse()
    rev_vertices = list(rev_curve.approximate(10))
    assert list(reversed(vertices)) == rev_vertices


def test_transform_interface(bezier):
    curve = bezier(DEFPOINTS3D)
    new = curve.transform(Matrix44.translate(1, 2, 3))
    assert new.control_points[0] == Vec3(DEFPOINTS3D[0]) + (1, 2, 3)
    assert new.control_points[0] != curve.control_points[
        0], 'expected a new object'


def test_transform_returns_always_3d_curves(bezier):
    curve = bezier(DEFPOINTS2D)
    new = curve.transform(Matrix44.translate(1, 2, 3))
    assert len(new.control_points[0]) == 3


def test_flattening(bezier):
    curve = bezier([(0, 0), (1, 1), (2, -1), (3, 0)])
    assert len(list(curve.flattening(1.0, segments=4))) == 5
    assert len(list(curve.flattening(0.1, segments=4))) == 7


def test_cubic_bezier_arc_parameters_computation(arc_params):
    parts = list(arc_params(0, math.tau))
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


def test_from_circular_arc(arc):
    curves = list(arc(end_angle=90))
    assert len(curves) == 1

    bezier4p = curves[0]
    cpoints = bezier4p.control_points
    assert len(cpoints) == 4
    assert cpoints[0].isclose((1, 0, 0))
    assert cpoints[1].isclose((1.0, 0.5522847498307933, 0.0))
    assert cpoints[2].isclose((0.5522847498307935, 1.0, 0.0))
    assert cpoints[3].isclose((0, 1, 0))


def test_bezier_curves_from_simple_elliptic_arc(ellipse):
    ellipse_ = ConstructionEllipse(
        center=(1, 1),
        major_axis=(2, 0),
        ratio=0.5,
        start_param=0,
        end_param=math.pi / 2,
    )
    curves = list(ellipse(ellipse_))
    assert len(curves) == 1

    p1, p2, p3, p4 = curves[0].control_points
    assert p1.isclose((3, 1, 0))
    assert p2.isclose((3.0, 1.5522847498307932, 0))
    assert p3.isclose((2.104569499661587, 2.0, 0))
    assert p4.isclose((1, 2, 0))


def test_bezier_curves_from_complex_elliptic_arc(ellipse):
    ellipse_ = ConstructionEllipse(
        center=(49.64089977339618, 36.43095770602131, 0.0),
        major_axis=(16.69099826506408, 6.96203799241026, 0.0),
        ratio=0.173450304570581,
        start_param=5.427509144462117,
        end_param=7.927025930557775,
    )
    curves = list(ellipse(ellipse_))

    assert curves[0].control_points[0].isclose(ellipse_.start_point)
    assert curves[1].control_points[-1].isclose(ellipse_.end_point)


def test_arc_params_issue_708(arc_params):
    cpts = list(arc_params(-2.498091544796509, -0.6435011087932844))
    assert cpts[0] == (
        Vec3(-0.8, -0.6, 0.0),
        Vec3(-0.6111456180001683, -0.8518058426664423, 0.0),
        Vec3(-0.3147573033330529, -1.0, 0.0),
        Vec3(6.123233995736766e-17, -1.0, 0.0)
    )
    assert cpts[1] == (
        Vec3(6.123233995736766e-17, -1.0, 0.0),
        Vec3(0.314757303333053, -1.0, 0.0),
        Vec3(0.6111456180001683, -0.8518058426664423, 0.0),
        Vec3(0.8, -0.5999999999999999, 0.0)
    )


def test_bezier_curves_ellipse_issue_708(ellipse):
    ellipse_ = ConstructionEllipse(
        center=(1.5, 0.375, 0.0),
        major_axis=(0.625, 0.0, 0.0),
        ratio=1.0,
        start_param=-2.498091544796509,
        end_param=-0.6435011087932844,
    )
    curves = list(ellipse(ellipse_))
    assert curves[0].control_points == (
        Vec3(0.9999999999999999, 1.6653345369377348e-16, 0.0),
        Vec3(1.1180339887498947, -0.15737865166652631, 0.0),
        Vec3(1.3032766854168418, -0.2499999999999999, 0.0),
        Vec3(1.4999999999999998, -0.25, 0.0)
    )
    assert curves[1].control_points == (
        Vec3(1.4999999999999998, -0.25, 0.0),
        Vec3(1.696723314583158, -0.25, 0.0),
        Vec3(1.881966011250105, -0.15737865166652654, 0.0),
        Vec3(2.0, -5.551115123125783e-17, 0.0)
    )


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
