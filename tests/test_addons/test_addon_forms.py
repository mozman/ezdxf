# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ezdxf.addons.forms import circle, close_polygon, cube, extrude, cylinder


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


def test_cylinder():
    mesh = cylinder(12)
    assert len(mesh.faces) == 14  # 1x bottom, 1x top, 12x side
    assert len(mesh.vertices) == 24  # 12x bottom, 12x top
