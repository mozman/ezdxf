# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from typing import Sequence, List, Iterable, Union, TYPE_CHECKING, Tuple
from enum import IntEnum
import math
from ezdxf.math import Vec3, Vec2, Matrix44

if TYPE_CHECKING:
    from ezdxf.math import Vertex, AnyVec

__all__ = [
    "is_planar_face",
    "subdivide_face",
    "subdivide_ngons",
    "Plane",
    "LocationState",
    "normal_vector_3p",
    "distance_point_line_3d",
    "basic_transformation",
    "best_fit_normal",
    "BarycentricCoordinates",
    "linear_vertex_spacing",
]


class LocationState(IntEnum):
    COPLANAR = 0  # all the vertices are within the plane
    FRONT = 1  # all the vertices are in front of the plane
    BACK = 2  # all the vertices are at the back of the plane
    SPANNING = 3  # some vertices are in front, some in the back


def is_planar_face(face: Sequence[Vec3], abs_tol=1e-9) -> bool:
    """Returns ``True`` if sequence of vectors is a planar face.

    Args:
         face: sequence of :class:`~ezdxf.math.Vec3` objects
         abs_tol: tolerance for normals check

    """
    if len(face) < 3:
        return False
    if len(face) == 3:
        return True
    first_normal = None
    for index in range(len(face) - 2):
        a, b, c = face[index: index + 3]
        normal = (b - a).cross(c - b).normalize()
        if first_normal is None:
            first_normal = normal
        elif not first_normal.isclose(normal, abs_tol=abs_tol):
            return False
    return True


def subdivide_face(
    face: Sequence["AnyVec"], quads: bool = True
) -> Iterable[Tuple[Vec3, ...]]:
    """Yields new subdivided faces. Creates new faces from subdivided edges and
    the face midpoint by linear interpolation.

    Args:
        face: a sequence of vertices, :class:`Vec2` and :class:`Vec3` objects
            supported.
        quads: create quad faces if ``True`` else create triangles

    """
    if len(face) < 3:
        raise ValueError("3 or more vertices required.")
    len_face: int = len(face)
    mid_pos = Vec3.sum(face) / len_face
    subdiv_location: List[Vec3] = [
        face[i].lerp(face[(i + 1) % len_face]) for i in range(len_face)
    ]

    for index, vertex in enumerate(face):
        if quads:
            yield vertex, subdiv_location[index], mid_pos, subdiv_location[
                index - 1
            ]
        else:
            yield subdiv_location[index - 1], vertex, mid_pos
            yield vertex, subdiv_location[index], mid_pos


def subdivide_ngons(
    faces: Iterable[Sequence["AnyVec"]]
) -> Iterable[Tuple[Vec3, ...]]:
    """Yields only triangles or quad faces, subdivides ngons into triangles.

    Args:
        faces: iterable of faces as sequence of :class:`Vec2` and
            :class:`Vec3` objects

    """
    for face in faces:
        if len(face) < 5:
            yield Vec3.tuple(face)
        else:
            mid_pos = Vec3.sum(face) / len(face)
            for index, vertex in enumerate(face):
                yield face[index - 1], vertex, mid_pos


def normal_vector_3p(a: Vec3, b: Vec3, c: Vec3) -> Vec3:
    """Returns normal vector for 3 points, which is the normalized cross
    product for: :code:`a->b x a->c`.
    """
    return (b - a).cross(c - a).normalize()


def best_fit_normal(vertices: Iterable["Vertex"]) -> Vec3:
    """Returns the "best fit" normal for a plane defined by three or more
    vertices. This function tolerates imperfect plane vertices. Safe function
    to detect the extrusion vector of flat arbitrary polygons.

    """
    # Source: https://gamemath.com/book/geomprims.html#plane_best_fit (9.5.3)
    _vertices = Vec3.list(vertices)
    if len(_vertices) < 3:
        raise ValueError("3 or more vertices required")
    first = _vertices[0]
    if not first.isclose(_vertices[-1]):
        _vertices.append(first)  # close polygon
    prev_x, prev_y, prev_z = first.xyz
    nx = 0.0
    ny = 0.0
    nz = 0.0
    for v in _vertices[1:]:
        x, y, z = v.xyz
        nx += (prev_z + z) * (prev_y - y)
        ny += (prev_x + x) * (prev_z - z)
        nz += (prev_y + y) * (prev_x - x)
        prev_x = x
        prev_y = y
        prev_z = z
    return Vec3(nx, ny, nz).normalize()


def distance_point_line_3d(point: Vec3, start: Vec3, end: Vec3) -> float:
    """Returns the normal distance from `point` to 3D line defined by `start-`
    and `end` point.
    """
    if start.isclose(end):
        raise ZeroDivisionError("Not a line.")
    v1 = point - start
    # point projected onto line start to end:
    v2 = (end - start).project(v1)
    # Pythagoras:
    diff = v1.magnitude_square - v2.magnitude_square
    if diff <= 0.0:
        # This should not happen (abs(v1) > abs(v2)), but floating point
        # imprecision at very small values makes it possible!
        return 0.0
    else:
        return math.sqrt(diff)


def basic_transformation(
    move: "Vertex" = (0, 0, 0),
    scale: "Vertex" = (1, 1, 1),
    z_rotation: float = 0,
) -> Matrix44:
    """Returns a combined transformation matrix for translation, scaling and
    rotation about the z-axis.

    Args:
        move: translation vector
        scale: x-, y- and z-axis scaling as float triplet, e.g. (2, 2, 1)
        z_rotation: rotation angle about the z-axis in radians

    """
    sx, sy, sz = Vec3(scale)
    m = Matrix44.scale(sx, sy, sz)
    if z_rotation:
        m *= Matrix44.z_rotate(z_rotation)
    translate = Vec3(move)
    if not translate.is_null:
        m *= Matrix44.translate(translate.x, translate.y, translate.z)
    return m


