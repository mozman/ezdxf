# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
import random

import pytest
import math

from ezdxf.math import (
    Vec3, angle_to_param, linspace, ConstructionEllipse, ellipse_param_span
)


def test_default_init():
    e = ConstructionEllipse()
    assert e.center == (0, 0, 0)
    assert e.major_axis == (1, 0, 0)
    assert e.minor_axis == (0, 1, 0)
    assert e.extrusion == (0, 0, 1)
    assert e.ratio == 1.0
    assert e.start_param == 0
    assert e.end_param == math.tau


def test_dxfattribs():
    e = ConstructionEllipse()
    attribs = e.dxfattribs()
    assert attribs['center'] == (0, 0, 0)
    assert attribs['major_axis'] == (1, 0, 0)
    assert 'minor_axis' not in attribs
    assert attribs['extrusion'] == (0, 0, 1)
    assert attribs['ratio'] == 1.0
    assert attribs['start_param'] == 0
    assert attribs['end_param'] == math.tau


def test_get_start_and_end_vertex():
    ellipse = ConstructionEllipse(
        center=(1, 2, 3),
        major_axis=(4, 3, 0),
        extrusion=(0, 0, -1),
        ratio=.7,
        start_param=math.pi / 2,
        end_param=math.pi,
    )

    start, end = list(ellipse.vertices([
        ellipse.start_param,
        ellipse.end_param,
    ]))
    # test values from BricsCAD
    assert start.isclose(Vec3(3.1, -0.8, 3), abs_tol=1e-6)
    assert end.isclose(Vec3(-3, -1, 3), abs_tol=1e-6)

    # for convenience, but vertices() is much more efficient:
    assert ellipse.start_point.isclose(Vec3(3.1, -0.8, 3), abs_tol=1e-6)
    assert ellipse.end_point.isclose(Vec3(-3, -1, 3), abs_tol=1e-6)


def test_from_arc():
    ellipse = ConstructionEllipse.from_arc(center=(2, 2, 2), radius=3)
    assert ellipse.center == (2, 2, 2)
    assert ellipse.major_axis == (3, 0, 0)
    assert ellipse.ratio == 1
    assert ellipse.start_param == 0
    assert math.isclose(ellipse.end_param, math.tau)


def test_swap_axis_full_ellipse():
    ellipse = ConstructionEllipse(
        major_axis=(5, 0, 0),
        ratio=2,
    )
    assert ellipse.minor_axis.isclose((0, 10, 0))

    ellipse.swap_axis()
    assert ellipse.ratio == 0.5
    assert ellipse.major_axis == (0, 10, 0)
    assert ellipse.minor_axis == (-5, 0, 0)
    assert ellipse.start_param == 0
    assert ellipse.end_param == math.pi * 2


def test_swap_axis_half_ellipse():
    ellipse = ConstructionEllipse(
        major_axis=(5, 0, 0),
        ratio=2,
        start_param=math.pi / 2.0,
        end_param=math.pi / 2.0 * 3.0,
    )
    assert ellipse.minor_axis.isclose((0, 10, 0))

    ellipse.swap_axis()
    assert ellipse.ratio == 0.5
    assert ellipse.major_axis == (0, 10, 0)
    assert ellipse.minor_axis == (-5, 0, 0)
    assert ellipse.start_param == 0
    assert ellipse.end_param == math.pi


def non_zero_random(limit=10):
    return random.uniform(0.001, limit) * random.choice((1, -1))


def test_swap_axis_arbitrary_params():
    random_tests_count = 100
    random.seed(0)

    for _ in range(random_tests_count):
        ellipse = ConstructionEllipse(
            # avoid (0, 0, 0) as major axis
            major_axis=(non_zero_random(), non_zero_random(), 0),
            ratio=2,
            start_param=random.uniform(0, math.tau),
            end_param=random.uniform(0, math.tau),
            extrusion=(0, 0, random.choice((1, -1))),
        )

        # Test if coordinates of start- and end point stay at the same location
        # before and after swapping axis.
        start_point = ellipse.start_point
        end_point = ellipse.end_point
        minor_axis = ellipse.minor_axis
        ellipse.swap_axis()
        assert ellipse.major_axis.isclose(minor_axis, abs_tol=1e-9)
        assert ellipse.start_point.isclose(start_point, abs_tol=1e-9)
        assert ellipse.end_point.isclose(end_point, abs_tol=1e-9)


def test_params():
    count = 9
    e = ConstructionEllipse(start_param=math.pi / 2, end_param=-math.pi / 2)
    params = list(e.params(count))
    expected = list(linspace(math.pi / 2, math.pi / 2.0 * 3.0, count))
    assert params == expected


def test_angle_to_param():
    random_tests_count = 100
    random.seed(0)

    angle = 1.23
    assert math.isclose(angle_to_param(1.0, angle), angle)

    angle = 1.23 + math.pi / 2
    assert math.isclose(angle_to_param(1.0, angle), angle)

    angle = 1.23 + math.pi
    assert math.isclose(angle_to_param(1.0, angle), angle)

    angle = 1.23 + 3 * math.pi / 2
    assert math.isclose(angle_to_param(1.0, angle), angle)

    angle = math.pi / 2 + 1e-15
    assert math.isclose(angle_to_param(1.0, angle), angle)

    for _ in range(random_tests_count):
        ratio = random.uniform(1e-6, 1)
        angle = random.uniform(0, math.tau)
        param = angle_to_param(ratio, angle)
        ellipse = ConstructionEllipse(
            # avoid (0, 0, 0) as major axis
            major_axis=(non_zero_random(), non_zero_random(), 0),
            ratio=ratio,
            start_param=0,
            end_param=param,
            extrusion=(0, 0, random.choice((1, -1))),
        )
        calculated_angle = ellipse.extrusion.angle_about(ellipse.major_axis,
                                                         ellipse.end_point)
        calculated_angle_without_direction = ellipse.major_axis.angle_between(
            ellipse.end_point)
        assert math.isclose(calculated_angle, angle, abs_tol=1e-9)
        assert (math.isclose(calculated_angle,
                             calculated_angle_without_direction) or
                math.isclose(math.tau - calculated_angle,
                             calculated_angle_without_direction))


