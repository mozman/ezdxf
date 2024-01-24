# Copyright (c) 2012-2024 Manfred Moitzi
# License: MIT License

import math
from math import isclose

from ezdxf.math import (
    rational_bspline_from_arc,
    rational_bspline_from_ellipse,
    ConstructionEllipse,
    ConstructionArc,
    BSpline,
    open_uniform_bspline,
)
from ezdxf.math.bspline import nurbs_arc_parameters, required_knot_values

DEFPOINTS = [
    (0.0, 0.0, 0.0),
    (10.0, 20.0, 20.0),
    (30.0, 10.0, 25.0),
    (40.0, 10.0, 25.0),
    (50.0, 0.0, 30.0),
]
DEFWEIGHTS = [1, 10, 10, 10, 1]


def test_rbspline():
    curve = BSpline(DEFPOINTS, order=3, weights=DEFWEIGHTS)
    expected = RBSPLINE
    points = list(curve.approximate(40))

    for rpoint, epoint in zip(points, expected):
        epx, epy, epz = epoint
        rpx, rpy, rpz = rpoint
        assert isclose(epx, rpx)
        assert isclose(epy, rpy)
        assert isclose(epz, rpz)


def test_rbsplineu():
    curve = open_uniform_bspline(DEFPOINTS, order=3, weights=DEFWEIGHTS)
    expected = RBSPLINEU
    points = list(curve.approximate(40))

    for rpoint, epoint in zip(points, expected):
        epx, epy, epz = epoint
        rpx, rpy, rpz = rpoint
        assert isclose(epx, rpx)
        assert isclose(epy, rpy)
        assert isclose(epz, rpz)


def test_rational_spline_from_circular_arc_has_expected_parameters():
    arc = ConstructionArc(end_angle=90)
    spline = rational_bspline_from_arc(end_angle=arc.end_angle)
    assert spline.degree == 2

    cpoints = spline.control_points
    assert len(cpoints) == 3
    assert cpoints[0].isclose((1, 0, 0))
    assert cpoints[1].isclose((1, 1, 0))
    assert cpoints[2].isclose((0, 1, 0))

    weights = spline.weights()
    assert len(weights) == 3
    assert weights[0] == 1.0
    assert weights[1] == math.cos(math.pi / 4)
    assert weights[2] == 1.0

    # as BSpline constructor()
    s2 = BSpline.from_arc(arc)
    assert spline.control_points == s2.control_points


def test_rational_spline_from_circular_arc_has_same_end_points():
    arc = ConstructionArc(start_angle=30, end_angle=330)
    spline = rational_bspline_from_arc(
        start_angle=arc.start_angle, end_angle=arc.end_angle
    )
    assert arc.start_point.isclose(spline.control_points[0])
    assert arc.end_point.isclose(spline.control_points[-1])


def test_rational_spline_from_elliptic_arc_has_expected_parameters():
    ellipse = ConstructionEllipse(
        center=(1, 1),
        major_axis=(2, 0),
        ratio=0.5,
        start_param=0,
        end_param=math.pi / 2,
    )
    spline = rational_bspline_from_ellipse(ellipse)
    assert spline.degree == 2

    cpoints = spline.control_points
    assert len(cpoints) == 3
    assert cpoints[0].isclose((3, 1, 0))
    assert cpoints[1].isclose((3, 2, 0))
    assert cpoints[2].isclose((1, 2, 0))

    weights = spline.weights()
    assert len(weights) == 3
    assert weights[0] == 1.0
    assert weights[1] == math.cos(math.pi / 4)
    assert weights[2] == 1.0

    # as BSpline constructor()
    s2 = BSpline.from_ellipse(ellipse)
    assert spline.control_points == s2.control_points


def test_rational_spline_from_elliptic_arc_has_same_end_points():
    ellipse = ConstructionEllipse(
        center=(1, 1),
        major_axis=(2, 0),
        ratio=0.5,
        start_param=math.radians(30),
        end_param=math.radians(330),
    )
    start_point = ellipse.start_point
    end_point = ellipse.end_point
    spline = rational_bspline_from_ellipse(ellipse)
    assert start_point.isclose(spline.control_points[0])
    assert end_point.isclose(spline.control_points[-1])


