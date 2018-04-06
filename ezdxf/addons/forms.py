# Purpose: basic forms
# Created: 15.02.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from math import pi, sin, cos
from ezdxf.algebra import Vector, Matrix44
from ezdxf.algebra.base import is_close_points, is_close
from ezdxf.algebra.bspline import bspline_control_frame
from ezdxf.algebra.eulerspiral import EulerSpiral
from .mesh import MeshBuilder, MeshVertexMerger


def circle(count, radius=1, elevation=0, close=False):
    """
    Create polygon vertices for a circle with *radius* and *count* corners,
    *elevation* is the z-axis for all vertices.

    Args:
        count: count of polygon vertices
        radius: circle radius
        elevation: z axis for all vertices
        close: yields first vertex also as last vertex if True.

    Returns: yields Vector() objects in counter clockwise orientation

    """
    radius = float(radius)
    delta = 2. * pi / count
    alpha = 0.
    for index in range(count):
        x = cos(alpha)*radius
        y = sin(alpha)*radius
        yield Vector(x, y, elevation)
        alpha += delta

    if close:
        yield Vector(radius, 0, elevation)


def ellipse(count, rx=1, ry=1, start_param=0, end_param=2*pi, elevation=0):
    """
    Create polygon vertices for an ellipse with *rx* as x-axis radius and *ry*
    for y-axis radius with *count* vertices, *elevation* is the z-axis for all
    vertices. The ellipse goes from *start_param* to *end_param* in counter
    clockwise orientation.

    Args:
        count: count of polygon vertices
        rx: ellipse x-axis radius
        ry: ellipse y-axis radius
        start_param: start of ellipse in range 0 .. 2*pi
        end_param: end of ellipse in range 0 .. 2*pi
        elevation: z-axis for all vertices

    Returns: yields Vector() objects

    """
    rx = float(rx)
    ry = float(ry)
    start_param = float(start_param)
    end_param = float(end_param)
    count = int(count)
    delta = (end_param - start_param) / (count-1)
    for param in range(count):
        alpha = start_param + param*delta
        yield Vector(cos(alpha) * rx, sin(alpha) * ry, elevation)


def euler_spiral(count, length=1, curvature=1, elevation=0):
    """
    Create polygon vertices for an euler spiral of a given length and
    radius of curvature. This is a parametric curve, which always starts
    at the origin.

    Args:
        count: count of polygon vertices
        length: length of curve in drawing units
        curvature: radius of curvature
        elevation: z-axis for all vertices

    Returns: yields Vector() objects

    """
    spiral = EulerSpiral(curvature=curvature)
    for vertex in spiral.approximate(length, count-1):
        yield vertex.replace(z=elevation)


def translate(vertices, vec=(0, 0, 1)):
    """
    Simple translation, faster than a Matrix44 transformation.

    Args:
        vertices: list of vertices
        vec: translation vector

    Returns: yields transformed vertices

    """
    vec = Vector(vec)
    for p in vertices:
        yield vec + p


def close_polygon(vertices):
    """
    Returns list of vertices, where vertices[0] == vertices[-1].

    """
    vertices = list(vertices)
    if not is_close_points(vertices[0], vertices[-1]):
        vertices.append(vertices[0])
    return vertices


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
    Extrude a profile polygon along a path polyline, vertices of profile should be in
    counter clockwise order.

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


def cylinder(count, radius=1., top_radius=None, top_center=(0, 0, 1), caps=True):
    """
    Create a cylinder as MeshVertexMerger() object.

    Args:
        count: profiles edge count
        radius: radius for bottom profile
        top_radius: radius for top profile, if None top_radius == radius
        top_center: location vector for the center of the top profile
        caps: close hull with bottom cap and top cap (as N-gons)

    Returns: MeshVertexMerger()

    """
    if top_radius is None:
        top_radius = radius

    if is_close(top_radius, 0.):  # pyramid/cone
        return cone(count=count, radius=radius, apex=top_center)

    base_profile = list(circle(count, radius, close=True))
    top_profile = list(translate(circle(count, top_radius, close=True), top_center))
    return from_profiles_linear([base_profile, top_profile], caps=caps)


