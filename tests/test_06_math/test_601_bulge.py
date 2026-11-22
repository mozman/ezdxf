# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.math import (
    bulge_radius,
    bulge_center,
    arc_to_bulge,
    bulge_3_points,
    bulge_to_arc,
    bulge_from_radius_and_chord,
    bulge_from_arc_angle,
)


def test_bulge_radius():
    assert bulge_radius((0, 0), (1, 0), 1) == 0.5
    assert bulge_radius((0, 0), (1, 0), -1) == 0.5


def test_bulge_center():
    assert bulge_center((0, 0), (1, 0), 1).isclose((0.5, 0))
    assert bulge_center((0, 0), (1, 0), -1).isclose((0.5, 0))


def test_arc_to_bulge():
    start, end, bulge = arc_to_bulge(
        center=(0.5, 0), start_angle=math.pi, end_angle=0, radius=0.5
    )
    assert start.isclose((0.0, 0.0, 0.0))
    assert end.isclose((1.0, 0.0, 0.0))
    assert math.isclose(bulge, 1.0)


def test_bulge_3_points():
    assert math.isclose(
        bulge_3_points(start_point=(0, 0), end_point=(1, 0), point=(0.5, -0.5)),
        1.0,
    )


@pytest.mark.parametrize("point", [(-1, 0), (0.5, 0), (2, 0)])
def test_bulge_3_points_collinear(point):
    # collinear points describe a straight segment
    assert bulge_3_points(start_point=(0, 0), end_point=(1, 0), point=point) == 0.0


@pytest.mark.parametrize("point", [(0, 0), (1, 0)])
def test_bulge_3_points_equal_points(point):
    # the third point is equal to the start- or end point
    assert bulge_3_points(start_point=(0, 0), end_point=(1, 0), point=point) == 0.0


def test_bulge_to_arc():
    center, start_angle, end_angle, radius = bulge_to_arc(
        start_point=(0, 0), end_point=(1, 0), bulge=-1
    )
    assert center.isclose((0.5, 0.0, 0.0))
    assert math.isclose(start_angle, 0, abs_tol=1e-15)
    assert math.isclose(end_angle, math.pi)
    assert radius == 0.5


def test_bulge_to_arc_bulge_zero_raises():
    with pytest.raises(ValueError):
        bulge_to_arc(start_point=(0, 0), end_point=(1, 0), bulge=0.0)


def test_bulge_to_arc_zero_length_chord():
    center, start_angle, end_angle, radius = bulge_to_arc(
        start_point=(0, 0), end_point=(0, 0), bulge=0.5
    )
    assert center.isclose((0, 0))
    assert start_angle == 0.0
    assert end_angle == 0.0
    assert radius == 0.0


@pytest.mark.parametrize("func", [bulge_radius, bulge_center])
def test_bulge_zero_raises(func):
    with pytest.raises(ValueError):
        func((0, 0), (1, 0), 0.0)


def test_arc_to_bulge_full_circle():
    # a full circle is not representable by a bulge value
    start, end, bulge = arc_to_bulge(
        center=(0, 0), start_angle=0, end_angle=2 * math.pi, radius=1
    )
    assert bulge == 0.0


def test_arc_to_bulge_clockwise_sweep_is_normalized():
    # a clockwise sweep of -pi/2 covers the same points as the counter-clockwise
    # sweep of 3 * pi / 2
    assert math.isclose(
        arc_to_bulge(center=(0, 0), start_angle=0, end_angle=-math.pi / 2, radius=1)[2],
        math.tan(3 * math.pi / 8),
    )


class TestBulgeFromRadiusAndChord:
    def test_semi_circle_bulge(self):
        assert math.isclose(bulge_from_radius_and_chord(5.0, 10), 1.0)

    def test_half_bulge(self):
        assert math.isclose(bulge_from_radius_and_chord(6.25, 10), 0.50)

    def test_radius_of_zero(self):
        assert bulge_from_radius_and_chord(0, 10) == 0.0

    def test_too_small_radius_for_chord(self):
        assert bulge_from_radius_and_chord(1, 10) == 0.0

    def test_radius_and_chord_sign_is_ignored(self):
        assert math.isclose(bulge_from_radius_and_chord(-5.0, 10), 1.0)
        assert math.isclose(bulge_from_radius_and_chord(5.0, -10), 1.0)
        assert math.isclose(bulge_from_radius_and_chord(-6.25, -10), 0.5)

    def test_rounded_semicircle_radius(self):
        # radius is one ulp below chord / 2
        radius = 0.5 - 2.220446049250313e-16
        assert math.isclose(bulge_from_radius_and_chord(radius, 1.0), 1.0)


@pytest.mark.parametrize("angle,bulge", [
    (180, 1.0),
    (-180, -1.0),
    (106.26020471, 0.5),
    (-106.26020471, -0.5),
    (56.14497387, 0.25),
    (-56.14497387, -0.25),
])
def test_bulge_from_arc_angle(angle, bulge):
    assert math.isclose(bulge_from_arc_angle(math.radians(angle)), bulge)


@pytest.mark.parametrize("angle", [2 * math.pi, -2 * math.pi, 4 * math.pi])
def test_bulge_from_arc_angle_full_circle(angle):
    # a full circle is not representable by a bulge value
    assert bulge_from_arc_angle(angle) == 0.0

