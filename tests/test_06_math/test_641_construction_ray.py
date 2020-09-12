# Purpose: test ConstructionRay
# Created: 28.02.2010
# License: MIT License
import pytest
import math
from ezdxf.math.line import ConstructionRay, ParallelRaysError
from ezdxf.math import Vector

HALF_PI = math.pi / 2.


class TestConstructionRay:
    def test_init_with_angle(self):
        point = (10, 10)
        ray = ConstructionRay(point, angle=0)
        ray_normal = ray.orthogonal(point)
        assert ray_normal._is_vertical is True
        ray = ConstructionRay(point, angle=-HALF_PI)
        assert ray._is_horizontal is False
        assert ray._is_vertical is True

    def test_Ray2D_get_x_y(self):
        ray1 = ConstructionRay((10, 1), (20, 10))
        y = ray1.yof(15)
        assert math.isclose(y, 5.5)
        assert math.isclose(ray1.xof(y), 15.)

    def test_ray2d_intersect(self):
        ray1 = ConstructionRay((10, 1), (20, 10))
        ray2 = ConstructionRay((17, -7), (-10, 3))

        point = ray1.intersect(ray2)
        assert point.isclose(Vector(5.7434, -2.8309), abs_tol=1e-4)
        assert ray1.is_parallel(ray2) is False

    def test_ray2d_parallel(self):
        ray1 = ConstructionRay((17, -8), (-10, 2))
        ray2 = ConstructionRay((-10, 3), (17, -7))
        ray3 = ConstructionRay((-10, 4), (17, -6))
        assert ray2.is_parallel(ray3) is True
        assert ray1.is_parallel(ray3) is True
        with pytest.raises(ParallelRaysError):
            _ = ray2.intersect(ray3)

    def test_ray2d_intersect_with_vertical(self):
        ray1 = ConstructionRay((10, 1), (10, -7))
        ray2 = ConstructionRay((-10, 3), (17, -7))
        point = ray1.intersect(ray2)
        assert point.x == 10
        assert point.isclose(Vector(10., -4.4074), abs_tol=1e-4)
        with pytest.raises(ArithmeticError):
            _ = ray1.yof(1)

    def test_ray2d_intersect_with_horizontal(self):
        ray1 = ConstructionRay((-10, 10), (10, 10))
        ray2 = ConstructionRay((-10, 20), (10, 0))
        point = ray1.intersect(ray2)
        assert point.y == 10
        assert point.isclose(Vector(0.0, 10.0), abs_tol=1e-4)

    def test_ray2d_intersect_with_vertical_and_horizontal(self):
        ray1 = ConstructionRay((-10, 10), (10, 10))
        ray2 = ConstructionRay((5, 0), (5, 20))
        point = ray1.intersect(ray2)
        assert point.y == 10
        assert point.x == 5
        assert point.isclose(Vector(5.0, 10.0), abs_tol=1e-4)

    def test_ray2d_parallel_vertical(self):
        ray1 = ConstructionRay((10, 1), (10, -7))
        ray2 = ConstructionRay((11, 0), angle=HALF_PI)
        ray3 = ConstructionRay((12, -10), (12, 7))
        ray4 = ConstructionRay((0, 0), (1, 1))
        ray5 = ConstructionRay((0, 0), angle=0)
        with pytest.raises(ParallelRaysError):
            _ = ray1.intersect(ray3)
        assert ray1.is_parallel(ray3) is True
        assert ray1.is_parallel(ray2) is True
        assert ray2.is_parallel(ray2) is True
        assert ray1.is_parallel(ray4) is False
        assert ray2.is_parallel(ray4) is False
        assert ray3.is_parallel(ray4) is False
        assert ray1.is_parallel(ray5) is False
        assert ray2.is_parallel(ray5) is False
        assert ray3.is_parallel(ray5) is False
        # vertical rays can't calc a y-value
        with pytest.raises(ArithmeticError):
            _ = ray1.yof(-1.)

    def test_ray2d_normal_vertical(self):
        ray = ConstructionRay((10, 1), (10, -7))  # vertical line
        ortho = ray.orthogonal((3, 3))
        point = ray.intersect(ortho)
        assert point.isclose(Vector(10, 3))

    def test_ray2d_normal(self):
        ray = ConstructionRay((-10, 3), (17, -7))
        ortho = ray.orthogonal((3, 3))
        point = ray.intersect(ortho)
        assert point.isclose(Vector(1.4318, -1.234), abs_tol=1e-4)

    def test_ray2d_normal_horizontal(self):
        ray = ConstructionRay((10, 10), (20, 10))  # horizontal line
        ortho = ray.orthogonal((3, 3))
        point = ray.intersect(ortho)
        assert point.isclose(Vector(3, 10))

    def test_ray2d_angle(self):
        ray = ConstructionRay((10, 10), angle=HALF_PI)
        assert ray._is_vertical is True
        ray = ConstructionRay((10, 10), angle=0)
        assert ray._is_horizontal is True
        ray = ConstructionRay((10, 10), angle=math.pi / 4)
        assert math.isclose(ray._slope, 1.)

    def test_bisectrix(self):
        ray1 = ConstructionRay((10, 10), angle=math.pi / 3)
        ray2 = ConstructionRay((3, -5), angle=math.pi / 2)
        ray3 = ConstructionRay((1, 1), angle=math.pi / 3)
        a = ray1.bisectrix(ray2)
        assert math.isclose(a._angle, 1.309, abs_tol=1e-4)
        assert math.isclose(a.yof(7), 12.80385, abs_tol=1e-4)
        with pytest.raises(ParallelRaysError):
            _ = ray1.bisectrix(ray3)

    def test_two_close_horizontal_rays(self):
        p1 = (39340.75302672016, 32489.73349764998)
        p2 = (39037.75302672119, 32489.73349764978)
        p3 = (38490.75302672015, 32489.73349764997)

        ray1 = ConstructionRay(p1, p2)
        ray2 = ConstructionRay(p2, p3)
        assert ray1.is_horizontal is True
        assert ray2.is_horizontal is True
        assert ray1.is_parallel(ray2) is True
        assert math.isclose(ray1.slope, ray2.slope) is False, 'Only slope testing is not sufficient'