def test_nurbs_arc_parameter_quarter_arc_1_segment():
    control_points, weights, knots = nurbs_arc_parameters(
        start_angle=0, end_angle=math.pi / 2, segments=1
    )

    assert len(control_points) == 3
    assert len(weights) == len(control_points)
    assert len(knots) == required_knot_values(len(control_points), order=3)

    assert control_points[0].isclose((1, 0, 0))
    assert control_points[1].isclose((1, 1, 0))
    assert control_points[2].isclose((0, 1, 0))

    assert weights[0] == 1.0
    assert weights[1] == math.cos(math.pi / 4)
    assert weights[2] == 1.0


def test_nurbs_arc_parameter_quarter_arc_4_segments():
    control_points, weights, knots = nurbs_arc_parameters(
        start_angle=0, end_angle=math.pi / 2, segments=4
    )
    assert len(control_points) == 9
    assert len(weights) == len(control_points)
    assert len(knots) == required_knot_values(len(control_points), order=3)


def test_nurbs_arc_parameter_full_circle():
    control_points, weights, knots = nurbs_arc_parameters(
        start_angle=0, end_angle=2 * math.pi, segments=4
    )
    cos_pi_4 = math.cos(math.pi / 4)
    assert knots == [
        0.0,
        0.0,
        0.0,
        0.25,
        0.25,
        0.5,
        0.5,
        0.75,
        0.75,
        1.0,
        1.0,
        1.0,
    ]
    assert weights == [
        1.0,
        cos_pi_4,
        1.0,
        cos_pi_4,
        1.0,
        cos_pi_4,
        1.0,
        cos_pi_4,
        1.0,
    ]


RBSPLINE = [
    [0.0, 0.0, 0.0],
    [6.523511823865181, 12.435444414243, 12.618918184289209],
    [8.577555396711936, 15.546819156540385, 16.02930664760543],
    [9.79458577064345, 16.834444293293426, 17.66086246769147],
    [10.73345259391771, 17.441860465116278, 18.64937388193202],
    [11.566265060240964, 17.710843373493976, 19.337349397590362],
    [12.366884232222603, 17.777396083819994, 19.864307798007555],
    [13.17543722061015, 17.70449376519489, 20.29840796800251],
    [14.018691588785048, 17.52336448598131, 20.677570093457945],
    [14.918157331307409, 17.249119414324195, 21.025277988811382],
    [15.894039735099337, 16.887417218543046, 21.357615894039736],
    [16.967671444180215, 16.437431711549586, 21.68680506459284],
    [18.163471241170534, 15.893037336024218, 22.023208879919274],
    [19.510974923394407, 15.242949158901883, 22.376649365267962],
    [20.9875, 14.5125, 22.74375],
    [22.421875, 13.828125, 23.0859375],
    [23.799999999999997, 13.2, 23.4],
    [25.121875000000003, 12.628125000000004, 23.685937500000005],
    [26.387500000000003, 12.112500000000002, 23.94375],
    [27.596875, 11.653125, 24.1734375],
    [28.75, 11.25, 24.375],
    [29.846874999999997, 10.903125, 24.5484375],
    [30.887500000000003, 10.6125, 24.69375],
    [31.871875, 10.378125, 24.8109375],
    [32.8, 10.2, 24.900000000000002],
    [33.671875, 10.078125, 24.9609375],
    [34.4875, 10.0125, 24.993750000000002],
    [35.24482521418298, 9.999374648239638, 25.00031267588019],
    [35.923309788092844, 9.989909182643796, 25.00504540867811],
    [36.53191079118195, 9.968506973455877, 25.01574651327206],
    [37.086092715231786, 9.933774834437086, 25.03311258278146],
    [37.59928171835071, 9.88327923199116, 25.05836038400442],
    [38.084112149532714, 9.813084112149534, 25.093457943925237],
    [38.553838914594934, 9.716884950199985, 25.14155752490001],
    [39.02439024390243, 9.584335279972517, 25.20783236001374],
    [39.51807228915663, 9.397590361445783, 25.30120481927711],
    [40.07155635062611, 9.123434704830053, 25.438282647584973],
    [40.75635967895525, 8.692694871446063, 25.653652564276967],
    [41.74410293066476, 7.9342387419585405, 26.03288062902073],
    [43.59880402283228, 6.278880130470243, 26.860559934764876],
    [50.0, 0.0, 30.0],
]

