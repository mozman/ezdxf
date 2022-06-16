# Copyright (c) 2018-2021 Manfred Moitzi
# License: MIT License
import pytest

import math
from ezdxf.math import Vec3, close_vectors, UCS
from ezdxf.render import forms


def test_circle_open():
    c = list(forms.circle(8))
    assert len(c) == 8


def test_circle_closed():
    c = list(forms.circle(8, close=True))
    assert len(c) == 9


def test_close_polygon():
    p = forms.close_polygon(Vec3.generate([(1, 0), (2, 0), (3, 0), (4, 0)]))
    assert len(p) == 5
    assert p[4] == (1, 0)


def test_close_polygon_without_doublets():
    p = forms.close_polygon(
        Vec3.generate([(1, 0), (2, 0), (3, 0), (4, 0), (1, 0)])
    )
    assert len(p) == 5


def test_close_circle():
    assert len(list(forms.circle(8, close=True))) == 9
    assert len(forms.close_polygon(forms.circle(8, close=True))) == 9
    assert len(forms.close_polygon(forms.circle(8, close=False))) == 9


def test_square():
    sq = forms.square(2)
    assert len(sq) == 4
    assert close_vectors(sq, [(0, 0), (2, 0), (2, 2), (0, 2)])


def test_box():
    b = forms.box(3, 2)
    assert len(b) == 4
    assert close_vectors(b, [(0, 0), (3, 0), (3, 2), (0, 2)])


def test_open_arrow():
    a = forms.open_arrow(3, 60)
    assert len(a) == 3
    assert close_vectors(a, [(-3, 1.5), (0, 0), (-3, -1.5)])


def test_closed_arrow():
    a = forms.arrow2(3, 60, 45)
    assert len(a) == 4
    assert close_vectors(a, [(-3, 1.5), (0, 0), (-3, -1.5), (-1.5, 0)])


def test_cube():
    c = forms.cube(center=True)
    assert len(c.vertices) == 8
    assert len(c.faces) == 6

    c = forms.cube(center=False)
    assert len(c.vertices) == 8
    assert len(c.faces) == 6


class TestExtrude:
    @pytest.fixture
    def profile(self):
        return [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]

    def test_extrude_without_caps(self, profile):
        path = ((0, 0, 0), (0, 0, 1))
        diag = forms.extrude(profile, path, close=True, caps=False).diagnose()
        assert diag.n_vertices == 8
        assert diag.n_faces == 4
        assert diag.is_manifold is True

    def test_extrude_open_profiles_with_caps(self, profile):
        path = ((0, 0, 0), (0, 0, 1))
        diag = forms.extrude(profile, path, close=False, caps=True).diagnose()
        assert diag.n_vertices == 8
        assert diag.n_faces == 5, "hull should have top- and bottom faces"
        assert diag.is_manifold is True

    def test_extrude_with_caps(self, profile):
        path = ((0, 0, 0), (0, 0, 1))
        diag = forms.extrude(profile, path, close=True, caps=True).diagnose()
        assert len(diag.faces[0]) == 4, "bottom face should have 4 vertices"
        assert diag.n_vertices == 8
        assert diag.n_faces == 6
        assert diag.is_manifold is True
        assert len(diag.faces[-1]) == 4, "top face should have 4 vertices"


