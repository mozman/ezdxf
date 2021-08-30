# Copyright (c) 2018-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List, Tuple, Sequence
from math import pi, sin, cos, radians, tan, isclose, asin, fabs
from enum import IntEnum
from ezdxf.math import (
    Vec3,
    Matrix44,
    global_bspline_interpolation,
    EulerSpiral,
)
from ezdxf.render.mesh import MeshVertexMerger, MeshTransformer

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

__all__ = [
    "circle",
    "ellipse",
    "euler_spiral",
    "square",
    "box",
    "open_arrow",
    "arrow2",
    "ngon",
    "star",
    "gear",
    "translate",
    "rotate",
    "scale",
    "close_polygon",
    "cube",
    "extrude",
    "cylinder",
    "cylinder_2p",
    "from_profiles_linear",
    "from_profiles_spline",
    "spline_interpolation",
    "spline_interpolated_profiles",
    "cone",
    "cone_2p",
    "rotation_form",
    "sphere",
]


def circle(
    count: int, radius: float = 1, elevation: float = 0, close: bool = False
) -> Iterable[Vec3]:
    """Create polygon vertices for a `circle <https://en.wikipedia.org/wiki/Circle>`_
    with the given `radius` and approximated by `count` vertices, `elevation`
    is the z-axis for all vertices.

    Args:
        count: count of polygon vertices
        radius: circle radius
        elevation: z-axis for all vertices
        close: yields first vertex also as last vertex if ``True``.

    Returns:
        vertices in counter clockwise orientation as :class:`~ezdxf.math.Vec3`
        objects

    """
    radius = float(radius)
    delta = 2.0 * pi / count
    alpha = 0.0
    for index in range(count):
        x = cos(alpha) * radius
        y = sin(alpha) * radius
        yield Vec3(x, y, elevation)
        alpha += delta

    if close:
        yield Vec3(radius, 0, elevation)


def ellipse(
    count: int,
    rx: float = 1,
    ry: float = 1,
    start_param: float = 0,
    end_param: float = 2 * pi,
    elevation: float = 0,
) -> Iterable[Vec3]:
    """Create polygon vertices for an `ellipse <https://en.wikipedia.org/wiki/Ellipse>`_
    with given `rx` as x-axis radius and `ry` as y-axis radius approximated by
    `count` vertices, `elevation` is the z-axis for all vertices.
    The ellipse goes from `start_param` to `end_param` in counter clockwise
    orientation.

    Args:
        count: count of polygon vertices
        rx: ellipse x-axis radius
        ry: ellipse y-axis radius
        start_param: start of ellipse in range [0, 2π]
        end_param: end of ellipse in range [0, 2π]
        elevation: z-axis for all vertices

    Returns:
        vertices in counter clockwise orientation as :class:`~ezdxf.math.Vec3`
        objects

    """
    rx = float(rx)
    ry = float(ry)
    start_param = float(start_param)
    end_param = float(end_param)
    count = int(count)
    delta = (end_param - start_param) / (count - 1)
    for param in range(count):
        alpha = start_param + param * delta
        yield Vec3(cos(alpha) * rx, sin(alpha) * ry, elevation)


def euler_spiral(
    count: int, length: float = 1, curvature: float = 1, elevation: float = 0
) -> Iterable[Vec3]:
    """Create polygon vertices for an `euler spiral <https://en.wikipedia.org/wiki/Euler_spiral>`_
    of a given `length` and radius of curvature. This is a parametric curve,
    which always starts at the origin (0, 0).

    Args:
        count: count of polygon vertices
        length: length of curve in drawing units
        curvature: radius of curvature
        elevation: z-axis for all vertices

    Returns:
        vertices as :class:`~ezdxf.math.Vec3` objects

    """
    spiral = EulerSpiral(curvature=curvature)
    for vertex in spiral.approximate(length, count - 1):
        yield vertex.replace(z=elevation)


