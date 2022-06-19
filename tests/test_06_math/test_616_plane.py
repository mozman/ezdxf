# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import (
    Plane,
    Vec3,
    X_AXIS,
    BoundingBox,
    Z_AXIS,
    split_polygon_by_plane,
)
from ezdxf.render import forms


def test_init():
    p = Plane(Vec3(1, 0, 0), 5)
    assert p.normal == (1, 0, 0)
    assert p.distance_from_origin == 5


def test_init_form_3_colinear_points():
    with pytest.raises(ValueError):
        Plane.from_3p(Vec3(1, 0, 0), Vec3(1, 0, 0), Vec3(1, 0, 0))


def test_init_form_3p():
    p = Plane.from_3p(Vec3(5, 0, 0), Vec3(5, 1, 5), Vec3(5, 0, 1))


def test_equal():
    p1 = Plane.from_vector((5, 0, 0))
    p2 = Plane.from_vector((5, 0, 0))
    assert p1 is not p2
    assert p1 == p1


def test_init_form_vector():
    p = Plane.from_vector((5, 0, 0))
    assert p.normal == (1, 0, 0)
    assert p.distance_from_origin == 5

    with pytest.raises(ValueError):
        Plane.from_vector((0, 0, 0))


def test_signed_distance_to():
    p = Plane.from_vector((5, 0, 0))
    assert p.signed_distance_to(Vec3(10, 0, 0)) == 5
    assert p.signed_distance_to(Vec3(0, 0, 0)) == -5


def test_distance_to():
    p = Plane.from_vector((5, 0, 0))
    assert p.distance_to(Vec3(10, 0, 0)) == 5
    assert p.distance_to(Vec3(0, 0, 0)) == 5


def test_is_coplanar():
    p = Plane.from_vector((5, 0, 0))
    assert p.is_coplanar_vertex(Vec3(5, 5, 0)) is True
    assert p.is_coplanar_vertex(Vec3(5, 0, 5)) is True


def test_is_coplanar_plane():
    p1 = Plane.from_vector((5, 0, 0))
    p2 = Plane.from_vector((-1, 0, 0))
    assert p1.is_coplanar_plane(p2) is True


class TestSplitConvexPolygon:
    def test_spit_horizontal_square(self):
        polygon = forms.square(center=True)
        plane = Plane(X_AXIS, 0)
        front, back = split_polygon_by_plane(polygon, plane)
        assert len(front) == 4
        assert len(back) == 4
        front_bbox = BoundingBox(front)
        assert front_bbox.extmin == (0, -0.5)
        assert front_bbox.extmax == (0.5, 0.5)
        back_bbox = BoundingBox(back)
        assert back_bbox.extmin == (-0.5, -0.5)
        assert back_bbox.extmax == (0, 0.5)

    def test_ignore_coplanar_square(self):
        polygon = forms.square(center=True)
        plane = Plane(Z_AXIS, 0)
        front, back = split_polygon_by_plane(polygon, plane, coplanar=False)
        assert len(front) == 0
        assert len(back) == 0

    def test_return_coplanar_square_front(self):
        polygon = forms.square(center=True)
        plane = Plane(Z_AXIS, 0)
        front, back = split_polygon_by_plane(polygon, plane, coplanar=True)
        assert len(front) == 4
        assert len(back) == 0

    def test_return_coplanar_square_back(self):
        polygon = forms.square(center=True)
        plane = Plane(-Z_AXIS, 0)
        front, back = split_polygon_by_plane(polygon, plane, coplanar=True)
        assert len(front) == 0
        assert len(back) == 4


class TestIntersectLine:
    @pytest.fixture(scope="class")
    def plane(self):
        return Plane(Z_AXIS, 5)

    def test_intersection_line(self, plane):
        ip = plane.intersect_line(Vec3(0, 0, 0), Vec3(0, 0, 10))
        assert ip.isclose((0, 0, 5))

    def test_line_above_plane(self, plane):
        ip = plane.intersect_line(Vec3(0, 0, 6), Vec3(0, 0, 10))
        assert ip is None

    def test_line_below_plane(self, plane):
        ip = plane.intersect_line(Vec3(0, 0, 0), Vec3(0, 0, 4))
        assert ip is None

    def test_colinear_start_point_intersection(self, plane):
        ip = plane.intersect_line(Vec3(0, 0, 5), Vec3(0, 0, 10))
        assert ip.isclose((0, 0, 5))

    def test_ignore_coplanar_start_point_intersection(self, plane):
        ip = plane.intersect_line(Vec3(0, 0, 5), Vec3(0, 0, 10), coplanar=False)
        assert ip is None

    def test_colinear_end_point_intersection(self, plane):
        ip = plane.intersect_line(Vec3(0, 0, 0), Vec3(0, 0, 5))
        assert ip.isclose((0, 0, 5))

    def test_ignore_coplanar_end_point_intersection(self, plane):
        ip = plane.intersect_line(Vec3(0, 0, 0), Vec3(0, 0, 5), coplanar=False)
        assert ip is None

    def test_coplanar_line_has_no_intersection(self, plane):
        ip = plane.intersect_line(Vec3(0, 0, 5), Vec3(1, 0, 5), coplanar=True)
        assert ip is None
        ip = plane.intersect_line(Vec3(0, 0, 5), Vec3(1, 0, 5), coplanar=False)
        assert ip is None


class TestIntersectRay:
    @pytest.fixture(scope="class")
    def plane(self):
        return Plane(Z_AXIS, 5)

    def test_intersection_line(self, plane):
        ip = plane.intersect_ray(Vec3(0, 0, 0), Vec3(0, 0, 10))
        assert ip.isclose((0, 0, 5))

    def test_coplanar_ray_has_no_intersection(self, plane):
        ip = plane.intersect_ray(Vec3(0, 0, 0), Vec3(1, 0, 0))
        assert ip is None

    def test_plane_parallel_to_yz(self):
        plane = Plane(Vec3(1, 0, 0), 3)
        ip = plane.intersect_ray(Vec3(0, 0, 2), Vec3(1, 0, 0))
        assert ip.isclose((3, 0, 2))


if __name__ == "__main__":
    pytest.main([__file__])
