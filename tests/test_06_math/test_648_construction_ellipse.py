# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import random

import pytest
import math

from ezdxf.math import Vector, angle_to_param, linspace, ConstructionEllipse


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
        start=math.pi / 2,
        end=math.pi,
    )

    start, end = list(ellipse.vertices([
        ellipse.start_param,
        ellipse.end_param,
    ]))
    # test values from BricsCAD
    assert start.isclose(Vector(3.1, -0.8, 3), abs_tol=1e-6)
    assert end.isclose(Vector(-3, -1, 3), abs_tol=1e-6)

    # for convenience, but vertices() is much more efficient:
    assert ellipse.start_point.isclose(Vector(3.1, -0.8, 3), abs_tol=1e-6)
    assert ellipse.end_point.isclose(Vector(-3, -1, 3), abs_tol=1e-6)


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
        start=math.pi / 2.0,
        end=math.pi / 2.0 * 3.0,
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
            start=random.uniform(0, math.tau),
            end=random.uniform(0, math.tau),
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
    e = ConstructionEllipse(start=math.pi / 2, end=-math.pi / 2)
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
            start=0,
            end=param,
            extrusion=(0, 0, random.choice((1, -1))),
        )
        calculated_angle = ellipse.extrusion.angle_about(ellipse.major_axis, ellipse.end_point)
        calculated_angle_without_direction = ellipse.major_axis.angle_between(ellipse.end_point)
        assert math.isclose(calculated_angle, angle, abs_tol=1e-9)
        assert (math.isclose(calculated_angle, calculated_angle_without_direction) or
                math.isclose(math.tau - calculated_angle, calculated_angle_without_direction))