def square(size: float = 1.0) -> Tuple[Vec3, Vec3, Vec3, Vec3]:
    """Returns 4 vertices for a square with a side length of the given `size`,
    lower left corner is ``(0, 0)``, upper right corner is (`size`, `size`).

    """
    return Vec3(0, 0), Vec3(size, 0), Vec3(size, size), Vec3(0, size)


def box(sx: float = 1.0, sy: float = 1.0) -> Tuple[Vec3, Vec3, Vec3, Vec3]:
    """Returns 4 vertices for a box with a width of `sx` by and a height of
    `sy`, lower left corner is ``(0, 0)``, upper right corner is (`sx`, `sy`).

    """
    return Vec3(0, 0), Vec3(sx, 0), Vec3(sx, sy), Vec3(0, sy)


def open_arrow(
    size: float = 1.0, angle: float = 30.0
) -> Tuple[Vec3, Vec3, Vec3]:
    """Returns 3 vertices for an open arrow `<` with a length of the given
    `size`, argument `angle` defines the enclosing angle in degrees.
    Vertex order: upward end vertex, tip (0, 0) , downward end vertex (counter
    clockwise order)

    Args:
        size: length of arrow
        angle: enclosing angle in degrees

    """
    h = sin(radians(angle / 2.0)) * size
    return Vec3(-size, h), Vec3(0, 0), Vec3(-size, -h)


def arrow2(
    size: float = 1.0, angle: float = 30.0, beta: float = 45.0
) -> Tuple[Vec3, Vec3, Vec3, Vec3]:
    """Returns 4 vertices for an arrow with a length of the given `size`, and
    an enclosing `angle` in degrees and a slanted back side defined by angle
    `beta`::

                    ****
                ****  *
            ****     *
        **** angle   X********************
            ****     * +beta
                ****  *
                    ****

                    ****
                ****    *
            ****         *
        **** angle        X***************
            ****         * -beta
                ****    *
                    ****

    Vertex order: upward end vertex, tip (0, 0), downward end vertex, bottom
    vertex `X` (anti clockwise order).

    Bottom vertex `X` is also the connection point to a continuation line.

    Args:
        size: length of arrow
        angle: enclosing angle in degrees
        beta: angle if back side in degrees

    """
    h = sin(radians(angle / 2.0)) * size
    back_step = tan(radians(beta)) * h
    return (
        Vec3(-size, h),
        Vec3(0, 0),
        Vec3(-size, -h),
        Vec3(-size + back_step, 0),
    )


def ngon(
    count: int,
    length: float = None,
    radius: float = None,
    rotation: float = 0.0,
    elevation: float = 0.0,
    close: bool = False,
) -> Iterable[Vec3]:
    """Returns the corner vertices of a `regular polygon <https://en.wikipedia.org/wiki/Regular_polygon>`_.
    The polygon size is determined by the edge `length` or the circum `radius`
    argument. If both are given `length` has the higher priority.

    Args:
        count: count of polygon corners >= 3
        length: length of polygon side
        radius: circum radius
        rotation: rotation angle in radians
        elevation: z-axis for all vertices
        close: yields first vertex also as last vertex if ``True``.

    Returns:
        vertices as :class:`~ezdxf.math.Vec3` objects

    """
    if count < 3:
        raise ValueError("Argument `count` has to be greater than 2.")
    if length is not None:
        if length <= 0.0:
            raise ValueError("Argument `length` has to be greater than 0.")
        radius = length / 2.0 / sin(pi / count)
    elif radius is not None:
        if radius <= 0.0:
            raise ValueError("Argument `radius` has to be greater than 0.")
    else:
        raise ValueError("Argument `length` or `radius` required.")

    delta = 2.0 * pi / count
    angle = rotation
    first = None
    for _ in range(count):
        v = Vec3(radius * cos(angle), radius * sin(angle), elevation)
        if first is None:
            first = v
        yield v
        angle += delta

    if close:
        yield first


