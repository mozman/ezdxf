# License: MIT License

import pytest
from ezdxf.addons.pycsg import CSG, Vector, BSPNode, Polygon


def test_cone():
    CSG.cone(start=(0, 0, 0), end=(1, 2, 3), radius=1, slices=8)


def test_cylinder():
    CSG.cylinder(start=(0, 0, 0), end=(1, 2, 3), radius=1, slices=8)


def test_sphere():
    a = CSG.sphere(center=(0, 0, 0), radius=1., slices=4, stacks=3)
    a.refine()


def test_cube_intersect():
    a = CSG.cube()
    b = CSG.cube(center=(0.5, 0.5, 0))
    c = a * b


def test_cube_union():
    a = CSG.cube()
    b = CSG.cube(center=(0.5, 0.5, 0))
    c = a + b
    c.refine().refine()


# @pytest.mark.skip('Windows stack overflow!')
# def test_sphere_union():
#     a = CSG.sphere(center=(0., 0., 0.), radius=1.0, slices=64, stacks=32)
#     b = CSG.sphere(center=(1.99, 0., 0.), radius=1.0, slices=64, stacks=32)
#     _ = a + b


def test_cube_subtract():
    a = CSG.cube()
    b = CSG.cube(center=(0.5, 0.5, 0))
    _ = a - b


def test_sphere_cylinder_intersect():
    a = CSG.sphere(center=(0.5, 0.5, 0.5), radius=0.5, slices=8, stacks=4)
    b = CSG.cylinder(start=(0, 0, 0), end=(1, 0, 0), radius=0.3, slices=16)
    a.intersect(b)


def test_sphere_cylinder_union():
    a = CSG.sphere(center=(0.5, 0.5, 0.5), radius=0.5, slices=8, stacks=4)
    b = CSG.cylinder(start=(0, 0, 0), end=(1, 0, 0), radius=0.3, slices=16)
    a.union(b)


def test_sphere_cylinder_subtract():
    a = CSG.sphere(center=(0.5, 0.5, 0.5), radius=0.5, slices=8, stacks=4)
    b = CSG.cylinder(start=(0, 0, 0), end=(1, 0, 0), radius=0.3, slices=16)
    a.subtract(b)


def test_bolt():
    shaft = CSG.cylinder(start=(0, 0, 0), end=(1, 0, 0), radius=0.1, slices=32)
    head = CSG.cone(start=(-0.12, 0, 0), end=(0.1, 0, 0), radius=0.25)
    notch1 = CSG.cube(center=(-0.1, 0, 0), scale=(0.02, 0.20, 0.02))
    notch2 = CSG.cube(center=(-0.1, 0, 0), scale=(0.02, 0.02, 0.20))
    bolt = shaft + head - notch1 - notch2
    bolt.refine()


def test_refine_sphere():
    a = CSG.sphere(center=(0, 0, 0), radius=1., slices=4, stacks=3)
    _ = a.refine()


def test_refine_cube_union():
    a = CSG.cube()
    b = CSG.cube(center=(0.5, 0.5, 0))
    c = a + b
    _ = c.refine().refine()


def test_example_simple():
    v0 = Vector(0., 0., 0.)
    v1 = Vector(1., 0., 0.)
    v2 = Vector(1., 1., 0.)
    p0 = Polygon([v0, v1, v2])
    polygons = [p0]
    node = BSPNode(polygons)


def test_example_infiniteRecursion():
    # This polygon is not exactly planar, causing
    # an infinite recursion when building the BSP
    # tree. Because of the last node, polygon is
    # put at the back of the list with respect to
    # its own cutting plane -- it should be classified
    # as co-planar
    v0 = Vector(0.12, -0.24, 1.50)
    v1 = Vector(0.01, 0.00, 1.75)
    v2 = Vector(-0.03, 0.05, 1.79)
    v3 = Vector(-0.13, -0.08, 1.5)
    p0 = Polygon([v0, v1, v2, v3])
    polygons = [p0]
    node = BSPNode(polygons)
