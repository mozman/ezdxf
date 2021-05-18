# Copyright (c) 2018-2021 Manfred Moitzi
# License: MIT License
from ezdxf.render.forms import (
    circle, close_polygon, cube, extrude, cylinder,
    cone, square, box, ngon,
)
from ezdxf.render.forms import open_arrow, arrow2
from ezdxf.render.forms import (
    spline_interpolation,
    spline_interpolated_profiles,
)
from ezdxf.render.forms import from_profiles_linear, from_profiles_spline
from ezdxf.render.forms import rotation_form, ngon_to_triangles
from ezdxf.render.forms import translate, rotate, scale
from ezdxf.math import Vec3, close_vectors


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


def test_square():
    sq = square(2)
    assert len(sq) == 4
    assert close_vectors(sq, [(0, 0), (2, 0), (2, 2), (0, 2)])


def test_box():
    b = box(3, 2)
    assert len(b) == 4
    assert close_vectors(b, [(0, 0), (3, 0), (3, 2), (0, 2)])


def test_open_arrow():
    a = open_arrow(3, 60)
    assert len(a) == 3
    assert close_vectors(a, [(-3, 1.5), (0, 0), (-3, -1.5)])


def test_closed_arrow():
    a = arrow2(3, 60, 45)
    assert len(a) == 4
    assert close_vectors(a, [(-3, 1.5), (0, 0), (-3, -1.5), (-1.5, 0)])


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


def in_vertices(v, vertices):
    v = Vec3(v)
    return any(v.isclose(v2) for v2 in vertices)


def test_cylinder():
    mesh = cylinder(12)
    assert len(mesh.faces) == 14  # 1x bottom, 1x top, 12x side
    assert len(mesh.vertices) == 24  # 12x bottom, 12x top

    mesh = cylinder(count=12, radius=3, top_radius=2, top_center=(1, 0, 3),
                    caps=False)
    assert len(mesh.faces) == 12
    assert len(mesh.vertices) == 24
    assert in_vertices((3, 0, 3), mesh.vertices)
    assert in_vertices((-1, 0, 3), mesh.vertices)


def test_spline_interpolation():
    vertices = [(0., 0.), (1., 2.), (3., 1.), (5., 3.)]
    result = spline_interpolation(vertices, method='uniform', subdivide=4)
    assert len(result) == 13  # (len-1) * subdivide + 1
    assert Vec3(0, 0, 0).isclose(result[0]), 'expected start point'
    assert Vec3(5, 3, 0).isclose(result[-1]), 'expected end point'
    assert Vec3(1, 2, 0).isclose(result[4]), 'expected 2. fit point'
    assert Vec3(3, 1, 0).isclose(result[8]), 'expected 3. fit point'


def test_spline_interpolated_profiles():
    p1 = circle(12, radius=2, elevation=0, close=True)
    p2 = circle(12, radius=3, elevation=2, close=True)
    p3 = circle(12, radius=1, elevation=4, close=True)
    p4 = circle(12, radius=2, elevation=6, close=True)
    profiles = list(spline_interpolated_profiles([p1, p2, p3, p4], subdivide=4))
    assert len(profiles) == 13  # 3*4 + 1


def test_from_profiles_splines():
    p1 = circle(12, radius=2, elevation=0, close=True)
    p2 = circle(12, radius=3, elevation=2, close=True)
    p3 = circle(12, radius=1, elevation=4, close=True)
    p4 = circle(12, radius=2, elevation=6, close=True)
    mesh = from_profiles_spline([p1, p2, p3, p4], subdivide=4, caps=True)
    assert len(mesh.vertices) == 156  # 12 (circle) * 13 (profiles)
    assert len(mesh.faces) == 146  # 12 (circle) * 12 + 2


def test_cone():
    mesh = cone(12, 2, apex=(0, 0, 3))
    assert len(mesh.vertices) == 13
    assert len(mesh.faces) == 13


def test_rotation_form():
    profile = [(0, 0.1), (1, 1), (3, 1.5), (5, 3)]  # in xy-plane
    mesh = rotation_form(count=16, profile=profile,
                         axis=(1, 0, 0))  # rotation axis is the x-axis
    assert len(mesh.vertices) == 16 * 4
    assert len(mesh.faces) == 16 * 3


def test_translate():
    p = [(1, 2, 3), (4, 5, 6)]
    r = list(translate(p, (3, 2, 1)))
    assert r[0].isclose((4, 4, 4))
    assert r[1].isclose((7, 7, 7))


def test_scale():
    p = [(1, 2, 3), (4, 5, 6)]
    r = list(scale(p, (3, 2, 1)))
    assert r[0].isclose((3, 4, 3))
    assert r[1].isclose((12, 10, 6))


def test_rotate():
    p = [(1, 0, 3), (0, 1, 6)]
    r = list(rotate(p, 90, deg=True))
    assert r[0].isclose((0, 1, 3))
    assert r[1].isclose((-1, 0, 6))


def test_square_by_radius():
    corners = list(ngon(4, radius=1))
    assert len(corners) == 4
    assert corners[0].isclose((1, 0, 0))
    assert corners[1].isclose((0, 1, 0))
    assert corners[2].isclose((-1, 0, 0))
    assert corners[3].isclose((0, -1, 0))


def test_heptagon_by_edge_length():
    corners = list(ngon(7, length=10))
    assert len(corners) == 7
    assert corners[0].isclose((11.523824354812433, 0, 0))
    assert corners[1].isclose((7.184986963636852, 9.009688679024192, 0))
    assert corners[2].isclose((-2.564292158181384, 11.234898018587335, 0))
    assert corners[3].isclose((-10.382606982861683, 5, 0))
    assert corners[4].isclose((-10.382606982861683, -5, 0))
    assert corners[5].isclose((-2.564292158181387, -11.234898018587335, 0))
    assert corners[6].isclose((7.18498696363685, -9.009688679024192, 0))


def test_ngons_to_triangles():
    open_square = square()
    r = list(ngon_to_triangles(open_square))
    assert len(r) == 4
    center = r[0][2]
    assert center == (0.5, 0.5, 0)

    closed_square = list(circle(4, elevation=2, close=True))
    assert len(closed_square) == 5
    r = list(ngon_to_triangles(closed_square))
    assert len(r) == 4
    center = r[0][2]
    assert center.isclose((0, 0, 2))

    # also subdivide triangles
    r = list(ngon_to_triangles([(0, 0), (1, 0), (1, 1)]))
    assert len(r) == 3