RBSPLINEU = [
    [9.09090909090909, 18.18181818181818, 18.18181818181818],
    [9.395802632247573, 18.562935108491285, 18.631536155292444],
    [9.798110761252083, 18.762733839599925, 19.012780144471197],
    [10.282214894437072, 18.83002869256135, 19.350349021455187],
    [10.840282232200128, 18.794098781270048, 19.66003848620911],
    [11.469194312796208, 18.672985781990523, 19.952606635071092],
    [12.169005932571265, 18.477789031978006, 20.23585588192736],
    [12.94215853361622, 18.215018608048418, 20.515808145803625],
    [13.793103448275861, 17.887931034482758, 20.79741379310345],
    [14.728173496505788, 17.497293218281442, 21.08500935070048],
    [15.755627009646302, 17.041800643086816, 21.382636655948552],
    [16.88583288443867, 16.518267372223452, 21.69428689121962],
    [18.131592164741335, 15.921647413360123, 22.024108488196887],
    [19.50861179706793, 15.24491263167766, 22.37660592041512],
    [20.9875, 14.5125, 22.74375],
    [22.421875, 13.828125, 23.0859375],
    [23.8, 13.199999999999998, 23.399999999999995],
    [25.121875000000003, 12.628125000000004, 23.685937500000005],
    [26.387499999999992, 12.112500000000002, 23.943749999999998],
    [27.596874999999997, 11.653125000000001, 24.1734375],
    [28.75, 11.25, 24.375],
    [29.846875000000004, 10.903125, 24.548437500000002],
    [30.887500000000003, 10.6125, 24.69375],
    [31.871874999999996, 10.378125, 24.810937499999998],
    [32.8, 10.2, 24.900000000000002],
    [33.671875, 10.078125, 24.9609375],
    [34.4875, 10.0125, 24.99375],
    [35.24585039542372, 9.99968741208465, 25.000156293957684],
    [35.93671521848317, 9.994977398292315, 25.00251130085384],
    [36.564846794892105, 9.984473525777116, 25.007763237111444],
    [37.138263665594856, 9.967845659163988, 25.016077170418008],
    [37.66363725844023, 9.944551986613734, 25.027724006693134],
    [38.146551724137936, 9.913793103448276, 25.043103448275865],
    [38.59170115822057, 9.87443914994261, 25.062780425028688],
    [39.003038634061646, 9.824916799305457, 25.087541600347276],
    [39.383886255924175, 9.763033175355451, 25.118483412322274],
    [39.737010904425915, 9.685695958948045, 25.15715202052598],
    [40.06466532482549, 9.588454455911952, 25.205772772044025],
    [40.36858677532876, 9.464715688090386, 25.267642155954803],
    [40.6499313989532, 9.304334569846029, 25.347832715076986],
    [40.90909090909091, 9.09090909090909, 25.454545454545453],
]


def test_flattening_issue():
    from ezdxf.layouts import VirtualLayout

    layout = VirtualLayout()
    # this configuration caused an math domain error in distance_point_line_3d()
    # sqrt() of negative number, cause by floating point imprecision for very
    # small numbers.
    e = layout.add_spline(
        degree=2,
        dxfattribs={
            "layer": "0",
            "linetype": "Continuous",
            "color": 84,
            "lineweight": 0,
            "extrusion": (0.0, 0.0, 1.0),
            "flags": 12,
            "knot_tolerance": 1e-09,
            "control_point_tolerance": 1e-10,
        },
    )
    e.control_points = [
        (696603.8306266892, 5711646.357537143, -2.8298889e-09),
        (696603.8352219285, 5711646.36068357, -2.8298889e-09),
        (696603.8392015211, 5711646.363408451, -2.8298889e-09),
    ]
    e.knots = [
        -6.110343499933633,
        -6.110343499933633,
        -6.110343499933633,
        -4.326590114514485,
        -4.326590114514485,
        -4.326590114514485,
    ]
    e.weights = [
        1.607007851100765,
        1.731310340973351,
        1.731310340973339,
    ]
    points = list(e.flattening(0.01))
    assert len(points) > 4
