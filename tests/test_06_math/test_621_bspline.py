# Copyright (c) 2012-2020 Manfred Moitzi
# License: MIT License
import pytest
from math import isclose
import random
from ezdxf.math import Vec3, BSpline
from ezdxf.math.bspline import (
    bspline_basis_vector, Basis,
    open_uniform_knot_vector, normalize_knots, subdivide_params,
)

DEFPOINTS = [(0.0, 0.0, 0.0), (10., 20., 20.), (30., 10., 25.), (40., 10., 25.),
             (50., 0., 30.)]


def random_point_comparision_to_nurbs_python(spline: BSpline, count: int = 10):
    curve = spline.to_nurbs_python_curve()
    for _ in range(count):
        t = random.random()
        p1 = spline.point(t)
        p2 = curve.evaluate_single(t)
        assert p1.isclose(p2)


def random_derivatives_comparision_to_nurbs_python(spline: BSpline,
                                                   count: int = 10):
    curve = spline.to_nurbs_python_curve()
    for _ in range(count):
        t = random.random()
        p1, d1_1, d2_1 = spline.derivative(t, n=2)
        p2, d1_2, d2_2 = curve.derivatives(t, order=2)
        assert p1.isclose(p2)
        assert d1_1.isclose(d1_2)
        assert d2_1.isclose(d2_2)


def test_if_nurbs_python_is_reliable():
    # Testing for some known values, just for the case
    # that NURBS-Python is incorrect.
    expected = [
        (0.0, 0.0, 0.0),
        (11.840000000000003, 13.760000000000002, 16.64),
        (22.72, 14.079999999999998, 22.719999999999995),
        (31.759999999999994, 11.2, 24.399999999999995),
        (39.92, 7.999999999999999, 26.0),
        (50.0, 0.0, 30.0)
    ]
    params = [0, .2, .4, .6, .8, 1.0]
    curve = BSpline(DEFPOINTS).to_nurbs_python_curve()
    points = curve.evaluate_list(params)
    for expect, point in zip(expected, points):
        assert Vec3(expect).isclose(point)


def test_bspline_basis_vector():
    degree = 3
    count = 10
    knots = list(open_uniform_knot_vector(count, order=degree + 1))
    max_t = max(knots)
    basis_func = Basis(knots=knots, order=degree + 1, count=count)
    for u in (0, 2., 2.5, 3.5, 4., max_t):
        basis = bspline_basis_vector(u, count=count, degree=degree, knots=knots)
        basis2 = basis_func.basis_vector(u)
        assert len(basis) == len(basis2)
        for v1, v2 in zip(basis, basis2):
            assert isclose(v1, v2)


def iter_points(values, n):
    return (data[n] for data in values)


def test_bspine_points_random():
    spline = BSpline(DEFPOINTS, order=3)
    random_point_comparision_to_nurbs_python(spline)


def test_is_clamped(weired_spline1):
    spline = BSpline(DEFPOINTS, order=3)
    assert spline.is_clamped is True
    assert weired_spline1.is_clamped is False


def test_bspine_derivatives_random():
    spline = BSpline(DEFPOINTS, order=3)
    random_derivatives_comparision_to_nurbs_python(spline)


def test_normalize_knots():
    assert normalize_knots([0, 0.25, 0.5, 0.75, 1.0]) == [0, 0.25, 0.5, 0.75,
                                                          1.0]
    assert normalize_knots([0, 1, 2, 3, 4]) == [0, 0.25, 0.5, 0.75, 1.0]
    assert normalize_knots([2, 3, 4, 5, 6]) == [0, 0.25, 0.5, 0.75, 1.0]


def test_normalize_knots_if_needed():
    s = BSpline(
        control_points=DEFPOINTS,
        knots=[2, 2, 2, 2, 3, 6, 6, 6, 6],
        order=4,
    )
    k = s.knots()
    assert k[0] == 0.0


def test_bspline_insert_knot():
    bspline = BSpline(
        [(0, 0), (10, 20), (30, 10), (40, 10), (50, 0), (60, 20), (70, 50),
         (80, 70)])
    t = bspline.max_t / 2
    assert len(bspline.control_points) == 8
    bspline.insert_knot(t)
    assert len(bspline.control_points) == 9


