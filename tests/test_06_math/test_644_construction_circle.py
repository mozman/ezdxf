# Copyright (c) 2009-2021, Manfred Moitzi
# License: MIT License
import math
from math import isclose

import pytest

from ezdxf.math import (
    ConstructionRay, ConstructionCircle, Vec2,
)

HALF_PI = math.pi / 2.


def test_init_circle():
    circle = ConstructionCircle((0., 0.), 5)
    point = circle.point_at(HALF_PI)
    assert isclose(point[0], 0., abs_tol=1e-4)
    assert isclose(point[1], 5., abs_tol=1e-4)
    point = circle.point_at(HALF_PI / 2)
    assert isclose(point[0], 3.5355, abs_tol=1e-4)
    assert isclose(point[1], 3.5355, abs_tol=1e-4)


def test_within():
    circle = ConstructionCircle((0., 0.), 5)
    p1 = (3., 2.)
    p2 = (4., 5.)
    assert circle.inside(p1) is True
    assert circle.inside(p2) is False


def test_tangent():
    circle = ConstructionCircle((0., 0.), 5.)
    tangent = circle.tangent(HALF_PI / 2)
    assert isclose(tangent._slope, -1, abs_tol=1e-4)
    tangent = circle.tangent(-HALF_PI / 2)
    assert isclose(tangent._slope, 1, abs_tol=1e-4)
    tangent = circle.tangent(0)
    assert tangent._is_vertical is True
    tangent = circle.tangent(HALF_PI)
    assert tangent._is_horizontal is True


def test_intersect_ray_pass():
    circle = ConstructionCircle((10., 10.), 3)
    ray1_hor = ConstructionRay((10., 15.), angle=0)
    ray2_hor = ConstructionRay((10., 5.), angle=0)
    ray1_vert = ConstructionRay((5., 10.), angle=HALF_PI)
    ray2_vert = ConstructionRay((15., 10.), angle=-HALF_PI)
    ray3 = ConstructionRay((13.24, 14.95), angle=0.3992)
    assert len(circle.intersect_ray(ray1_hor)) == 0
    assert len(circle.intersect_ray(ray2_hor)) == 0
    assert len(circle.intersect_ray(ray1_vert)) == 0
    assert len(circle.intersect_ray(ray2_vert)) == 0
    assert len(circle.intersect_ray(ray3)) == 0


def test_intersect_ray_touch():
    def test_touch(testnum, x, y, _angle, abs_tol=1e-6):
        result = True
        ray = ConstructionRay((x, y), angle=_angle)
        points = circle.intersect_ray(ray, abs_tol=abs_tol)
        if len(points) != 1:
            result = False
        else:
            point = points[0]
            # print ("{0}: x= {1:.{places}f} y= {2:.{places}f} : x'= {3:.{places}f} y' = {4:.{places}f}".format(testnum, x, y, point[0], point[1], places=places))
            if not isclose(point[0], x, abs_tol=abs_tol):
                result = False
            if not isclose(point[1], y, abs_tol=abs_tol):
                result = False
        return result

    circle = ConstructionCircle((10., 10.), 3)
    assert test_touch(1, 10., 13., 0) is True
    assert test_touch(2, 10., 7., 0) is True
    assert test_touch(3, 7., 10., HALF_PI) is True
    assert test_touch(4, 13., 10., -HALF_PI) is True
    assert test_touch(5, 8.8341, 12.7642, 0.3991568, abs_tol=1e-4) is True


class TestCircleInterectRay:
    @pytest.fixture
    def circle(self):
        return ConstructionCircle((10., 10.), 3)

    def test_vertical_ray(self, circle):
        ray_vert = ConstructionRay((8.5, 10.), angle=HALF_PI)
        cross_points = circle.intersect_ray(ray_vert)
        assert len(cross_points) == 2
        p1, p2 = cross_points
        if p1[1] > p2[1]: p1, p2 = p2, p1
        assert p1.isclose((8.5, 7.4019), abs_tol=1e-4)
        assert p2.isclose((8.5, 12.5981), abs_tol=1e-4)

    def test_horizontal_ray(self, circle):
        ray_hor = ConstructionRay((10, 8.5), angle=0.)
        cross_points = circle.intersect_ray(ray_hor)
        assert len(cross_points) == 2
        p1, p2 = cross_points
        if p1[0] > p2[0]: p1, p2 = p2, p1
        assert p1.isclose((7.4019, 8.5), abs_tol=1e-4)
        assert p2.isclose((12.5981, 8.5), abs_tol=1e-4)

    def test_diagonal_ray(self, circle):
        ray_slope = ConstructionRay((5, 5), (16, 12))
        cross_points = circle.intersect_ray(ray_slope)
        assert len(cross_points) == 2
        p1, p2 = cross_points
        if p1[0] > p2[0]: p1, p2 = p2, p1
        assert p1.isclose((8.64840, 7.3217), abs_tol=1e-4)
        assert p2.isclose((12.9986, 10.0900), abs_tol=1e-4)

    def test_diagonal_ray_through_mid_point(self, circle):
        ray_slope = ConstructionRay((10, 10), angle=HALF_PI / 2)
        cross_points = circle.intersect_ray(ray_slope)
        assert len(cross_points) == 2
        p1, p2 = cross_points
        if p1[0] > p2[0]: p1, p2 = p2, p1
        # print (p1[0], p1[1], p2[0], p2[1])
        assert p1.isclose((7.8787, 7.8787), abs_tol=1e-4)
        assert p2.isclose((12.1213, 12.1213), abs_tol=1e-4)

    def test_horizontal_ray_through_mid_point(self, circle):
        ray_hor = ConstructionRay((10, 10), angle=0)
        cross_points = circle.intersect_ray(ray_hor)
        assert len(cross_points) == 2
        p1, p2 = cross_points
        if p1[0] > p2[0]: p1, p2 = p2, p1
        # print (p1[0], p1[1], p2[0], p2[1])
        assert p1.isclose((7, 10), abs_tol=1e-5)
        assert p2.isclose((13, 10), abs_tol=1e-5)

    def test_vertical_ray_through_mid_point(self, circle):
        ray_vert = ConstructionRay((10, 10), angle=HALF_PI)
        cross_points = circle.intersect_ray(ray_vert)
        assert len(cross_points) == 2
        p1, p2 = cross_points
        if p1[1] > p2[1]: p1, p2 = p2, p1
        # print (p1[0], p1[1], p2[0], p2[1])
        assert p1.isclose((10, 7), abs_tol=1e-5)
        assert p2.isclose((10, 13), abs_tol=1e-5)