def star(
    count: int,
    r1: float,
    r2: float,
    rotation: float = 0.0,
    elevation: float = 0.0,
    close: bool = False,
) -> Iterable[Vec3]:
    """Returns the corner vertices for a `star shape <https://en.wikipedia.org/wiki/Star_polygon>`_.

    The shape has `count` spikes, `r1` defines the radius of the "outer"
    vertices and `r2` defines the radius of the "inner" vertices,
    but this does not mean that `r1` has to be greater than `r2`.

    Args:
        count: spike count >= 3
        r1: radius 1
        r2: radius 2
        rotation: rotation angle in radians
        elevation: z-axis for all vertices
        close: yields first vertex also as last vertex if ``True``.

    Returns:
        vertices as :class:`~ezdxf.math.Vec3` objects

    """
    if count < 3:
        raise ValueError("Argument `count` has to be greater than 2.")
    if r1 <= 0.0:
        raise ValueError("Argument `r1` has to be greater than 0.")
    if r2 <= 0.0:
        raise ValueError("Argument `r2` has to be greater than 0.")

    corners1 = ngon(
        count, radius=r1, rotation=rotation, elevation=elevation, close=False
    )
    corners2 = ngon(
        count,
        radius=r2,
        rotation=pi / count + rotation,
        elevation=elevation,
        close=False,
    )
    first = None
    for s1, s2 in zip(corners1, corners2):
        if first is None:
            first = s1
        yield s1
        yield s2

    if close:
        yield first


class _Gear(IntEnum):
    TOP_START = 0
    TOP_END = 1
    BOTTOM_START = 2
    BOTTOM_END = 3


def gear(
    count: int,
    top_width: float,
    bottom_width: float,
    height: float,
    outside_radius: float,
    elevation: float = 0,
    close: bool = False,
) -> Iterable[Vec3]:
    """Returns the corner vertices of a `gear shape <https://en.wikipedia.org/wiki/Gear>`_
    (cogwheel).

    .. warning::

        This function does not create correct gears for mechanical engineering!

    Args:
        count: teeth count >= 3
        top_width: teeth width at outside radius
        bottom_width: teeth width at base radius
        height: teeth height; base radius = outside radius - height
        outside_radius: outside radius
        elevation: z-axis for all vertices
        close: yields first vertex also as last vertex if True.

    Returns:
        vertices in counter clockwise orientation as :class:`~ezdxf.math.Vec3`
        objects

    """
    if count < 3:
        raise ValueError("Argument `count` has to be greater than 2.")
    if outside_radius <= 0.0:
        raise ValueError("Argument `radius` has to be greater than 0.")
    if top_width <= 0.0:
        raise ValueError("Argument `width` has to be greater than 0.")
    if bottom_width <= 0.0:
        raise ValueError("Argument `width` has to be greater than 0.")
    if height <= 0.0:
        raise ValueError("Argument `height` has to be greater than 0.")
    if height >= outside_radius:
        raise ValueError("Argument `height` has to be smaller than `radius`")

    base_radius = outside_radius - height
    alpha_top = asin(top_width / 2.0 / outside_radius)  # angle at tooth top
    alpha_bottom = asin(
        bottom_width / 2.0 / base_radius
    )  # angle at tooth bottom
    alpha_difference = (
        alpha_bottom - alpha_top
    ) / 2.0  # alpha difference at start and end of tooth
    beta = (2.0 * pi - count * alpha_bottom) / count
    angle = -alpha_top / 2.0  # center of first tooth is in x-axis direction
    state = _Gear.TOP_START
    first = None
    for _ in range(4 * count):
        if state == _Gear.TOP_START or state == _Gear.TOP_END:
            radius = outside_radius
        else:
            radius = base_radius
        v = Vec3(radius * cos(angle), radius * sin(angle), elevation)

        if state == _Gear.TOP_START:
            angle += alpha_top
        elif state == _Gear.TOP_END:
            angle += alpha_difference
        elif state == _Gear.BOTTOM_START:
            angle += beta
        elif state == _Gear.BOTTOM_END:
            angle += alpha_difference

        if first is None:
            first = v
        yield v

        state += 1  # type: ignore
        if state > _Gear.BOTTOM_END:
            state = _Gear.TOP_START

    if close:
        yield first


