# Purpose: test Ray2D
# Created: 28.02.2010
# License: MIT License
import unittest
import math
from ezdxf.algebra.ray import Ray2D, ParallelRaysError

HALF_PI = math.pi / 2.


class Test_Ray2D(unittest.TestCase):
    def test_init_with_slope(self):
        ray1 = Ray2D((10, 10), slope=1)
        ray2 = Ray2D((-3, -3), slope=-1)
        self.assertAlmostEqual(ray1.get_y(15), 15, 3)
        self.assertAlmostEqual(ray2.get_y(-2), -4, 3)

    def test_init_with_angle(self):
        point = (10, 10)
        ray = Ray2D(point, angle=0)
        ray_normal = ray.normal_through(point)
        self.assertTrue(ray_normal.is_vertical)
        ray = Ray2D(point, angle=-HALF_PI)
        self.assertFalse(ray.is_horizontal)
        self.assertTrue(ray.is_vertical)

    def test_Ray2D_get_x_y(self):
        ray1 = Ray2D((10, 1), (20, 10))
        y = ray1.get_y(15)
        self.assertAlmostEqual(y, 5.5, 3)
        x = ray1.get_x(y)
        self.assertAlmostEqual(x, 15., 3)

    def test_ray2d_intersect(self):
        ray1 = Ray2D((10, 1), (20, 10))
        ray2 = Ray2D((17, -7), (-10, 3))
        point = ray1.intersect(ray2)
        self.assertAlmostEqual(point[0], 5.7434, 3)
        self.assertAlmostEqual(point[1], -2.8309, 3)
        self.assertFalse(ray1.is_parallel(ray2))

    def test_ray2d_parallel(self):
        ray1 = Ray2D((17, -8), (-10, 2))
        ray2 = Ray2D((-10, 3), (17, -7))
        ray3 = Ray2D((-10, 4), (17, -6))
        self.assertTrue(ray2.is_parallel(ray3))
        self.assertTrue(ray1.is_parallel(ray3))
        self.assertRaises(ParallelRaysError, ray2.intersect, ray3)

    def test_ray2d_intersect_with_vertical(self):
        ray1 = Ray2D((10, 1), (10, -7))
        ray2 = Ray2D((-10, 3), (17, -7))
        point = ray1.intersect(ray2)
        self.assertAlmostEqual(point[0], 10., 3)
        self.assertAlmostEqual(point[1], -4.4074, 3)
        self.assertRaises(ArithmeticError, ray1.get_y, 1.)
        # vertical rays can't calc a y-value

    def test_ray2d_parallel_vertical(self):
        ray1 = Ray2D((10, 1), (10, -7))
        ray2 = Ray2D((11, 0), angle=HALF_PI)
        ray3 = Ray2D((12, -10), (12, 7))
        ray4 = Ray2D((0, 0), slope=1.0)
        ray5 = Ray2D((0, 0), slope=0)
        self.assertRaises(ParallelRaysError, ray1.intersect, ray3)
        self.assertTrue(ray1.is_parallel(ray3))
        self.assertTrue(ray1.is_parallel(ray2))
        self.assertTrue(ray2.is_parallel(ray2))
        self.assertFalse(ray1.is_parallel(ray4))
        self.assertFalse(ray2.is_parallel(ray4))
        self.assertFalse(ray3.is_parallel(ray4))
        self.assertFalse(ray1.is_parallel(ray5))
        self.assertFalse(ray2.is_parallel(ray5))
        self.assertFalse(ray3.is_parallel(ray5))
        # vertical rays can't calc a y-value
        self.assertRaises(ArithmeticError, ray1.get_y, -1.)

    def test_ray2d_normal_vertical(self):
        ray = Ray2D((10, 1), (10, -7))  # vertical line
        norm = ray.normal_through((3, 3))
        point = ray.intersect(norm)
        self.assertAlmostEqual(point[0], 10.0, 3)
        self.assertAlmostEqual(point[1], 3.0, 3)

    def test_ray2d_normal(self):
        ray = Ray2D((-10, 3), (17, -7))
        norm = ray.normal_through((3, 3))
        point = ray.intersect(norm)
        self.assertAlmostEqual(point[0], 1.4318, 3)
        self.assertAlmostEqual(point[1], -1.234, 3)

    def test_ray2d_normal_horizontal(self):
        ray = Ray2D((10, 10), (20, 10))  # horizontal line
        norm = ray.normal_through((3, 3))
        point = ray.intersect(norm)
        self.assertAlmostEqual(point[0], 3.0, 3)
        self.assertAlmostEqual(point[1], 10.0, 3)

    def test_ray2d_angle(self):
        ray = Ray2D((10, 10), angle=HALF_PI)
        self.assertTrue(ray.is_vertical)
        ray = Ray2D((10, 10), angle=0)
        self.assertTrue(ray.is_horizontal)
        ray = Ray2D((10, 10), angle=math.pi / 4)
        self.assertAlmostEqual(ray.slope, 1., 6)

    def test_bisectrix(self):
        ray1 = Ray2D((10, 10), angle=math.pi / 3)
        ray2 = Ray2D((3, -5), angle=math.pi / 2)
        ray3 = Ray2D((1, 1), angle=math.pi / 3)
        a = ray1.bisectrix(ray2)
        self.assertAlmostEqual(a.angle, 1.309, 4)
        self.assertAlmostEqual(a.get_y(7), 12.80385, 4)
        self.assertRaises(ParallelRaysError, ray1.bisectrix, ray3)


if __name__ == '__main__':
    unittest.main()