def test_cicles_do_not_intersect():
    M1 = (30, 30)
    M2 = (40, 40)
    M3 = (30.3, 30.3)
    circle1 = ConstructionCircle(M1, 5)
    circle2 = ConstructionCircle(M1, 3)
    circle3 = ConstructionCircle(M2, 3)
    circle4 = ConstructionCircle(M3, 3)

    cross_points = circle1.intersect_circle(circle2)
    assert len(cross_points) == 0
    cross_points = circle2.intersect_circle(circle3)
    assert len(cross_points) == 0
    cross_points = circle1.intersect_circle(circle4)
    assert len(cross_points) == 0


def test_intersect_circle_touch():
    def check_touch(m, t, abs_tol=1e-9):
        circle2 = ConstructionCircle(m, 1.5)
        points = circle1.intersect_circle(circle2, 4)
        assert len(points) == 1
        return points[0].isclose(t, abs_tol=abs_tol)

    circle1 = ConstructionCircle((20, 20), 5)

    assert check_touch((26.5, 20.), (25., 20.)) is True
    assert check_touch((20., 26.5), (20., 25.)) is True
    assert check_touch((13.5, 20.), (15., 20.)) is True
    assert check_touch((20., 13.5), (20., 15.)) is True
    assert check_touch((14.9339, 15.9276), (16.1030, 16.8674),
                       abs_tol=1e-4) is True

    assert check_touch((23.5, 20.), (25., 20.)) is True
    assert check_touch((20., 23.5), (20., 25.)) is True
    assert check_touch((16.5, 20.), (15., 20.)) is True
    assert check_touch((20., 16.5), (20., 15.)) is True
    assert check_touch((17.2721, 17.8071), (16.1030, 16.8673),
                       abs_tol=1e-4) is True


def test_intersect_circle_intersect():
    def check_intersection(m, p1, p2, abs_tol=1e-4):
        p1 = Vec2(p1)
        p2 = Vec2(p2)
        circle2 = ConstructionCircle(m, 1.5)
        points = circle1.intersect_circle(circle2, abs_tol=abs_tol)
        assert len(points) == 2
        a, b = points

        result1 = a.isclose(p1, abs_tol=abs_tol) and \
                  b.isclose(p2, abs_tol=abs_tol)
        result2 = a.isclose(p2, abs_tol=abs_tol) and \
                  b.isclose(p1, abs_tol=abs_tol)
        return result1 or result2

    circle1 = ConstructionCircle((40, 20), 5)
    assert check_intersection((46., 20.), (44.8958, 21.0153),
                              (44.8958, 18.9847)) is True
    assert check_intersection((44., 20.), (44.8438, 21.2402),
                              (44.8438, 18.7598)) is True
    assert check_intersection((40., 26.), (38.9847, 24.8958),
                              (41.0153, 24.8958)) is True
    assert check_intersection((40., 24.), (38.7598, 24.8438),
                              (41.2402, 24.8438)) is True
    assert check_intersection((34., 20.), (35.1042, 18.9847),
                              (35.1042, 21.0153)) is True
    # assert check_intersection( (36.,20.),  (35.1563, 18.7598),  (35.1563, 21.2402)))
    assert check_intersection((40., 14.), (38.9847, 15.1042),
                              (41.0153, 15.1042)) is True
    assert check_intersection((40., 14.), (38.9847, 15.1042),
                              (41.0153, 15.1042)) is True
    assert check_intersection((36.8824, 17.4939), (35.4478, 17.9319),
                              (37.0018, 15.9987)) is True
    assert check_intersection((35.3236, 16.2408), (35.5481, 17.7239),
                              (36.8203, 16.1413)) is True


def test_create_3P():
    p1 = (3., 3.)
    p2 = (5., 7.)
    p3 = (12., 5.)
    circle = ConstructionCircle.from_3p(p1, p2, p3)
    assert isclose(circle.center[0], 7.6875, abs_tol=1e-4)
    assert isclose(circle.center[1], 3.15625, abs_tol=1e-4)
    assert isclose(circle.radius, 4.6901, abs_tol=1e-4)
