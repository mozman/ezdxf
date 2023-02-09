#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import intersection_line_polygon_3d, Vec3


@pytest.fixture(scope="module")
def polygon():
    return Vec3.list([(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)])


def test_polygon_with_invalid_normal():
    polygon = Vec3.list([(0, 0, 0), (1, 0, 0), (2, 0, 0)])
    ip = intersection_line_polygon_3d(Vec3(0, 0, 0), Vec3(0, 0, 5), polygon)
    assert ip is None


def test_intersection_point_inside(polygon):
    ip = intersection_line_polygon_3d(Vec3(0, 0, 0), Vec3(0, 0, 5), polygon)
    assert ip.isclose((0, 0, 1))


def test_intersection_point_at_boundary_line(polygon):
    ip = intersection_line_polygon_3d(
        Vec3(1, 0, 0), Vec3(1, 0, 5), polygon, boundary=True
    )
    assert ip.isclose((1, 0, 1))


def test_ignore_intersection_point_at_boundary_line(polygon):
    ip = intersection_line_polygon_3d(
        Vec3(1, 0, 0), Vec3(1, 0, 5), polygon, boundary=False
    )
    assert ip is None


def test_ignore_coplanar_start_point_as_intersection_point(polygon):
    ip = intersection_line_polygon_3d(
        Vec3(0, 0, 1), Vec3(0, 0, 5), polygon, coplanar=False
    )
    assert ip is None


def test_ignore_coplanar_end_point_as_intersection_point(polygon):
    ip = intersection_line_polygon_3d(
        Vec3(0, 0, 0), Vec3(0, 0, 1), polygon, coplanar=False
    )
    assert ip is None


def test_intersection_point_outside():
    polygon = Vec3.list([(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)])
    ip = intersection_line_polygon_3d(Vec3(2, 0, 0), Vec3(2, 0, 5), polygon)
    assert ip is None


def test_ignore_coplanar_line(polygon):
    ip = intersection_line_polygon_3d(Vec3(1, 0, 1), Vec3(2, 0, 1), polygon)
    assert ip is None


if __name__ == "__main__":
    pytest.main([__file__])