def test_transform_interface():
    from ezdxf.math import Matrix44
    spline = BSpline(control_points=[(1, 0, 0), (3, 3, 0), (6, 0, 1)], order=3)
    spline.transform(Matrix44.translate(1, 2, 3))
    assert spline.control_points[0] == (2, 2, 3)


def test_bezier_decomposition():
    bspline = BSpline.from_fit_points(
        [(0, 0), (10, 20), (30, 10), (40, 10), (50, 0), (60, 20), (70, 50),
         (80, 70)])
    bezier_segments = list(bspline.bezier_decomposition())
    assert len(bezier_segments) == 5
    # results visually checked to be correct
    assert bezier_segments[0] == [
        (0.0, 0.0, 0.0),
        (2.02070813064438, 39.58989657555839, 0.0),
        (14.645958536022286, 10.410103424441612, 0.0),
        (30.0, 10.0, 0.0)
    ]
    assert bezier_segments[-1] == [
        (60.0, 20.0, 0.0),
        (66.33216513897267, 43.20202388489432, 0.0),
        (69.54617236126121, 50.37880459351478, 0.0),
        (80.0, 70.0, 0.0)
    ]


def test_cubic_bezier_approximation():
    bspline = BSpline.from_fit_points(
        [(0, 0), (10, 20), (30, 10), (40, 10), (50, 0), (60, 20), (70, 50),
         (80, 70)])
    bezier_segments = list(bspline.cubic_bezier_approximation(level=3))
    assert len(bezier_segments) == 28
    bezier_segments = list(bspline.cubic_bezier_approximation(segments=40))
    assert len(bezier_segments) == 40
    # The interpolation is based on cubic_bezier_interpolation()
    # and therefore the interpolation result is not topic of this test.


def test_subdivide_params():
    assert list(subdivide_params([0.0, 1.0])) == [0.0, 0.5, 1.0]
    assert list(subdivide_params([0.0, 0.5, 1.0])) == [0.0, 0.25, 0.5, 0.75,
                                                       1.0]


@pytest.fixture
def weired_spline1():
    # test spline from: 'CADKitSamples\Tamiya TT-01.dxf'
    control_points = [
        (-52.08772752271847, 158.6939842216689, 0.0),
        (-52.08681215879965, 158.5299954819766, 0.0),
        (-52.10118023714384, 158.453369560292, 0.0),
        (-52.15481567142786, 158.3191250853181, 0.0),
        (-52.19398877522381, 158.2621809388646, 0.0),
        (-52.28596439525645, 158.1780834350967, 0.0),
        (-52.33953844794299, 158.1503467960972, 0.0),
        (-52.44810872122953, 158.1300340044323, 0.0),
        (-52.50421992306838, 158.1373171840982, 0.0),
        (-52.6075289246734, 158.1865954546344, 0.0),
        (-52.65514787710273, 158.2285032895921, 0.0),
        (-52.73668761545541, 158.3403743627349, 0.0),
        (-52.77007322118961, 158.4091709021843, 0.0),
        (-52.82282063670695, 158.5633574927312, 0.0),
        (-52.84192253131899, 158.6479284406054, 0.0),
        (-52.86740213628708, 158.8193660227095, 0.0),
        (-52.87386770841857, 158.9069288997418, 0.0),
        (-52.87483030423064, 159.0684635170357, 0.0),
        (-52.86932199691667, 159.1438624785262, 0.0),
        (-52.84560704446005, 159.2697570380293, 0.0),
        (-52.82725914916205, 159.3212520891559, 0.0),
        (-52.75022655463125, 159.4318434990425, 0.0),
        (-52.6670694478151, 159.4452110783386, 0.0),
        (-52.51141458339235, 159.3709884860868, 0.0),
        (-52.45531159130934, 159.3310594465107, 0.0),
        (-52.34571913237574, 159.2278392570542, 0.0),
        (-52.29163139562603, 159.1638425241462, 0.0),
        (-52.19834244727945, 159.0217561474263, 0.0),
        (-52.15835994602539, 158.9423430023927, 0.0),
        (-52.10315233959036, 158.778742732499, 0.0),
        (-52.08772752271847, 158.6939842216689, 0.0),
        (-52.08681215879965, 158.5299954819766, 0.0),
    ]
    knots = [
        -0.0624999999999976,
        -0.0624999999999976,
        0.0,
        0.0,
        0.0624999999999998,
        0.0624999999999998,
        0.1249999999999997,
        0.1249999999999997,
        0.1874999999999996,
        0.1874999999999996,
        0.2499999999999994,
        0.2499999999999994,
        0.3124999999999992,
        0.3124999999999992,
        0.3749999999999991,
        0.3749999999999991,
        0.4374999999999989,
        0.4374999999999989,
        0.4999999999999988,
        0.4999999999999988,
        0.5624999999999987,
        0.5624999999999987,
        0.6249999999999984,
        0.6249999999999984,
        0.7500000000000099,
        0.7500000000000099,
        0.8125000000000074,
        0.8125000000000074,
        0.875000000000005,
        0.875000000000005,
        0.9375000000000024,
        0.9375000000000024,
        1.0,
        1.0,
        1.0625,
        1.0625,
    ]
    return BSpline(control_points, order=4, knots=knots)