def translate(
    vertices: Iterable["Vertex"], vec: "Vertex" = (0, 0, 0)
) -> Iterable[Vec3]:
    """Translate `vertices` along `vec`, faster than a Matrix44 transformation.

    Args:
        vertices: iterable of vertices
        vec: translation vector

    Returns: yields transformed vertices

    """
    _vec = Vec3(vec)
    for p in vertices:
        yield _vec + p


def rotate(
    vertices: Iterable["Vertex"], angle: float = 0.0, deg: bool = True
) -> Iterable[Vec3]:
    """Rotate `vertices` about to z-axis at to origin (0, 0), faster than a
    Matrix44 transformation.

    Args:
        vertices: iterable of vertices
        angle: rotation angle
        deg: True if angle in degrees, False if angle in radians

    Returns: yields transformed vertices

    """
    if deg:
        return (Vec3(v).rotate_deg(angle) for v in vertices)
    else:
        return (Vec3(v).rotate(angle) for v in vertices)


def scale(
    vertices: Iterable["Vertex"], scaling=(1.0, 1.0, 1.0)
) -> Iterable[Vec3]:
    """Scale `vertices` around the origin (0, 0), faster than a Matrix44
    transformation.

    Args:
        vertices: iterable of vertices
        scaling: scale factors as tuple of floats for x-, y- and z-axis

    Returns: yields scaled vertices

    """
    sx, sy, sz = scaling
    for v in Vec3.generate(vertices):
        yield Vec3(v.x * sx, v.y * sy, v.z * sz)


def close_polygon(
    vertices: Iterable["Vertex"], rel_tol: float = 1e-9, abs_tol: float = 1e-12
) -> List["Vertex"]:
    """Returns list of vertices, where vertices[0] == vertices[-1]."""
    vertices = list(vertices)
    if not Vec3(vertices[0]).isclose(
        vertices[-1], rel_tol=rel_tol, abs_tol=abs_tol
    ):
        vertices.append(vertices[0])
    return vertices


# 8 corner vertices
_cube_vertices = [
    Vec3(0, 0, 0),
    Vec3(1, 0, 0),
    Vec3(1, 1, 0),
    Vec3(0, 1, 0),
    Vec3(0, 0, 1),
    Vec3(1, 0, 1),
    Vec3(1, 1, 1),
    Vec3(0, 1, 1),
]

