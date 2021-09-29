# License: MIT License
from ezdxf.addons.pycsg import CSG, Vec3, BSPNode, Polygon
from ezdxf.render.forms import cube, sphere, cone_2p, cylinder_2p


def test_cube_intersect():
    a = cube()
    b = cube().translate(0.5, 0.5)
    c = CSG(mesh=a) * CSG(mesh=b)


def test_cube_union():
    a = cube()
    b = cube().translate(0.5, 0.5)
    c = CSG(mesh=a) + CSG(mesh=b)


def test_cube_subtract():
    a = cube()
    b = cube().translate(0.5, 0.5)
    _ = CSG(a) - CSG(b)


def test_sphere_cylinder_intersect():
    a = sphere(count=8, stacks=4, radius=0.5).translate(0.5, 0.5, 0.5)
    b = cylinder_2p(
        count=16, base_center=(0, 0, 0), top_center=(1, 0, 0), radius=0.3
    )
    CSG(a) * CSG(b)


def test_sphere_cylinder_union():
    a = sphere(count=8, stacks=4, radius=0.5).translate(0.5, 0.5, 0.5)
    b = cylinder_2p(
        count=16, base_center=(0, 0, 0), top_center=(1, 0, 0), radius=0.3
    )
    CSG(a) + CSG(b)


def test_sphere_cylinder_subtract():
    a = sphere(count=8, stacks=4, radius=0.5).translate(0.5, 0.5, 0.5)
    b = cylinder_2p(
        count=16, base_center=(0, 0, 0), top_center=(1, 0, 0), radius=0.3
    )
    CSG(a) - CSG(b)


def test_bolt():
    shaft = cylinder_2p(
        count=32, base_center=(0, 0, 0), top_center=(1, 0, 0), radius=0.1
    )
    head = cone_2p(base_center=(-0.12, 0, 0), apex=(0.1, 0, 0), radius=0.25)
    notch1 = cube().translate(-0.1, 0, 0).scale(0.02, 0.20, 0.02)
    notch2 = cube().translate(-0.1, 0, 0).scale(0.02, 0.02, 0.20)
    bolt = CSG(shaft) + CSG(head) - CSG(notch1) - CSG(notch2)


def test_example_simple():
    v0 = Vec3(0.0, 0.0, 0.0)
    v1 = Vec3(1.0, 0.0, 0.0)
    v2 = Vec3(1.0, 1.0, 0.0)
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
    v0 = Vec3(0.12, -0.24, 1.50)
    v1 = Vec3(0.01, 0.00, 1.75)
    v2 = Vec3(-0.03, 0.05, 1.79)
    v3 = Vec3(-0.13, -0.08, 1.5)
    p0 = Polygon([v0, v1, v2, v3])
    polygons = [p0]
    node = BSPNode(polygons)