def test_from_profiles_linear():
    bottom = Vec3.list([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
    top = Vec3.list([(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)])
    mesh = forms.from_profiles_linear([bottom, top], close=True, caps=True)
    assert len(mesh.vertices) == 8
    assert len(mesh.faces) == 6

    mesh = forms.from_profiles_linear([bottom, top], close=True, caps=False)
    assert len(mesh.vertices) == 8
    assert len(mesh.faces) == 4


def in_vertices(v, vertices):
    v = Vec3(v)
    return any(v.isclose(v2) for v2 in vertices)


def test_cylinder():
    mesh = forms.cylinder(12)
    assert len(mesh.faces) == 14  # 1x bottom, 1x top, 12x side
    assert len(mesh.vertices) == 24  # 12x bottom, 12x top

    mesh = forms.cylinder(
        count=12, radius=3, top_radius=2, top_center=(1, 0, 3), caps=False
    )
    assert len(mesh.faces) == 12
    assert len(mesh.vertices) == 24
    assert in_vertices((3, 0, 3), mesh.vertices)
    assert in_vertices((-1, 0, 3), mesh.vertices)


def test_spline_interpolation():
    vertices = [(0.0, 0.0), (1.0, 2.0), (3.0, 1.0), (5.0, 3.0)]
    result = forms.spline_interpolation(vertices, method="uniform", subdivide=4)
    assert len(result) == 13  # (len-1) * subdivide + 1
    assert Vec3(0, 0, 0).isclose(result[0]), "expected start point"
    assert Vec3(5, 3, 0).isclose(result[-1]), "expected end point"
    assert Vec3(1, 2, 0).isclose(result[4]), "expected 2. fit point"
    assert Vec3(3, 1, 0).isclose(result[8]), "expected 3. fit point"


def test_spline_interpolated_profiles():
    p1 = forms.circle(12, radius=2, elevation=0, close=True)
    p2 = forms.circle(12, radius=3, elevation=2, close=True)
    p3 = forms.circle(12, radius=1, elevation=4, close=True)
    p4 = forms.circle(12, radius=2, elevation=6, close=True)
    profiles = list(
        forms.spline_interpolated_profiles(
            [Vec3.list(p) for p in [p1, p2, p3, p4]], subdivide=4
        )
    )
    assert len(profiles) == 13  # 3*4 + 1


def test_from_profiles_splines():
    p1 = list(forms.circle(12, radius=2, elevation=0, close=True))
    p2 = list(forms.circle(12, radius=3, elevation=2, close=True))
    p3 = list(forms.circle(12, radius=1, elevation=4, close=True))
    p4 = list(forms.circle(12, radius=2, elevation=6, close=True))
    mesh = forms.from_profiles_spline([p1, p2, p3, p4], subdivide=4, caps=True)
    assert len(mesh.vertices) == 156  # 12 (circle) * 13 (profiles)
    assert len(mesh.faces) == 146  # 12 (circle) * 12 + 2


def test_cone():
    mesh = forms.cone(12, 2, apex=(0, 0, 3))
    assert len(mesh.vertices) == 13
    assert len(mesh.faces) == 13


def test_rotation_form():
    profile = [(0, 0.1), (1, 1), (3, 1.5), (5, 3)]  # in xy-plane
    mesh = forms.rotation_form(
        count=16, profile=profile, axis=(1, 0, 0)
    )  # rotation axis is the x-axis
    assert len(mesh.vertices) == 16 * 4
    assert len(mesh.faces) == 16 * 3


def test_translate():
    p = [(1, 2, 3), (4, 5, 6)]
    r = list(forms.translate(p, (3, 2, 1)))
    assert r[0].isclose((4, 4, 4))
    assert r[1].isclose((7, 7, 7))


def test_scale():
    p = [(1, 2, 3), (4, 5, 6)]
    r = list(forms.scale(p, (3, 2, 1)))
    assert r[0].isclose((3, 4, 3))
    assert r[1].isclose((12, 10, 6))


def test_rotate():
    p = [(1, 0, 3), (0, 1, 6)]
    r = list(forms.rotate(p, 90, deg=True))
    assert r[0].isclose((0, 1, 3))
    assert r[1].isclose((-1, 0, 6))


def test_square_by_radius():
    corners = list(forms.ngon(4, radius=1))
    assert len(corners) == 4
    assert corners[0].isclose((1, 0, 0))
    assert corners[1].isclose((0, 1, 0))
    assert corners[2].isclose((-1, 0, 0))
    assert corners[3].isclose((0, -1, 0))


def test_heptagon_by_edge_length():
    corners = list(forms.ngon(7, length=10))
    assert len(corners) == 7
    assert corners[0].isclose((11.523824354812433, 0, 0))
    assert corners[1].isclose((7.184986963636852, 9.009688679024192, 0))
    assert corners[2].isclose((-2.564292158181384, 11.234898018587335, 0))
    assert corners[3].isclose((-10.382606982861683, 5, 0))
    assert corners[4].isclose((-10.382606982861683, -5, 0))
    assert corners[5].isclose((-2.564292158181387, -11.234898018587335, 0))
    assert corners[6].isclose((7.18498696363685, -9.009688679024192, 0))


class TestTorus:
    def test_closed_torus_ngon_faces(self):
        t = forms.torus(major_count=16, minor_count=8)
        diag = t.diagnose()
        assert diag.n_vertices == 16 * 8
        assert diag.n_faces == 16 * 8
        assert diag.is_manifold is True

    def test_open_torus_ngon_faces(self):
        t = forms.torus(major_count=16, minor_count=8, end_angle=math.pi)
        diag = t.diagnose()
        assert diag.n_vertices == 17 * 8
        assert diag.n_faces == 16 * 8 + 2
        assert diag.is_manifold is True

    @pytest.mark.parametrize("r", [2, 1, -2])
    def test_major_radius_is_bigger_than_minor_radius(self, r):
        with pytest.raises(ValueError):
            forms.torus(major_radius=1, minor_radius=r)

    def test_major_radius_is_bigger_than_zero(self):
        with pytest.raises(ValueError):
            forms.torus(major_radius=0)

    def test_minor_radius_is_bigger_than_zero(self):
        with pytest.raises(ValueError):
            forms.torus(minor_radius=0)


def test_intersection_profiles():
    p0 = Vec3.list([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
    p1 = Vec3.list([(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)])
    p2 = Vec3.list([(0, 0, 1), (0, 0, 2), (0, 1, 2), (0, 1, 1)])
    p3 = Vec3.list([(-1, 0, 1), (-1, 0, 2), (-1, 1, 2), (-1, 1, 1)])
    profiles = forms._intersection_profiles([p0, p2], [p1, p3])
    assert profiles[0] == p0
    assert (
        close_vectors(profiles[1], [(0, 0, 1), (1, 0, 2), (1, 1, 2), (0, 1, 1)])
        is True
    )
    assert profiles[2] == p3


class TestReferenceFrame:
    def test_ref_z_in_x_axis(self):
        ucs = forms.reference_frame_z(Vec3(1, 0, 0))
        assert ucs.uy.isclose((0, 1, 0))
        assert ucs.uz.isclose((1, 0, 0))
        assert ucs.ux.isclose((0, 0, -1))

    @pytest.mark.parametrize("n", [Vec3(0, 0, 1), Vec3(0, 0, -1)])
    def test_ref_z_in_z_axis_raise_exception(self, n):
        with pytest.raises(ZeroDivisionError):
            forms.reference_frame_z(n)

    def test_ref_ext_preserve_x(self):
        frame = UCS()
        ucs = forms.reference_frame_ext(frame)
        assert ucs.ux.isclose((1, 0, 0))
        assert ucs.uy.isclose((0, 1, 0))
        assert ucs.uz.isclose((0, 0, 1))

    def test_ref_ext_preserve_y(self):
        # x-axis of previous reference frame is parallel to the Z_AXIS
        frame = UCS(ux=(0, 0, 1), uy=(0, 1, 0))
        ucs = forms.reference_frame_ext(frame)
        assert ucs.ux.isclose((1, 0, 0))
        assert ucs.uy.isclose((0, 1, 0))
        assert ucs.uz.isclose((0, 0, 1))


class TestExtrude2:
    def test_divide_path_count(self):
        p = [Vec3(), Vec3(3, 0)]
        assert len(forms._divide_path_into_steps(p, max_step_size=3)) == 2
        assert len(forms._divide_path_into_steps(p, max_step_size=2)) == 3
        assert len(forms._divide_path_into_steps(p, max_step_size=1)) == 4
        assert len(forms._divide_path_into_steps(p, max_step_size=0.5)) == 7

    def test_divide_path_vertices(self):
        p = [Vec3(), Vec3(3, 0)]
        assert (
            close_vectors(
                forms._divide_path_into_steps(p, 1.0),
                Vec3.list([(0, 0), (1, 0), (2, 0), (3, 0)]),
            )
            is True
        )

        p = [Vec3(), Vec3(1, 0), Vec3(2, 0), Vec3(3, 0)]
        assert (
            close_vectors(
                forms._divide_path_into_steps(p, 1.0),
                Vec3.list([(0, 0), (1, 0), (2, 0), (3, 0)]),
            )
            is True
        )

    def test_divide_path_into_equally_spaced_segments(self):
        p = [Vec3(), Vec3(1.5, 0), Vec3(3, 0)]
        assert (
            close_vectors(
                forms._divide_path_into_steps(p, 1.0),
                Vec3.list([(0, 0), (0.75, 0), (1.5, 0), (2.25, 0), (3, 0)]),
            )
            is True
        )

    def test_divide_path_has_to_include_all_source_vertices(self):
        p = [Vec3(), Vec3(1, 0), Vec3(1.5, 0), Vec3(2, 0), Vec3(3, 0)]
        assert (
            close_vectors(
                forms._divide_path_into_steps(p, 1.0),
                Vec3.list([(0, 0), (1, 0), (1.5, 0), (2, 0), (3, 0)]),
            )
            is True
        )

    def test_partial_path_factors(self):
        p = forms._partial_path_factors(
            Vec3.list([(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)])
        )
        assert p == pytest.approx([0, 0.25, 0.5, 0.75, 1.0])

    def test_extrude_square_without_intermediate_profiles(self):
        profile = forms.square(center=True)
        path = [(0, 0), (10, 0)]
        mesh = forms.extrude_twist_scale(
            profile, path, close=True, step_size=0.0
        )
        assert len(mesh.vertices) == 8

    def test_extrude_square_with_intermediate_profiles(self):
        profile = forms.square(center=True)
        path = [(0, 0), (0, 0, 10)]
        mesh = forms.extrude_twist_scale(
            profile, path, close=True, step_size=1.0
        )
        assert len(mesh.vertices) == 11 * 4
        assert len(mesh.faces) == 10 * 4

    def test_extrude_with_twist(self):
        mesh = forms.extrude_twist_scale(
            profile=forms.square(center=True),
            path=[(0, 0), (0, 0, 10)],
            close=True,
            step_size=1.0,
            twist=math.pi / 2,
        )
        assert close_vectors(
            mesh.vertices[-4:],
            [
                Vec3(0.5, 0.5, 10.0),
                Vec3(0.5, -0.5, 10.0),
                Vec3(-0.5, 0.5, 10.0),
                Vec3(-0.5, -0.5, 10.0),
            ],
        )

    def test_extrude_with_scale(self):
        mesh = forms.extrude_twist_scale(
            profile=forms.square(center=True),
            path=[(0, 0), (0, 0, 10)],
            close=True,
            step_size=1.0,
            scale=2.0,
        )
        assert close_vectors(
            mesh.vertices[-4:],
            [
                Vec3(1.0, -1.0, 10.0),
                Vec3(-1.0, -1.0, 10.0),
                Vec3(1.0, 1.0, 10.0),
                Vec3(-1.0, 1.0, 10.0),
            ],
        )
