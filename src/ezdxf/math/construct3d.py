# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Sequence, List, Iterable, Union, Tuple
from enum import IntEnum
import math
from .vector import Vector, Vec2


class LocationState(IntEnum):
    COPLANAR = 0  # all the vertices are within the plane
    FRONT = 1  # all the vertices are in front of the plane
    BACK = 2  # all the vertices are at the back of the plane
    SPANNING = 3  # some vertices are in front, some in the back


def is_planar_face(face: Sequence[Vector], abs_tol=1e-9) -> bool:
    """ Returns ``True`` if sequence of vectors is a planar face.

    Args:
         face: sequence of :class:`~ezdxf.math.Vector` objects
         abs_tol: tolerance for normals check

    .. versionadded:: 0.11

    """
    if len(face) < 3:
        return False
    if len(face) == 3:
        return True
    first_normal = None
    for index in range(len(face) - 2):
        a, b, c = face[index:index + 3]
        normal = (b - a).cross(c - b).normalize()
        if first_normal is None:
            first_normal = normal
        elif not first_normal.isclose(normal, abs_tol):
            return False
    return True


def subdivide_face(face: Sequence[Union[Vector, Vec2]], quads=True) -> Iterable[List[Vector]]:
    """ Yields new subdivided faces. Creates new faces from subdivided edges and the face midpoint by linear
    interpolation.

    Args:
        face: a sequence of vertices, :class:`Vec2` and :class:`Vector` objects supported.
        quads: create quad faces if ``True`` else create triangles

    .. versionadded:: 0.11

    """
    if len(face) < 3:
        raise ValueError('3 or more vertices required.')
    len_face = len(face)
    mid_pos = sum(face) / len_face
    subdiv_location = [face[i].lerp(face[(i + 1) % len_face]) for i in range(len_face)]

    for index, vertex in enumerate(face):
        if quads:
            yield vertex, subdiv_location[index], mid_pos, subdiv_location[index - 1]
        else:
            yield subdiv_location[index - 1], vertex, mid_pos
            yield vertex, subdiv_location[index], mid_pos


def subdivide_ngons(faces: Iterable[Sequence[Union[Vector, Vec2]]]) -> Iterable[List[Vector]]:
    """
    Yields only triangles or quad faces, subdivides ngons into triangles.

    Args:
        faces: iterable of faces as sequence of :class:`Vec2` and :class:`Vector` objects

    .. versionadded:: 0.12

    """
    for face in faces:
        if len(face) < 5:
            yield face
        else:
            mid_pos = sum(face) / len(face)
            for index, vertex in enumerate(face):
                yield face[index - 1], vertex, mid_pos


def normal_vector_3p(a: Vector, b: Vector, c: Vector) -> Vector:
    """ Returns normal vector for 3 points, which is the normalized cross product for: :code:`a->b x a->c`.

    .. versionadded:: 0.11

    """
    return (b - a).cross(c - a).normalize()


def _determinant(v1, v2, v3) -> float:
    """ Returns determinant. """
    e11, e12, e13 = v1
    e21, e22, e23 = v2
    e31, e32, e33 = v3

    return e11 * e22 * e33 + e12 * e23 * e31 + \
           e13 * e21 * e32 - e13 * e22 * e31 - \
           e11 * e23 * e32 - e12 * e21 * e33


def intersection_ray_ray_3d(ray1: Tuple[Vector, Vector], ray2: Tuple[Vector, Vector], abs_tol=1e-10) -> Sequence[
    Vector]:
    """
    Calculate intersection of two rays, returns a 0-tuple for parallel rays, a 1-tuple for intersecting rays and a
    2-tuple for not intersecting and not parallel rays with points of closest approach on each ray.

    Args:
        ray1: first ray as tuple of two points on the ray as :class:`Vector` objects
        ray2: second ray as tuple of two points on the ray as :class:`Vector` objects
        abs_tol: absolute tolerance for comparisons

    .. versionadded:: 0.11

    """
    # source: http://www.realtimerendering.com/intersections.html#I304
    o1, p1 = ray1
    d1 = (p1 - o1).normalize()
    o2, p2 = ray2
    d2 = (p2 - o2).normalize()
    d1xd2 = d1.cross(d2)
    denominator = d1xd2.magnitude_square
    if math.isclose(denominator, 0., abs_tol=abs_tol):
        # ray1 is parallel to ray2
        return tuple()
    else:
        o2_o1 = o2 - o1
        det1 = _determinant(o2_o1, d2, d1xd2)
        det2 = _determinant(o2_o1, d1, d1xd2)
        p1 = o1 + d1 * (det1 / denominator)
        p2 = o2 + d2 * (det2 / denominator)
        if p1.isclose(p2, abs_tol=abs_tol):
            # ray1 and ray2 have an intersection point
            return p1,
        else:
            # ray1 and ray2 do not have an intersection point,
            # p1 and p2 are the points of closest approach on each ray
            return p1, p2


class Plane:
    """ Represents a plane in 3D space as normal vector and the perpendicular distance from origin.

    .. versionadded:: 0.11

    """
    __slots__ = ('_normal', '_distance_from_origin')

    def __init__(self, normal: Vector, distance: float):
        self._normal = normal
        # the (perpendicular) distance of the plane from (0, 0, 0)
        self._distance_from_origin = distance

    @property
    def normal(self) -> Vector:
        """ Normal vector of the plane. """
        return self._normal

    @property
    def distance_from_origin(self) -> float:
        """ The (perpendicular) distance of the plane from origin (0, 0, 0). """
        return self._distance_from_origin

    @property
    def vector(self) -> Vector:
        """ Returns the location vector. """
        return self._normal * self._distance_from_origin

    @classmethod
    def from_3p(cls, a: Vector, b: Vector, c: Vector) -> 'Plane':
        """ Returns a new plane from 3 points in space. """
        n = (b - a).cross(c - a).normalize()
        return Plane(n, n.dot(a))

    @classmethod
    def from_vector(cls, vector) -> 'Plane':
        """ Returns a new plane from a location vector. """
        v = Vector(vector)
        return Plane(v.normalize(), v.magnitude)

    def __copy__(self) -> 'Plane':
        """ Returns a copy of the plane. """
        return self.__class__(self._normal, self._distance_from_origin)

    copy = __copy__

    def __repr__(self):
        return f'Plane({repr(self._normal)}, {self._distance_from_origin})'

    def __eq__(self, other: 'Plane'):
        if isinstance(other, Plane):
            return self.vector == other.vector
        else:
            raise TypeError

    def signed_distance_to(self, v: Vector) -> float:
        """ Returns signed distance of vertex `v` to plane, if distance is > 0, `v` is in 'front' of plane, in direction
        of the normal vector, if distance is < 0, `v` is at the 'back' of the plane, in the opposite direction of
        the normal vector.

        """
        return self._normal.dot(v) - self._distance_from_origin

    def distance_to(self, v: Vector) -> float:
        """ Returns absolute (unsigned) distance of vertex `v` to plane. """
        return math.fabs(self.signed_distance_to(v))

    def is_coplanar_vertex(self, v: Vector, abs_tol=1e-9) -> bool:
        """ Returns ``True`` if vertex `v` is coplanar, distance from plane to vertex `v` is 0. """
        return self.distance_to(v) < abs_tol

    def is_coplanar_plane(self, p: 'Plane', abs_tol=1e-9) -> bool:
        """ Returns ``True`` if plane `p` is coplanar, normal vectors in same or opposite direction. """
        n_is_close = self._normal.isclose
        return n_is_close(p._normal, abs_tol) or n_is_close(-p._normal, abs_tol)
