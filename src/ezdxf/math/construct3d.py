# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Sequence, List, Iterable, Union, Tuple
from enum import IntEnum
import math
from ezdxf.math import Vec3, Vec2


class LocationState(IntEnum):
    COPLANAR = 0  # all the vertices are within the plane
    FRONT = 1  # all the vertices are in front of the plane
    BACK = 2  # all the vertices are at the back of the plane
    SPANNING = 3  # some vertices are in front, some in the back


def is_planar_face(face: Sequence[Vec3], abs_tol=1e-9) -> bool:
    """ Returns ``True`` if sequence of vectors is a planar face.

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
        a, b, c = face[index:index + 3]
        normal = (b - a).cross(c - b).normalize()
        if first_normal is None:
            first_normal = normal
        elif not first_normal.isclose(normal, abs_tol):
            return False
    return True


def subdivide_face(face: Sequence[Union[Vec3, Vec2]], quads=True) -> Iterable[
    List[Vec3]]:
    """ Yields new subdivided faces. Creates new faces from subdivided edges and the face midpoint by linear
    interpolation.

    Args:
        face: a sequence of vertices, :class:`Vec2` and :class:`Vec3` objects supported.
        quads: create quad faces if ``True`` else create triangles

    """
    if len(face) < 3:
        raise ValueError('3 or more vertices required.')
    len_face = len(face)
    mid_pos = Vec3.sum(face) / len_face
    subdiv_location = [face[i].lerp(face[(i + 1) % len_face]) for i in
                       range(len_face)]

    for index, vertex in enumerate(face):
        if quads:
            yield vertex, subdiv_location[index], mid_pos, subdiv_location[
                index - 1]
        else:
            yield subdiv_location[index - 1], vertex, mid_pos
            yield vertex, subdiv_location[index], mid_pos


def subdivide_ngons(faces: Iterable[Sequence[Union[Vec3, Vec2]]]) -> Iterable[
    List[Vec3]]:
    """ Yields only triangles or quad faces, subdivides ngons into triangles.

    Args:
        faces: iterable of faces as sequence of :class:`Vec2` and
            :class:`Vec3` objects

    """
    for face in faces:
        if len(face) < 5:
            yield face
        else:
            mid_pos = Vec3.sum(face) / len(face)
            for index, vertex in enumerate(face):
                yield face[index - 1], vertex, mid_pos


def normal_vector_3p(a: Vec3, b: Vec3, c: Vec3) -> Vec3:
    """ Returns normal vector for 3 points, which is the normalized cross
    product for: :code:`a->b x a->c`.
    """
    return (b - a).cross(c - a).normalize()


def distance_point_line_3d(point: Vec3, start: Vec3, end: Vec3) -> float:
    """ Returns the normal distance from `point` to 3D line defined by `start-`
    and `end` point.
    """
    if start.isclose(end):
        raise ZeroDivisionError('Not a line.')
    v1 = point - start
    # point projected onto line start to end:
    v2 = (end - start).project(v1)
    # Pythagoras:
    return math.sqrt(v1.magnitude_square - v2.magnitude_square)


class Plane:
    """ Represents a plane in 3D space as normal vector and the perpendicular
    distance from origin.
    """
    __slots__ = ('_normal', '_distance_from_origin')

    def __init__(self, normal: Vec3, distance: float):
        self._normal = normal
        # the (perpendicular) distance of the plane from (0, 0, 0)
        self._distance_from_origin = distance

    @property
    def normal(self) -> Vec3:
        """ Normal vector of the plane. """
        return self._normal

    @property
    def distance_from_origin(self) -> float:
        """ The (perpendicular) distance of the plane from origin (0, 0, 0). """
        return self._distance_from_origin

    @property
    def vector(self) -> Vec3:
        """ Returns the location vector. """
        return self._normal * self._distance_from_origin

    @classmethod
    def from_3p(cls, a: Vec3, b: Vec3, c: Vec3) -> 'Plane':
        """ Returns a new plane from 3 points in space. """
        n = (b - a).cross(c - a).normalize()
        return Plane(n, n.dot(a))

    @classmethod
    def from_vector(cls, vector) -> 'Plane':
        """ Returns a new plane from a location vector. """
        v = Vec3(vector)
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

    def signed_distance_to(self, v: Vec3) -> float:
        """ Returns signed distance of vertex `v` to plane, if distance is > 0, `v` is in 'front' of plane, in direction
        of the normal vector, if distance is < 0, `v` is at the 'back' of the plane, in the opposite direction of
        the normal vector.

        """
        return self._normal.dot(v) - self._distance_from_origin

    def distance_to(self, v: Vec3) -> float:
        """ Returns absolute (unsigned) distance of vertex `v` to plane. """
        return math.fabs(self.signed_distance_to(v))

    def is_coplanar_vertex(self, v: Vec3, abs_tol=1e-9) -> bool:
        """ Returns ``True`` if vertex `v` is coplanar, distance from plane to vertex `v` is 0. """
        return self.distance_to(v) < abs_tol

    def is_coplanar_plane(self, p: 'Plane', abs_tol=1e-9) -> bool:
        """ Returns ``True`` if plane `p` is coplanar, normal vectors in same or opposite direction. """
        n_is_close = self._normal.isclose
        return n_is_close(p._normal, abs_tol) or n_is_close(-p._normal, abs_tol)