def test_vertices():
    e = ConstructionEllipse(center=(3, 3), major_axis=(2, 0), ratio=0.5,
                            start_param=0, end_param=math.pi * 1.5)
    params = list(e.params(7))
    result = [
        (5.0, 3.0, 0.0),
        (4.414213562373095, 3.7071067811865475, 0.0),
        (3.0, 4.0, 0.0),
        (1.585786437626905, 3.7071067811865475, 0.0),
        (1.0, 3.0, 0.0),
        (1.5857864376269046, 2.2928932188134525, 0.0),
        (3.0, 2.0, 0.0),
    ]
    for v, r in zip(e.vertices(params), result):
        assert v.isclose(r)

    v1, v2 = e.vertices([0, math.tau])
    assert v1 == v2


def test_tangents():
    e = ConstructionEllipse(center=(3, 3), major_axis=(2, 0), ratio=0.5,
                            start_param=0, end_param=math.pi * 1.5)
    params = list(e.params(7))
    result = [
        (0.0, 1.0, 0.0),
        (-0.894427190999916, 0.447213595499958, 0.0),
        (-1.0, 3.061616997868383e-17, 0.0),
        (-0.894427190999916, -0.4472135954999579, 0.0),
        (-2.4492935982947064e-16, -1.0, 0.0),
        (0.8944271909999159, -0.44721359549995804, 0.0),
        (1.0, 0.0, 0.0)
    ]
    for v, r in zip(e.tangents(params), result):
        assert v.isclose(r)


def test_params_from_vertices_random():
    center = Vec3.random(5)
    major_axis = Vec3.random(5)
    extrusion = Vec3.random()
    ratio = 0.75
    e = ConstructionEllipse(center, major_axis, extrusion, ratio)

    params = [random.uniform(0.0001, math.tau - 0.0001) for _ in range(20)]
    vertices = e.vertices(params)
    new_params = e.params_from_vertices(vertices)
    for expected, param in zip(params, new_params):
        assert math.isclose(expected, param)

    # This creates the same vertex as v1 and v2
    v1, v2 = e.vertices([0, math.tau])
    assert v1.isclose(v2)

    # This should create the same param for v1 and v2, but
    # floating point inaccuracy produces unpredictable results:
    p1, p2 = e.params_from_vertices((v1, v2))

    assert math.isclose(p1, 0, abs_tol=1e-9) or math.isclose(p1, math.tau,
                                                             abs_tol=1e-9)
    assert math.isclose(p2, 0, abs_tol=1e-9) or math.isclose(p2, math.tau,
                                                             abs_tol=1e-9)


def test_to_ocs():
    e = ConstructionEllipse().to_ocs()
    assert e.center == (0, 0)


@pytest.mark.parametrize('s, e, distance, count', [
    # known tests from ARC
    (0, 180, 0.35, 3),
    (0, 180, 0.10, 5),
    (270, 90, 0.10, 5),  # start angle > end angle
    (90, -90, 0.10, 5),
    (0, 0, 0.10, 0),  # angle span 0 works but yields nothing
    (-45, -45, 0.10, 0),
])
def test_flattening(s, e, distance, count):
    ellipse = ConstructionEllipse(
        start_param=math.radians(s),
        end_param=math.radians(e),
    )
    assert len(list(ellipse.flattening(distance, segments=2))) == count


def test_flattening_ellipse():
    # Visually checked in BricsCAD:
    e = ConstructionEllipse(major_axis=(3, 0), ratio=0.25)
    assert len(list(e.flattening(0.1))) == 13
    assert len(list(e.flattening(0.01))) == 37


PI2 = math.pi / 2.0


class TestParamSpan:
    @pytest.mark.parametrize('start, end', [
        (0, 0), (math.pi, math.pi), (math.tau, math.tau),
        (0, 0), (-math.pi, -math.pi), (-math.tau, -math.tau),
    ])
    def test_no_ellipse(self, start, end):
        e = ConstructionEllipse(start_param=start, end_param=end)
        assert e.param_span == 0.0

    @pytest.mark.parametrize('start, end', [
        (0, math.tau), (math.tau, 0), (math.pi, -math.pi),
        (0, -math.tau), (-math.tau, 0), (-math.pi, math.pi),
    ])
    def test_full_ellipse(self, start, end):
        e = ConstructionEllipse(start_param=start, end_param=end)
        assert e.param_span == pytest.approx(math.tau)

    @pytest.mark.parametrize('start, end, expected', [
        (0, PI2, PI2), (PI2, 0, math.pi * 1.5), (PI2, math.pi, PI2),
        (PI2, -PI2, math.pi), (math.pi, 0, math.pi), (0, math.pi, math.pi),
        (0, -PI2, math.pi * 1.5), (-PI2, 0, PI2),
        (-PI2, -math.pi, math.pi * 1.5),
        (-PI2, PI2, math.pi), (-math.pi, 0, math.pi), (0, -math.pi, math.pi),
    ])
    def test_elliptic_arc(self, start, end, expected):
        e = ConstructionEllipse(start_param=start, end_param=end)
        assert e.param_span == pytest.approx(expected)