def test_weired_closed_spline(weired_spline1):
    first = weired_spline1.point(0)
    last = weired_spline1.point(weired_spline1.max_t)
    assert first.isclose(last,
                         1e-9) is False, 'The loaded SPLINE is not a correct closed B-spline.'
    random_point_comparision_to_nurbs_python(weired_spline1)


def test_bezier_decomposition_issue(weired_spline1):
    assert weired_spline1.is_rational is False
    assert weired_spline1.is_clamped is False
    with pytest.raises(TypeError):
        list(weired_spline1.bezier_decomposition())


# visually checked:
EXPECTED_FLATTENING = [
    Vec3(0.0, 0.0, 0.0),
    Vec3(0.1875, 1.5717773437500002, 0.0),
    Vec3(0.28125, 2.1450805664062504, 0.0),
    Vec3(0.375, 2.5898437500000004, 0.0),
    Vec3(0.46874999999999994, 2.9159545898437504, 0.0),
    Vec3(0.5625, 3.1333007812500004, 0.0),
    Vec3(0.6562499999999999, 3.251770019531251, 0.0),
    Vec3(0.7031249999999999, 3.277015686035157, 0.0),
    Vec3(0.7499999999999999, 3.281250000000001, 0.0),
    Vec3(0.8437499999999999, 3.231628417968751, 0.0),
    Vec3(0.9374999999999999, 3.1127929687500013, 0.0),
    Vec3(1.0312499999999998, 2.9346313476562513, 0.0),
    Vec3(1.1249999999999998, 2.7070312500000013, 0.0),
    Vec3(1.3124999999999998, 2.1430664062500013, 0.0),
    Vec3(1.4999999999999998, 1.5000000000000018, 0.0),
    Vec3(1.6874999999999998, 0.8569335937500013, 0.0),
    Vec3(1.8749999999999996, 0.29296875000000133, 0.0),
    Vec3(1.9687499999999996, 0.06536865234375133, 0.0),
    Vec3(2.0624999999999996, -0.11279296874999867, 0.0),
    Vec3(2.1562499999999996, -0.2316284179687489, 0.0),
    Vec3(2.2499999999999996, -0.2812499999999989, 0.0),
    Vec3(2.296875, -0.27701568603515514, 0.0),
    Vec3(2.34375, -0.2517700195312489, 0.0),
    Vec3(2.4375, -0.13330078124999956, 0.0),
    Vec3(2.53125, 0.08404541015625044, 0.0),
    Vec3(2.625, 0.41015625000000044, 0.0),
    Vec3(2.71875, 0.8549194335937504, 0.0),
    Vec3(2.8125, 1.4282226562500002, 0.0),
    Vec3(3.0, 3.0, 0.0)
]


def test_flattening():
    fitpoints = [(0, 0), (1, 3), (2, 0), (3, 3)]
    bspline = BSpline.from_fit_points(fitpoints)
    assert list(bspline.flattening(0.01, segments=4)) == EXPECTED_FLATTENING
