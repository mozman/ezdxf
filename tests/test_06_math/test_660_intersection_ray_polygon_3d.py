#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import intersection_ray_polygon_3d, Vec3, Z_AXIS


@pytest.fixture(scope="module")
def polygon():
    return Vec3.list([(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)])


def test_polygon_with_invalid_normal():
    polygon = Vec3.list([(0, 0, 0), (1, 0, 0), (2, 0, 0)])
    ip = intersection_ray_polygon_3d(Vec3(0, 0, 0), Z_AXIS, polygon)
    assert ip is None


def test_intersection_point_inside(polygon):
    ip = intersection_ray_polygon_3d(Vec3(0, 0, 0), Z_AXIS, polygon)
    assert ip.isclose((0, 0, 1))


def test_intersection_point_at_boundary_line(polygon):
    ip = intersection_ray_polygon_3d(
        Vec3(1, 0, 0), Z_AXIS, polygon, boundary=True
    )
    assert ip.isclose((1, 0, 1))


def test_ignore_intersection_point_at_boundary_line(polygon):
    ip = intersection_ray_polygon_3d(
        Vec3(1, 0, 0), Z_AXIS, polygon, boundary=False
    )
    assert ip is None


def test_intersection_point_outside():
    polygon = Vec3.list([(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)])
    ip = intersection_ray_polygon_3d(Vec3(2, 0, 0), Z_AXIS, polygon)
    assert ip is None


def test_ignore_coplanar_ray(polygon):
    ip = intersection_ray_polygon_3d(Vec3(1, 0, 1), Vec3(1, 0, 0), polygon)
    assert ip is None


if __name__ == "__main__":
    pytest.main([__file__])
