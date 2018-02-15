# Author:  mozman <me@mozman.at>
# Purpose: basic forms
# Created: 15.02.2018
# License: MIT License

from math import pi, sin, cos

from ezdxf.algebra.matrix44 import Matrix44
from ezdxf.algebra.vector import Vector
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
        yields Vector() objects

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

    Returns:
        MeshBuilder() object

    """
    mesh = MeshBuilder()
    vertices = _cube0_vertices if center else _cube_vertices
    vectices = vertices if matrix is None else matrix.transform_vectors(vertices)
    mesh.add_mesh(vertices=vectices, faces=cube_faces)
    return mesh


def cylinder(count, radius=1., height=1.):
    """
    Create a cylinder as MashBuilder() object.

    Args:
        count: edge count
        radius: cylinder radius
        height: cylinder height

    Returns:
        MeshBuilder() object

    """
    def add_circle_area(vertices, center):
        prev_vertex = None
        for vertex in vertices:
            if prev_vertex is not None:
                mesh.add_face([center, vertex, prev_vertex])
            prev_vertex = vertex

    def add_hull():
        prev_bottom = None
        prev_top = None
        for bottom, top in zip(base_circle, top_circle):
            if prev_bottom is not None:
                mesh.add_face([prev_bottom, bottom, top, prev_top])
            prev_bottom = bottom
            prev_top = top

    mesh = MeshVertexMerger()
    base_circle = list(circle(count, radius, close=True))
    top_circle = list(circle(count, radius, z=height, close=True))
    add_circle_area(base_circle, center=Vector(0, 0, 0))
    add_circle_area(top_circle, center=Vector(0, 0, height))
    add_hull()
    return MeshBuilder.from_mesh(mesh)


def cone(count, radius, height):
    pass


def rotation_form(count, polygon, angle=2*pi, axis=(0., 0., 1.)):
    pass


def translation_form(polygon, path):
    pass


def doughnut(mcount, ncount, outer_radius=1., ring_radius=.25):
    pass


def sphere(mcount, ncount, radius=1.):
    pass
