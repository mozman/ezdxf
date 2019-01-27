# (c) 2009, Manfred Moitzi
# License: MIT License
import unittest
import math
from ezdxf.algebra.base import equals_almost
from ezdxf.algebra.ray import ConstructionRay
from ezdxf.algebra.circle import ConstructionCircle

HALF_PI = math.pi / 2.


class TestConstructionCircle(unittest.TestCase):
    def test_init_circle(self):
        circle = ConstructionCircle((0., 0.), 5)
        point = circle.get_point(HALF_PI)
        self.assertAlmostEqual(point[0], 0., 3)
        self.assertAlmostEqual(point[1], 5., 3)
        point = circle.get_point(HALF_PI / 2)
        self.assertAlmostEqual(point[0], 3.5355, 3)
        self.assertAlmostEqual(point[1], 3.5355, 3)

    def test_within(self):
        circle = ConstructionCircle((0., 0.), 5)
        p1 = (3., 2.)
        p2 = (4., 5.)
        self.assertTrue(circle.within(p1))
        self.assertFalse(circle.within(p2))

    def test_tangent(self):
        circle = ConstructionCircle((0., 0.), 5.)
        tangent = circle.tangent(HALF_PI / 2)
        self.assertAlmostEqual(tangent.slope, -1, 4)
        tangent = circle.tangent(-HALF_PI / 2)
        self.assertAlmostEqual(tangent.slope, 1, 4)
        tangent = circle.tangent(0)
        self.assertTrue(tangent.is_vertical)
        tangent = circle.tangent(HALF_PI)
        self.assertTrue(tangent.is_horizontal)

    def test_intersect_ray_pass(self):
        circle = ConstructionCircle((10., 10.), 3)
        ray1_hor = ConstructionRay((10., 15.), angle=0)
        ray2_hor = ConstructionRay((10., 5.), angle=0)
        ray1_vert = ConstructionRay((5., 10.), angle=HALF_PI)
        ray2_vert = ConstructionRay((15., 10.), angle=-HALF_PI)
        ray3 = ConstructionRay((13.24, 14.95), angle=0.3992)
        self.assertFalse(circle.intersect_ray(ray1_hor))
        self.assertFalse(circle.intersect_ray(ray2_hor))
        self.assertFalse(circle.intersect_ray(ray1_vert))
        self.assertFalse(circle.intersect_ray(ray2_vert))
        self.assertFalse(circle.intersect_ray(ray3))

    def test_intersect_ray_touch(self):
        def test_touch(testnum, x, y, _angle, places=7):
            result = True
            ray = ConstructionRay((x, y), angle=_angle)
            points = circle.intersect_ray(ray, places)
            if len(points) != 1:
                result = False
            else:
                point = points[0]
                # print ("{0}: x= {1:.{places}f} y= {2:.{places}f} : x'= {3:.{places}f} y' = {4:.{places}f}".format(testnum, x, y, point[0], point[1], places=places))
                if not equals_almost(point[0], x, 4): result = False
                if not equals_almost(point[1], y, 4): result = False
            return result

        circle = ConstructionCircle((10., 10.), 3)
        self.assertTrue(test_touch(1, 10., 13., 0))
        self.assertTrue(test_touch(2, 10., 7., 0))
        self.assertTrue(test_touch(3, 7., 10., HALF_PI))
        self.assertTrue(test_touch(4, 13., 10., -HALF_PI))
        self.assertTrue(test_touch(5, 8.8341, 12.7642, 0.3991568, places=4))

    def test_intersect_ray_intersect(self):
        circle = ConstructionCircle((10., 10.), 3)
        ray_vert = ConstructionRay((8.5, 10.), angle=HALF_PI)
        cross_points = circle.intersect_ray(ray_vert)
        self.assertEqual(len(cross_points), 2)
        p1, p2 = cross_points
        if p1[1] > p2[1]: p1, p2 = p2, p1
        self.assertTrue(equal_points_almost(p1, (8.5, 7.4019), places=4))
        self.assertTrue(equal_points_almost(p2, (8.5, 12.5981), places=4))

        ray_hor = ConstructionRay((10, 8.5), angle=0.)
        cross_points = circle.intersect_ray(ray_hor)
        self.assertEqual(len(cross_points), 2)
        p1, p2 = cross_points
        if p1[0] > p2[0]: p1, p2 = p2, p1
        self.assertTrue(equal_points_almost(p1, (7.4019, 8.5), places=4))
        self.assertTrue(equal_points_almost(p2, (12.5981, 8.5), places=4))

        ray_slope = ConstructionRay((5, 5), (16, 12))
        cross_points = circle.intersect_ray(ray_slope)
        self.assertEqual(len(cross_points), 2)
        p1, p2 = cross_points
        if p1[0] > p2[0]: p1, p2 = p2, p1
        self.assertTrue(equal_points_almost(p1, (8.64840, 7.3217), places=4))
        self.assertTrue(equal_points_almost(p2, (12.9986, 10.0900), places=4))

        # ray with slope through midpoint
        ray_slope = ConstructionRay((10, 10), angle=HALF_PI / 2)
        cross_points = circle.intersect_ray(ray_slope)
        self.assertEqual(len(cross_points), 2)
        p1, p2 = cross_points
        if p1[0] > p2[0]: p1, p2 = p2, p1
        # print (p1[0], p1[1], p2[0], p2[1])
        self.assertTrue(equal_points_almost(p1, (7.8787, 7.8787), places=4))
        self.assertTrue(equal_points_almost(p2, (12.1213, 12.1213), places=4))

        # horizontal ray through midpoint
        ray_hor = ConstructionRay((10, 10), angle=0)
        cross_points = circle.intersect_ray(ray_hor)
        self.assertEqual(len(cross_points), 2)
        p1, p2 = cross_points
        if p1[0] > p2[0]: p1, p2 = p2, p1
        # print (p1[0], p1[1], p2[0], p2[1])
        self.assertTrue(equal_points_almost(p1, (7, 10), places=4))
        self.assertTrue(equal_points_almost(p2, (13, 10), places=4))

        # vertical ray through midpoint
        ray_vert = ConstructionRay((10, 10), angle=HALF_PI)
        cross_points = circle.intersect_ray(ray_vert)
        self.assertEqual(len(cross_points), 2)
        p1, p2 = cross_points
        if p1[1] > p2[1]: p1, p2 = p2, p1
        # print (p1[0], p1[1], p2[0], p2[1])
        self.assertTrue(equal_points_almost(p1, (10, 7), places=4))
        self.assertTrue(equal_points_almost(p2, (10, 13), places=4))

    def test_intersect_circle_pass(self):
        M1 = (30, 30)
        M2 = (40, 40)
        M3 = (30.3, 30.3)
        circle1 = ConstructionCircle(M1, 5)
        circle2 = ConstructionCircle(M1, 3)
        circle3 = ConstructionCircle(M2, 3)
        circle4 = ConstructionCircle(M3, 3)

        cross_points = circle1.intersect_circle(circle2)
        self.assertFalse(cross_points)
        cross_points = circle2.intersect_circle(circle3)
        self.assertFalse(cross_points)
        cross_points = circle1.intersect_circle(circle4)
        self.assertFalse(cross_points)

    def test_intersect_circle_touch(self):
        def check_touch(m, t):
            circle2 = ConstructionCircle(m, 1.5)
            points = circle1.intersect_circle(circle2, 4)
            self.assertEqual(len(points), 1)
            return equal_points_almost(points[0], t, 4)

        circle1 = ConstructionCircle((20, 20), 5)

        self.assertTrue(check_touch((26.5, 20.), (25., 20.)))
        self.assertTrue(check_touch((20., 26.5), (20., 25.)))
        self.assertTrue(check_touch((13.5, 20.), (15., 20.)))
        self.assertTrue(check_touch((20., 13.5), (20., 15.)))
        self.assertTrue(check_touch((14.9339, 15.9276), (16.1030, 16.8674)))

        self.assertTrue(check_touch((23.5, 20.), (25., 20.)))
        self.assertTrue(check_touch((20., 23.5), (20., 25.)))
        self.assertTrue(check_touch((16.5, 20.), (15., 20.)))
        self.assertTrue(check_touch((20., 16.5), (20., 15.)))
        self.assertTrue(check_touch((17.2721, 17.8071), (16.1030, 16.8673)))

    def test_intersect_circle_intersect(self):
        def check_intersection(m, p1, p2):
            circle2 = ConstructionCircle(m, 1.5)
            points = circle1.intersect_circle(circle2, 4)
            self.assertEqual(len(points), 2)
            a, b = points

            result1 = equal_points_almost(a, p1, 4) and equal_points_almost(b, p2, 4)
            result2 = equal_points_almost(a, p2, 4) and equal_points_almost(b, p1, 4)
            return result1 or result2

        circle1 = ConstructionCircle((40, 20), 5)
        self.assertTrue(check_intersection((46., 20.), (44.8958, 21.0153), (44.8958, 18.9847)))
        self.assertTrue(check_intersection((44., 20.), (44.8438, 21.2402), (44.8438, 18.7598)))
        self.assertTrue(check_intersection((40., 26.), (38.9847, 24.8958), (41.0153, 24.8958)))
        self.assertTrue(check_intersection((40., 24.), (38.7598, 24.8438), (41.2402, 24.8438)))
        self.assertTrue(check_intersection((34., 20.), (35.1042, 18.9847), (35.1042, 21.0153)))
        # self.assertTrue(check_intersection( (36.,20.),  (35.1563, 18.7598),  (35.1563, 21.2402)))
        self.assertTrue(check_intersection((40., 14.), (38.9847, 15.1042), (41.0153, 15.1042)))
        self.assertTrue(check_intersection((40., 14.), (38.9847, 15.1042), (41.0153, 15.1042)))
        self.assertTrue(check_intersection((36.8824, 17.4939), (35.4478, 17.9319), (37.0018, 15.9987)))
        self.assertTrue(check_intersection((35.3236, 16.2408), (35.5481, 17.7239), (36.8203, 16.1413)))

    def test_create_3P(self):
        p1 = (3., 3.)
        p2 = (5., 7.)
        p3 = (12., 5.)
        circle = ConstructionCircle.from_3p(p1, p2, p3)
        self.assertAlmostEqual(circle.center[0], 7.6875, 4)
        self.assertAlmostEqual(circle.center[1], 3.15625, 4)
        self.assertAlmostEqual(circle.radius, 4.6901, 4)

    def test_get_y(self):
        def check(x, y1, y2):
            result = circle.get_y(x)
            self.assertTrue(result)
            # order of results unknown
            v1 = equals_almost(result[0], y1, 4) and equals_almost(result[1], y2, 4)
            v2 = equals_almost(result[0], y2, 4) and equals_almost(result[1], y1, 4)
            return v1 or v2

        circle = ConstructionCircle((20., -20.), 5)
        self.assertFalse(circle.get_x(-14))
        self.assertTrue(check(15., -20., -20.))
        self.assertTrue(check(25., -20., -20.))
        self.assertTrue(check(20., -15., -25.))
        self.assertTrue(check(17.8504, -15.4857, -24.5143))
        self.assertTrue(check(22.2848, -15.5526, -24.4474))

    def test_get_x(self):
        def check(y, x1, x2):
            result = circle.get_x(y)
            self.assertTrue(result)
            # order of results unknown
            v1 = equals_almost(result[0], x1, 4) and equals_almost(result[1], x2, 4)
            v2 = equals_almost(result[0], x2, 4) and equals_almost(result[1], x1, 4)
            return v1 or v2

        circle = ConstructionCircle((20., -20.), 5.)
        self.assertEqual(len(circle.get_y(-14.)), 0)
        self.assertTrue(check(-15., 20., 20.))
        self.assertTrue(check(-25., 20., 20.))
        self.assertTrue(check(-20., 15., 25.))
        self.assertTrue(check(-17.7152, 15.5526, 24.4474))
        self.assertTrue(check(-22.1496, 15.4857, 24.5143))


def equal_points_almost(p1, p2, places=7):
    return equals_almost(p1[0], p2[0], places) and equals_almost(p1[1], p2[1], places)
