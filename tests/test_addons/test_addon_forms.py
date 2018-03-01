# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
from ezdxf.tools.c23 import PY3
from ezdxf.addons.forms import circle, close_polygon, cube, extrude, cylinder, cone
from ezdxf.addons.forms import spline_interpolation, spline_interpolated_profiles
from ezdxf.addons.forms import from_profiles_linear, from_profiles_spline
from ezdxf.addons.forms import rotation_form
from ezdxf.algebra.base import is_close_points
from ezdxf.algebra import Vector


def test_circle_open():
    c = list(circle(8))
    assert len(c) == 8


def test_circle_closed():
    c = list(circle(8, close=True))
    assert len(c) == 9


def test_close_polygon():
    p = list(close_polygon([(1, 0), (2, 0), (3, 0), (4, 0)]))
    assert len(p) == 5
    assert p[4] == (1, 0)


def test_close_polygon_without_doublets():
    p = list(close_polygon([(1, 0), (2, 0), (3, 0), (4, 0), (1, 0)]))
    assert len(p) == 5


def test_close_circle():
    assert len(list(circle(8, close=True))) == 9
    assert len(list(close_polygon(circle(8, close=True)))) == 9
    assert len(list(close_polygon(circle(8, close=False)))) == 9


def test_cube():
    c = cube(center=True)
    assert len(c.vertices) == 8
    assert len(c.faces) == 6

    c = cube(center=False)
    assert len(c.vertices) == 8
    assert len(c.faces) == 6


def test_extrude():
    profile = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    path = ((0, 0, 0), (0, 0, 1))
    mesh = extrude(profile, path, close=True)
    assert len(mesh.vertices) == 8
    assert len(mesh.faces) == 4


def test_from_profiles_linear():
    bottom = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    top = [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
    mesh = from_profiles_linear([bottom, top], close=True, caps=True)
    assert len(mesh.vertices) == 8
    assert len(mesh.faces) == 6

    mesh = from_profiles_linear([bottom, top], close=True, caps=False)
    assert len(mesh.vertices) == 8
    assert len(mesh.faces) == 4


def test_cylinder():
    mesh = cylinder(12)
    assert len(mesh.faces) == 14  # 1x bottom, 1x top, 12x side
    assert len(mesh.vertices) == 24  # 12x bottom, 12x top

    mesh = cylinder(count=12, radius=3, top_radius=2, top_center=(1, 0, 3), caps=False)
    assert len(mesh.faces) == 12
    assert len(mesh.vertices) == 24
    assert Vector(3, 0, 3) in mesh.vertices
    assert Vector(-1, 0, 3) in mesh.vertices


@pytest.mark.skipif(PY3 is False, reason='wired division by zero exception')
def test_spline_interpolation():
    vertices = [(0., 0.), (1., 2.), (3., 1.), (5., 3.)]
    result = spline_interpolation(vertices, subdivide=4)
    assert len(result) == 13  # (len-1) * subdivide + 1
    assert is_close_points((0, 0, 0), result[0]), 'expected start point'
    assert is_close_points((5, 3, 0), result[-1]), 'expected end point'
    assert is_close_points((1, 2, 0), result[4]), 'expected 2. fit point'
    assert is_close_points((3, 1, 0), result[8]), 'expected 3. fit point'


@pytest.mark.skipif(PY3 is False, reason='wired division by zero exception')
def test_spline_interpolated_profiles():
    p1 = circle(12, radius=2, z=0, close=True)
    p2 = circle(12, radius=3, z=2, close=True)
    p3 = circle(12, radius=1, z=4, close=True)
    p4 = circle(12, radius=2, z=6, close=True)
    profiles = list(spline_interpolated_profiles([p1, p2, p3, p4], subdivide=4))
    assert len(profiles) == 13  # 3*4 + 1


@pytest.mark.skipif(PY3 is False, reason='wired division by zero exception')
def test_from_profiles_splines():
    p1 = circle(12, radius=2, z=0, close=True)
    p2 = circle(12, radius=3, z=2, close=True)
    p3 = circle(12, radius=1, z=4, close=True)
    p4 = circle(12, radius=2, z=6, close=True)
    mesh = from_profiles_spline([p1, p2, p3, p4], subdivide=4, caps=True)
    assert len(mesh.vertices) == 156  # 12 (circle) * 13 (profiles)
    assert len(mesh.faces) == 146  # 12 (circle) * 12 + 2


def test_cone():
    mesh = cone(12, 2, apex=(0, 0, 3))
    assert len(mesh.vertices) == 13
    assert len(mesh.faces) == 13


def test_rotation_form():
    profile = [(0, 0.1), (1, 1), (3, 1.5), (5, 3)]  # in xy-plane
    mesh = rotation_form(count=16, profile=profile, axis=(1, 0, 0))  # rotation axis is the x-axis
    assert len(mesh.vertices) == 16 * 4
    assert len(mesh.faces) == 16 * 3
