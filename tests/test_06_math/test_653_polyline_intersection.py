#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import (
    intersect_polylines_2d,
    intersect_polylines_3d,
    Vec2,
    Vec3,
    ConstructionEllipse,
    BSpline,
)


class TestIntersectPolylines2d:
    def test_intersecting_one_liners(self):
        pline1 = Vec2.list([(0, 1), (2, 1)])
        pline2 = Vec2.list([(1, 0), (1, 2)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 1
        assert res[0].isclose(Vec2(1, 1))

    def test_none_intersecting_one_liners(self):
        pline1 = Vec2.list([(0, 0), (2, 0)])
        pline2 = Vec2.list([(0, 1), (2, 1)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 0

    def test_intersecting_cross(self):
        pline1 = Vec2.list([(0, 1), (1, 1), (2, 1)])
        pline2 = Vec2.list([(1, 0), (1, 1), (1, 2)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 1
        assert res[0].isclose(Vec2(1, 1))

    def test_intersecting_x_cross(self):
        pline1 = Vec2.list([(0, 0), (1, 1), (2, 2)])
        pline2 = Vec2.list([(2, 0), (1, 1), (0, 2)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 1
        assert res[0].isclose(Vec2(1, 1))

    def test_intersecting_zig_zag(self):
        pline1 = Vec2.list([(0, 0), (2, 2), (4, 0), (6, 2), (8, 0)])
        pline2 = Vec2.list([(0, 2), (2, 0), (4, 2), (6, 0), (8, 2)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 4
        res.sort()  # do not rely on any order
        assert res[0].isclose(Vec2(1, 1))
        assert res[1].isclose(Vec2(3, 1))
        assert res[2].isclose(Vec2(5, 1))
        assert res[3].isclose(Vec2(7, 1))

    def test_touching_zig_zag(self):
        pline1 = Vec2.list([(0, 0), (2, 2), (4, 0), (6, 2), (8, 0)])
        pline2 = Vec2.list([(0, 4), (2, 2), (4, 4), (6, 2), (8, 4)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 2
        res.sort()  # do not rely on any order
        assert res[0].isclose(Vec2(2, 2))
        assert res[1].isclose(Vec2(6, 2))

    def test_complex_ellipse_spline_intersection(self):
        ellipse = ConstructionEllipse(center=(0, 0), major_axis=(3, 0), ratio=0.5)
        bspline = BSpline([(-4, -4), (-2, -1), (2, 1), (4, 4)])
        p1 = ellipse.flattening(distance=0.01)
        p2 = bspline.flattening(distance=0.01)
        res = intersect_polylines_2d(Vec2.list(p1), Vec2.list(p2))
        assert len(res) == 2


class TestIntersectPolylines3d:
    """
    The 3D line intersection function is tested in test suite 614.

    The basic polyline intersection algorithm is tested in class TestIntersectPolylines2d.

    This class tests only if the function intersect_polylines_3d() is implemented.

    """
    def test_intersecting_one_liners(self):
        pline1 = Vec3.list([(0, 1), (2, 1)])
        pline2 = Vec3.list([(1, 0), (1, 2)])
        res = intersect_polylines_3d(pline1, pline2)
        assert len(res) == 1
        assert res[0].isclose(Vec3(1, 1))

    def test_none_intersecting_one_liners(self):
        pline1 = Vec3.list([(0, 0), (2, 0)])
        pline2 = Vec3.list([(0, 1), (2, 1)])
        res = intersect_polylines_3d(pline1, pline2)
        assert len(res) == 0


if __name__ == "__main__":
    pytest.main([__file__])