class Plane:
    """Represents a plane in 3D space as normal vector and the perpendicular
    distance from origin.
    """

    __slots__ = ("_normal", "_distance_from_origin")

    def __init__(self, normal: Vec3, distance: float):
        self._normal = normal
        # the (perpendicular) distance of the plane from (0, 0, 0)
        self._distance_from_origin = distance

    @property
    def normal(self) -> Vec3:
        """Normal vector of the plane."""
        return self._normal

    @property
    def distance_from_origin(self) -> float:
        """The (perpendicular) distance of the plane from origin (0, 0, 0)."""
        return self._distance_from_origin

    @property
    def vector(self) -> Vec3:
        """Returns the location vector."""
        return self._normal * self._distance_from_origin

    @classmethod
    def from_3p(cls, a: Vec3, b: Vec3, c: Vec3) -> "Plane":
        """Returns a new plane from 3 points in space."""
        n = (b - a).cross(c - a).normalize()
        return Plane(n, n.dot(a))

    @classmethod
    def from_vector(cls, vector) -> "Plane":
        """Returns a new plane from a location vector."""
        v = Vec3(vector)
        return Plane(v.normalize(), v.magnitude)

    def __copy__(self) -> "Plane":
        """Returns a copy of the plane."""
        return self.__class__(self._normal, self._distance_from_origin)

    copy = __copy__

    def __repr__(self):
        return f"Plane({repr(self._normal)}, {self._distance_from_origin})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Plane):
            return NotImplemented
        return self.vector == other.vector

    def signed_distance_to(self, v: Vec3) -> float:
        """Returns signed distance of vertex `v` to plane, if distance is > 0,
        `v` is in 'front' of plane, in direction of the normal vector, if
        distance is < 0, `v` is at the 'back' of the plane, in the opposite
        direction of the normal vector.

        """
        return self._normal.dot(v) - self._distance_from_origin

    def distance_to(self, v: Vec3) -> float:
        """Returns absolute (unsigned) distance of vertex `v` to plane."""
        return math.fabs(self.signed_distance_to(v))

    def is_coplanar_vertex(self, v: Vec3, abs_tol=1e-9) -> bool:
        """Returns ``True`` if vertex `v` is coplanar, distance from plane to
        vertex `v` is 0.
        """
        return self.distance_to(v) < abs_tol

    def is_coplanar_plane(self, p: "Plane", abs_tol=1e-9) -> bool:
        """Returns ``True`` if plane `p` is coplanar, normal vectors in same or
        opposite direction.
        """
        n_is_close = self._normal.isclose
        return n_is_close(p._normal, abs_tol=abs_tol) or n_is_close(
            -p._normal, abs_tol=abs_tol
        )


class BarycentricCoordinates:
    """Barycentric coordinate calculation.

    The arguments `a`, `b` and `c` are the cartesian coordinates of an arbitrary
    triangle in 3D space. The barycentric coordinates (b1, b2, b3) define the
    linear combination of `a`, `b` and `c` to represent the point `p`::

        p = a * b1 + b * b2 + c * b3

    This implementation returns the barycentric coordinates of the normal
    projection of `p` onto the plane defined by (a, b, c).

    These barycentric coordinates have some useful properties:

    - if all barycentric coordinates (b1, b2, b3) are in the range [0, 1], then
      the point `p` is inside the triangle (a, b, c)
    - if one of the coordinates is negative, the point `p` is outside the
      triangle
    - the sum of b1, b2 and b3 is always 1
    - the center of "mass" has the barycentric coordinates (1/3, 1/3, 1/3) =
      (a + b + c)/3

    """

    # Source: https://gamemath.com/book/geomprims.html#triangle_barycentric_space

    def __init__(self, a: "Vertex", b: "Vertex", c: "Vertex"):
        self.a = Vec3(a)
        self.b = Vec3(b)
        self.c = Vec3(c)
        self._e1 = self.c - self.b
        self._e2 = self.a - self.c
        self._e3 = self.b - self.a
        e1xe2 = self._e1.cross(self._e2)
        self._n = e1xe2.normalize()
        self._denom = e1xe2.dot(self._n)
        if abs(self._denom) < 1e-9:
            raise ValueError("invalid triangle")

    def from_cartesian(self, p: "Vertex") -> Vec3:
        p = Vec3(p)
        n = self._n
        denom = self._denom
        d1 = p - self.a
        d2 = p - self.b
        d3 = p - self.c
        b1 = self._e1.cross(d3).dot(n) / denom
        b2 = self._e2.cross(d1).dot(n) / denom
        b3 = self._e3.cross(d2).dot(n) / denom
        return Vec3(b1, b2, b3)

    def to_cartesian(self, b: "Vertex") -> Vec3:
        b1, b2, b3 = Vec3(b).xyz
        return self.a * b1 + self.b * b2 + self.c * b3


def linear_vertex_spacing(start: Vec3, end: Vec3, count: int) -> List[Vec3]:
    """Returns `count` evenly spaced vertices from `start` to `end`."""
    if count <= 2:
        return [start, end]
    distance = end - start
    if distance.is_null:
        return [start] * count

    vertices = [start]
    step = distance.normalize(distance.magnitude / (count - 1))
    for index in range(1, count - 1):
        vertices.append(start + (step * index))
    vertices.append(end)
    return vertices
