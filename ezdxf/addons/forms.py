# Purpose: basic forms
# Created: 15.02.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from math import pi, sin, cos
from ezdxf.algebra.vector import Vector
from ezdxf.algebra.base import is_close_points
from .mesh import MeshBuilder, MeshVertexMerger


def circle(count, radius=1.0, z=0., close=False):
    """
    Create polygon vertices for a circle with *radius* and *count* corners at *z* height.

    Args:
        count: polygon corners
        radius: circle radius
        z: elevation
        close: yields first vertex also as last vertex if True.

    Returns:
        yields Vector() objects in count clockwise orientation

    """
    delta = 2. * pi / count
    alpha = 0.
    for index in range(count):
        x = cos(alpha)*radius
        y = sin(alpha)*radius
        yield Vector(x, y, z)
        alpha += delta

    if close:
        yield Vector(radius, 0, z)


def close_polygon(points):
    """
    Yields first point at the end to close polygon if necessary.

    """
    first_point = None
    last_point = None
    for point in points:
        if first_point is None:
            first_point = point
        yield point
        last_point = point

    if not is_close_points(first_point, last_point):
        yield first_point


# 8 corner vertices
_cube_vertices = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (1, 1, 1),
    (0, 1, 1),
]

# 8 corner vertices, 'mass' center in (0, 0, 0)
_cube0_vertices = [
    (-.5, -.5, -.5),
    (+.5, -.5, -.5),
    (+.5, +.5, -.5),
    (-.5, +.5, -.5),
    (-.5, -.5, +.5),
    (+.5, -.5, +.5),
    (+.5, +.5, +.5),
    (-.5, +.5, +.5),
]

# 6 cube faces
cube_faces = [
    [0, 3, 2, 1],
    [4, 5, 6, 7],
    [0, 1, 5, 4],
    [1, 2, 6, 5],
    [3, 7, 6, 2],
    [0, 4, 7, 3],
]


def cube(center=True, matrix=None):
    """
    Create a cube as MeshBuilder() object.

    Args:
        matrix: transformation matrix
        center: 'mass' center of cube in (0, 0, 0) if True, else first corner at (0, 0, 0)

    Returns: MeshBuilder()

    """
    mesh = MeshBuilder()
    vertices = _cube0_vertices if center else _cube_vertices
    vectices = vertices if matrix is None else matrix.transform_vectors(vertices)
    mesh.add_mesh(vertices=vectices, faces=cube_faces)
    return mesh


def extrude(profile, path, close=True):
    """
    Extrude a profile polygon along a path polyline, vertices of profile should be in counter clockwise order.

    Args:
        profile: sweeping profile as list of (x, y, z) tuples in counter clock wise order
        path:  extrusion path as list of (x, y, z) tuples
        close: close profile polygon if True

    Returns: MeshVertexMerger()

    """
    def add_hull(bottom_profile, top_profile):
        prev_bottom = bottom_profile[0]
        prev_top = top_profile[0]
        for bottom, top in zip(bottom_profile[1:], top_profile[1:]):
            face = (prev_bottom, bottom, top, prev_top)  # counter clock wise: normals outwards
            mesh.faces.append(face)
            prev_bottom = bottom
            prev_top = top

    mesh = MeshVertexMerger()
    if close:
        profile = close_polygon(profile)
    profile = [Vector(p) for p in profile]
    path = [Vector(p) for p in path]
    start_point = path[0]
    bottom_indices = mesh.add_vertices(profile)  # base profile
    for target_point in path[1:]:
        translation_vector = target_point - start_point
        # profile will just be translated
        profile = [vec + translation_vector for vec in profile]
        top_indices = mesh.add_vertices(profile)
        add_hull(bottom_indices, top_indices)
        bottom_indices = top_indices
        start_point = target_point
    return mesh


def cylinder(count, radius=1., height=1.):
    """
    Create a cylinder as MeshVertexMerger() object.

    Args:
        count: edge count
        radius: cylinder radius
        height: cylinder height

    Returns: MeshVertexMerger()

    """
    mesh = MeshVertexMerger()
    base_circle = list(circle(count, radius, close=True))
    top_circle = list(circle(count, radius, z=height, close=True))
    mesh.add_face(reversed(base_circle))  # clock wise: normals down
    mesh.add_face(top_circle)  # count clockwise: normals up
    hull = extrude(base_circle, [(0, 0, 0), (0, 0, height)])
    mesh.add_mesh(vertices=hull.vertices, faces=hull.faces)  # normal outwards
    return mesh


def from_profiles_linear(profiles, close=True):
    pass


def from_profiles_bezier(profiles, subdivide=4, close=True):
    if len(profiles) < 3:
        return from_profiles_linear(profiles, close=close)


def cone(count, radius, height):
    pass


def rotation_form(count, profile, angle=2*pi, axis=(0., 0., 1.)):
    pass


def doughnut(mcount, ncount, outer_radius=1., ring_radius=.25):
    pass


def sphere(mcount, ncount, radius=1.):
    pass
