# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import Vec3, Vec2, Matrix44
# Import from 'ezdxf.math._bezier4p' to test Python implementation
from ezdxf.math._bezier4p import Bezier4P

curve_classes = [Bezier4P]
try:
    from ezdxf.acc.bezier4p import Bezier4P as CBezier4P

    curve_classes.append(CBezier4P)
except ImportError:
    pass

DEFPOINTS2D = [(0., 0.), (3., 0.), (7., 10.), (10., 10.)]
DEFPOINTS3D = [(0.0, 0.0, 0.0), (10., 20., 20.), (30., 10., 25.),
               (40., 10., 25.)]


@pytest.fixture(params=curve_classes)
def bezier(request):
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