# 8 corner vertices, 'mass' center in (0, 0, 0)
_cube0_vertices = [
    Vec3(-0.5, -0.5, -0.5),
    Vec3(+0.5, -0.5, -0.5),
    Vec3(+0.5, +0.5, -0.5),
    Vec3(-0.5, +0.5, -0.5),
    Vec3(-0.5, -0.5, +0.5),
    Vec3(+0.5, -0.5, +0.5),
    Vec3(+0.5, +0.5, +0.5),
    Vec3(-0.5, +0.5, +0.5),
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


def cube(center: bool = True) -> MeshTransformer:
    """Create a `cube <https://en.wikipedia.org/wiki/Cube>`_ as
    :class:`~ezdxf.render.MeshTransformer` object.

    Args:
        center: 'mass' center of cube, ``(0, 0, 0)`` if ``True``, else first
            corner at ``(0, 0, 0)``

    Returns: :class:`~ezdxf.render.MeshTransformer`

    """
    mesh = MeshTransformer()
    vectices = _cube0_vertices if center else _cube_vertices
    mesh.add_mesh(vertices=vectices, faces=cube_faces)  # type: ignore
    return mesh


def extrude(
    profile: Iterable["Vertex"], path: Iterable["Vertex"], close=True
) -> MeshTransformer:
    """Extrude a `profile` polygon along a `path` polyline, vertices of profile
    should be in counter clockwise order.

    Args:
        profile: sweeping profile as list of (x, y, z) tuples in counter
            clockwise order
        path:  extrusion path as list of (x, y, z) tuples
        close: close profile polygon if ``True``

    Returns: :class:`~ezdxf.render.MeshTransformer`

    """

    def add_hull(bottom_profile, top_profile):
        prev_bottom = bottom_profile[0]
        prev_top = top_profile[0]
        for bottom, top in zip(bottom_profile[1:], top_profile[1:]):
            face = (
                prev_bottom,
                bottom,
                top,
                prev_top,
            )  # counter clock wise: normals outwards
            mesh.faces.append(face)
            prev_bottom = bottom
            prev_top = top

    mesh = MeshVertexMerger()
    profile = Vec3.list(profile)
    if close:
        profile = close_polygon(profile)
    path = Vec3.list(path)
    start_point = path[0]  # type: ignore
    bottom_indices = mesh.add_vertices(profile)  # base profile
    for target_point in path[1:]:  # type: ignore
        translation_vector = target_point - start_point
        # profile will just be translated
        profile = [vec + translation_vector for vec in profile]
        top_indices = mesh.add_vertices(profile)
        add_hull(bottom_indices, top_indices)
        bottom_indices = top_indices
        start_point = target_point
    return MeshTransformer.from_builder(mesh)


def cylinder(
    count: int = 16,
    radius: float = 1.0,
    top_radius: float = None,
    top_center: "Vertex" = (0, 0, 1),
    caps=True,
    ngons=True,
) -> MeshTransformer:
    """Create a `cylinder <https://en.wikipedia.org/wiki/Cylinder>`_ as
    :class:`~ezdxf.render.MeshTransformer` object, the base center is fixed in
    the origin (0, 0, 0).

    Args:
        count: profiles edge count
        radius: radius for bottom profile
        top_radius: radius for top profile, if ``None`` top_radius == radius
        top_center: location vector for the center of the top profile
        caps: close hull with bottom cap and top cap (as N-gons)
        ngons: use ngons for caps if ``True`` else subdivide caps into triangles

    Returns: :class:`~ezdxf.render.MeshTransformer`

    """
    if top_radius is None:
        top_radius = radius

    if isclose(top_radius, 0.0):  # pyramid/cone
        return cone(count=count, radius=radius, apex=top_center)

    base_profile = list(circle(count, radius, close=True))
    top_profile = list(
        translate(circle(count, top_radius, close=True), top_center)
    )
    return from_profiles_linear(
        [base_profile, top_profile], caps=caps, ngons=ngons
    )


def cylinder_2p(
    count: int = 16,
    radius: float = 1,
    base_center=(0, 0, 0),
    top_center=(0, 0, 1),
) -> MeshTransformer:
    """Create a `cylinder <https://en.wikipedia.org/wiki/Cylinder>`_ as
    :class:`~ezdxf.render.MeshTransformer` object from two points,
    `base_center` is the center of the base circle and, `top_center` the center
    of the top circle.

    Args:
        count: profiles edge count
        radius: radius for bottom profile
        base_center: center of base circle
        top_center: center of top circle

    Returns: :class:`~ezdxf.render.MeshTransformer`

    """
    # Copyright (c) 2011 Evan Wallace (http://madebyevan.com/), under the MIT license.
    # Python port Copyright (c) 2012 Tim Knip (http://www.floorplanner.com), under the MIT license.
    # Additions by Alex Pletzer (Pennsylvania State University)
    # Adaptation for ezdxf, Copyright (c) 2020, Manfred Moitzi, MIT License.
    start = Vec3(base_center)
    end = Vec3(top_center)
    radius = float(radius)
    slices = int(count)
    ray = end - start

    z_axis = ray.normalize()
    is_y = fabs(z_axis.y) > 0.5
    x_axis = Vec3(float(is_y), float(not is_y), 0).cross(z_axis).normalize()
    y_axis = x_axis.cross(z_axis).normalize()
    mesh = MeshVertexMerger()

    def vertex(stack, angle):
        out = (x_axis * cos(angle)) + (y_axis * sin(angle))
        return start + (ray * stack) + (out * radius)

    dt = pi * 2 / float(slices)
    for i in range(0, slices):
        t0 = i * dt
        i1 = (i + 1) % slices
        t1 = i1 * dt
        mesh.add_face([start, vertex(0, t0), vertex(0, t1)])
        mesh.add_face(
            [vertex(0, t1), vertex(0, t0), vertex(1, t0), vertex(1, t1)]
        )
        mesh.add_face([end, vertex(1, t1), vertex(1, t0)])
    return MeshTransformer.from_builder(mesh)


def ngon_to_triangles(face: Iterable["Vertex"]) -> Iterable[Sequence[Vec3]]:
    _face = Vec3.list(face)
    if _face[0].isclose(_face[-1]):  # closed shape
        center = Vec3.sum(_face[:-1]) / (len(_face) - 1)
    else:
        center = Vec3.sum(_face) / len(_face)
        _face.append(_face[0])

    for v1, v2 in zip(_face[:-1], _face[1:]):
        yield v1, v2, center


def from_profiles_linear(
    profiles: Iterable[Iterable["Vertex"]], close=True, caps=False, ngons=True
) -> MeshTransformer:
    """Create MESH entity by linear connected `profiles`.

    Args:
        profiles: list of profiles
        close: close profile polygon if ``True``
        caps: close hull with bottom cap and top cap
        ngons: use ngons for caps if ``True`` else subdivide caps into triangles

    Returns: :class:`~ezdxf.render.MeshTransformer`

    """
    mesh = MeshVertexMerger()
    profiles = list(profiles)
    if close:
        profiles = [close_polygon(p) for p in profiles]
    if caps:
        base = reversed(profiles[0])  # type: ignore # for correct outside pointing normals
        top = profiles[-1]
        if ngons:
            mesh.add_face(base)
            mesh.add_face(top)
        else:
            for face in ngon_to_triangles(base):
                mesh.add_face(face)
            for face in ngon_to_triangles(top):
                mesh.add_face(face)

    for profile1, profile2 in zip(profiles, profiles[1:]):
        prev_v1, prev_v2 = None, None
        for v1, v2 in zip(profile1, profile2):
            if prev_v1 is not None:
                mesh.add_face([prev_v1, v1, v2, prev_v2])
            prev_v1 = v1
            prev_v2 = v2

    return MeshTransformer.from_builder(mesh)


def spline_interpolation(
    vertices: Iterable["Vertex"],
    degree: int = 3,
    method: str = "chord",
    subdivide: int = 4,
) -> List[Vec3]:
    """B-spline interpolation, vertices are fit points for the spline
    definition.

    Only method 'uniform', yields vertices at fit points.

    Args:
        vertices: fit points
        degree: degree of B-spline
        method: "uniform", "chord"/"distance", "centripetal"/"sqrt_chord" or
            "arc" calculation method for parameter t
        subdivide: count of sub vertices + 1, e.g. 4 creates 3 sub-vertices

    Returns: list of vertices

    """
    vertices = list(vertices)
    spline = global_bspline_interpolation(
        vertices, degree=degree, method=method
    )
    return list(spline.approximate(segments=(len(vertices) - 1) * subdivide))


def spline_interpolated_profiles(
    profiles: Iterable[Iterable["Vertex"]], subdivide: int = 4
) -> Iterable[List[Vec3]]:
    """Profile interpolation by cubic B-spline interpolation.

    Args:
        profiles: list of profiles
        subdivide: count of interpolated profiles + 1, e.g. 4 creates 3
            sub-profiles between two main profiles (4 face loops)

    Returns: yields profiles as list of vertices

    """
    _profiles = [list(p) for p in profiles]
    if len(set(len(p) for p in _profiles)) != 1:
        raise ValueError("All profiles have to have the same vertex count")

    vertex_count = len(_profiles[0])
    edges = (
        []
    )  # interpolated spline vertices, where profile vertices are fit points
    for index in range(vertex_count):
        edge_vertices = [p[index] for p in _profiles]
        edges.append(spline_interpolation(edge_vertices, subdivide=subdivide))

    profile_count = len(edges[0])
    for profile_index in range(profile_count):
        yield [edge[profile_index] for edge in edges]


def from_profiles_spline(
    profiles: Iterable[Iterable["Vertex"]],
    subdivide: int = 4,
    close=True,
    caps=False,
    ngons=True,
) -> MeshTransformer:
    """Create MESH entity by spline interpolation between given `profiles`.
    Requires at least 4 profiles. A subdivide value of 4, means, create 4 face
    loops between two profiles, without interpolation two profiles create one
    face loop.

    Args:
        profiles: list of profiles
        subdivide: count of face loops
        close: close profile polygon if ``True``
        caps: close hull with bottom cap and top cap
        ngons: use ngons for caps if ``True`` else subdivide caps into triangles

    Returns: :class:`~ezdxf.render.MeshTransformer`

    """
    profiles = list(profiles)
    if len(profiles) > 3:
        profiles = spline_interpolated_profiles(profiles, subdivide)  # type: ignore
    else:
        raise ValueError("Spline interpolation requires at least 4 profiles")
    return from_profiles_linear(profiles, close=close, caps=caps, ngons=ngons)


def cone(
    count: int = 16,
    radius: float = 1.0,
    apex: "Vertex" = (0, 0, 1),
    caps=True,
    ngons=True,
) -> MeshTransformer:
    """Create a `cone <https://en.wikipedia.org/wiki/Cone>`_ as
    :class:`~ezdxf.render.MeshTransformer` object, the base center is fixed in
    the origin (0, 0, 0).

    Args:
        count: edge count of basis_vector
        radius: radius of basis_vector
        apex: tip of the cone
        caps: add a bottom face if ``True``
        ngons: use ngons for caps if ``True`` else subdivide caps into triangles

    Returns: :class:`~ezdxf.render.MeshTransformer`

    """
    mesh = MeshVertexMerger()
    base_circle = list(circle(count, radius, close=True))
    for p1, p2 in zip(base_circle, base_circle[1:]):
        mesh.add_face([p1, p2, apex])
    if caps:
        base_circle = reversed(  # type: ignore
            base_circle
        )  # for correct outside pointing normals
        if ngons:
            mesh.add_face(base_circle)
        else:
            for face in ngon_to_triangles(base_circle):
                mesh.add_face(face)

    return MeshTransformer.from_builder(mesh)


def cone_2p(
    count: int = 16, radius: float = 1.0, base_center=(0, 0, 0), apex=(0, 0, 1)
) -> MeshTransformer:
    """Create a `cone <https://en.wikipedia.org/wiki/Cone>`_ as
    :class:`~ezdxf.render.MeshTransformer` object from two points, `base_center`
    is the center of the base circle and `apex` as the tip of the cone.

    Args:
        count: edge count of basis_vector
        radius: radius of basis_vector
        base_center: center point of base circle
        apex: tip of the cone

    Returns: :class:`~ezdxf.render.MeshTransformer`

    """
    # Copyright (c) 2011 Evan Wallace (http://madebyevan.com/), under the MIT license.
    # Python port Copyright (c) 2012 Tim Knip (http://www.floorplanner.com), under the MIT license.
    # Additions by Alex Pletzer (Pennsylvania State University)
    # Adaptation for ezdxf, Copyright (c) 2020, Manfred Moitzi, MIT License.
    start = Vec3(base_center)
    end = Vec3(apex)
    slices = int(count)
    ray = end - start
    z_axis = ray.normalize()
    is_y = fabs(z_axis.y) > 0.5
    x_axis = Vec3(float(is_y), float(not is_y), 0).cross(z_axis).normalize()
    y_axis = x_axis.cross(z_axis).normalize()
    mesh = MeshVertexMerger()

    def vertex(angle) -> Vec3:
        # radial direction pointing out
        out = x_axis * cos(angle) + y_axis * sin(angle)
        return start + out * radius

    dt = pi * 2.0 / slices
    for i in range(0, slices):
        t0 = i * dt
        i1 = (i + 1) % slices
        t1 = i1 * dt
        # coordinates and associated normal pointing outwards of the cone's
        # side
        p0 = vertex(t0)
        p1 = vertex(t1)
        # polygon on the low side (disk sector)
        mesh.add_face([start, p0, p1])
        # polygon extending from the low side to the tip
        mesh.add_face([p0, end, p1])

    return MeshTransformer.from_builder(mesh)


def rotation_form(
    count: int,
    profile: Iterable["Vertex"],
    angle: float = 2 * pi,
    axis: "Vertex" = (1, 0, 0),
) -> MeshTransformer:
    """Create MESH entity by rotating a `profile` around an `axis`.

    Args:
        count: count of rotated profiles
        profile: profile to rotate as list of vertices
        angle: rotation angle in radians
        axis: rotation axis

    Returns: :class:`~ezdxf.render.MeshTransformer`

    """
    if count < 3:
        raise ValueError("count >= 2")
    delta = float(angle) / count
    m = Matrix44.axis_rotate(Vec3(axis), delta)
    profile = [Vec3(p) for p in profile]
    profiles = [profile]
    for _ in range(int(count)):
        profile = list(m.transform_vertices(profile))
        profiles.append(profile)
    mesh = from_profiles_linear(profiles, close=False, caps=False)
    return mesh


def sphere(
    count: int = 16, stacks: int = 8, radius: float = 1, quads=True
) -> MeshTransformer:
    """Create a `sphere <https://en.wikipedia.org/wiki/Sphere>`_ as
    :class:`~ezdxf.render.MeshTransformer` object, center is fixed at origin
    (0, 0, 0).

    Args:
        count: longitudinal slices
        stacks: latitude slices
        radius: radius of sphere
        quads: use quads for body faces if ``True`` else triangles

    Returns: :class:`~ezdxf.render.MeshTransformer`

    """
    radius = float(radius)
    slices = int(count)
    stacks_2 = int(stacks) // 2  # stacks from -stack/2 to +stack/2
    delta_theta = pi * 2.0 / float(slices)
    delta_phi = pi / float(stacks)
    mesh = MeshVertexMerger()

    def radius_of_stack(stack: float) -> float:
        return radius * cos(delta_phi * stack)

    def vertex(slice_: float, r: float, z: float) -> Vec3:
        actual_theta = delta_theta * slice_
        return Vec3(cos(actual_theta) * r, sin(actual_theta) * r, z)

    def cap_triangles(stack, top=False):
        z = sin(stack * delta_phi) * radius
        cap_vertex = Vec3(0, 0, radius) if top else Vec3(0, 0, -radius)
        r1 = radius_of_stack(stack)
        for slice_ in range(slices):
            v1 = vertex(slice_, r1, z)
            v2 = vertex(slice_ + 1, r1, z)
            if top:
                mesh.add_face((v1, v2, cap_vertex))
            else:
                mesh.add_face((cap_vertex, v2, v1))

    # bottom triangle faces
    cap_triangles(-stacks_2 + 1, top=False)

    # add body faces
    for actual_stack in range(-stacks_2 + 1, stacks_2 - 1):
        next_stack = actual_stack + 1
        r1 = radius_of_stack(actual_stack)
        r2 = radius_of_stack(next_stack)
        z1 = sin(delta_phi * actual_stack) * radius
        z2 = sin(delta_phi * next_stack) * radius
        for i in range(slices):
            v1 = vertex(i, r1, z1)
            v2 = vertex(i + 1, r1, z1)
            v3 = vertex(i + 1, r2, z2)
            v4 = vertex(i, r2, z2)
            if quads:
                mesh.add_face([v1, v2, v3, v4])
            else:
                center = vertex(
                    i + 0.5,
                    radius_of_stack(actual_stack + 0.5),
                    sin(delta_phi * (actual_stack + 0.5)) * radius,
                )
                mesh.add_face([v1, v2, center])
                mesh.add_face([v2, v3, center])
                mesh.add_face([v3, v4, center])
                mesh.add_face([v4, v1, center])

    # top triangle faces
    cap_triangles(stacks_2 - 1, top=True)

    return MeshTransformer.from_builder(mesh)