def from_profiles_linear(profiles, close=True, caps=False):
    """
    Mesh by linear connected profiles.

    Args:
        profiles: list of profiles
        close: close profile polygon if True
        caps: close hull with bottom cap and top cap (as N-gons)

    Returns: MeshVertexMerger()

    """
    mesh = MeshVertexMerger()
    profiles = list(profiles)  # generator -> list
    if close:
        profiles = [close_polygon(p) for p in profiles]
    if caps:
        mesh.add_face(profiles[0])
        mesh.add_face(profiles[-1])

    for profile1, profile2 in zip(profiles, profiles[1:]):
        prev_v1, prev_v2 = None, None
        for v1, v2 in zip(profile1, profile2):
            if prev_v1 is not None:
                mesh.add_face([prev_v1, v1, v2, prev_v2])
            prev_v1 = v1
            prev_v2 = v2

    return mesh


def spline_interpolation(vertices, degree=3, method='uniform', power=.5, subdivide=4):
    """
    B-spline interpolation, vertices are fit points for the spline definition.

    Only method 'uniform', yields vertices at fit points.

    Args:
        vertices: fit points
        degree: degree of B-spline
        method: 'uniform', 'distance' or 'centripetal', calculation method for parameter t
        power: power for 'centripetal', default is distance ^ .5
        subdivide: count of sub vertices + 1, e.g. 4 creates 3 sub-vertices

    Returns: list of vertices

    """
    spline = bspline_control_frame(vertices, degree=degree, method=method, power=power)
    return list(spline.approximate(segments=(len(vertices)-1)*subdivide))


def spline_interpolated_profiles(profiles, subdivide=4):
    """
    Profile interpolation by cubic B-spline interpolation.

    Args:
        profiles: list of profiles
        subdivide: count of interpolated profiles + 1, e.g. 4 creates 3 sub-profiles between two main profiles (4 face loops)

    Returns: yields profiles as list of vertices

    """
    profiles = [list(p) for p in profiles]
    if len(set(len(p) for p in profiles)) != 1:
        raise ValueError('All profiles have to have the same vertex count')

    vertex_count = len(profiles[0])
    edges = []  # interpolated spline vertices, where profile vertices are fit points
    for index in range(vertex_count):
        edge_vertices = [p[index] for p in profiles]
        edges.append(spline_interpolation(edge_vertices, subdivide=subdivide))

    profile_count = len(edges[0])
    for profile_index in range(profile_count):
        yield [edge[profile_index] for edge in edges]


def from_profiles_spline(profiles, subdivide=4, close=True, caps=False):
    """
    Mesh entity by spline interpolation between given profiles. Requires at least 4 profiles. A subdivide value of 4,
    means, create 4 face loops between two profiles, without interpolation two profiles create one face loop.

    Args:
        profiles: list of profiles
        subdivide: count of face loops
        close: close profile polygon if True
        caps: close hull with bottom cap and top cap (as N-gons)

    Returns: MeshVertexMerger()

    """
    if len(profiles) > 3:
        profiles = spline_interpolated_profiles(profiles, subdivide)
    else:
        raise ValueError("Spline interpolation requires at least 4 profiles")
    return from_profiles_linear(profiles, close=close, caps=caps)


def cone(count, radius, apex=(0, 0, 1), caps=True):
    """
    Cone as Mesh.

    Args:
        count: edge count of basis
        radius: radius of basis
        apex: apex of the cone
        caps: add a bottom face if true

    Returns: MeshVertexMerger()

    """
    mesh = MeshVertexMerger()
    base_circle = list(circle(count, radius, close=True))
    for p1, p2 in zip(base_circle, base_circle[1:]):
        mesh.add_face([p1, p2, apex])
    if caps:
        mesh.add_face(base_circle)
    return mesh


def rotation_form(count, profile, angle=2*pi, axis=(1, 0, 0)):
    """
    Mesh by rotating a profile around an axis.

    Args:
        count: count of rotated profiles
        profile: profile to rotate as list of vertices
        angle: rotation angle in radians
        axis: rotation axis

    Returns: MeshVertexMerger()

    """
    if count < 3:
        raise ValueError('count >= 2')
    delta = float(angle) / count
    m = Matrix44.axis_rotate(Vector(axis), delta)
    profile = [Vector(p) for p in profile]
    profiles = [profile]
    for _ in range(int(count)):
        profile = m.transform_vectors(profile)
        profiles.append(profile)
    mesh = from_profiles_linear(profiles, close=False, caps=False)
    return mesh


def doughnut(mcount, ncount, outer_radius=1., ring_radius=.25):
    pass


def sphere(mcount, ncount, radius=1.):
    pass
