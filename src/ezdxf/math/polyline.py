#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, List, TYPE_CHECKING, Tuple, Iterator, Sequence
from ezdxf.math import Vec3, linspace, NULLVEC
import bisect

if TYPE_CHECKING:
    from ezdxf.math import Vertex

__all__ = ["ConstructionPolyline"]

REL_TOL = 1e-9


class ConstructionPolyline(Sequence):
    """A polyline construction tool to measure, interpolate and divide anything
    that can be approximated or flattened into vertices.
    This is an immutable data structure which supports the :class:`Sequence`
    interface.

    Args:
        vertices: iterable of polyline vertices
        close: ``True`` to close the polyline (first vertex == last vertex)
        rel_tol: relative tolerance for floating point comparisons

    Example to measure or divide a SPLINE entity::

        import ezdxf
        from ezdxf.math import ConstructionPolyline

        doc = ezdxf.readfile("your.dxf")
        msp = doc.modelspace()
        spline = msp.query("SPLINE").first
        if spline is not None:
            polyline = ConstructionPolyline(spline.flattening(0.01))
            print(f"Entity {spline} has an approximated length of {polyline.length}")
            # get dividing points with a distance of 1.0 drawing unit to each other
            points = list(polyline.divide_by_length(1.0))

    """
    def __init__(
        self,
        vertices: Iterable["Vertex"],
        close: bool = False,
        rel_tol: float = REL_TOL,
    ):
        self._rel_tol = float(rel_tol)
        v3list: List[Vec3] = Vec3.list(vertices)
        self._vertices: List[Vec3] = v3list
        if close and len(v3list) > 2:
            if not v3list[0].isclose(v3list[-1], rel_tol=self._rel_tol):
                v3list.append(v3list[0])

        self._distances: List[float] = _distances(v3list)

    def __len__(self) -> int:
        """len(self)"""
        return len(self._vertices)

    def __iter__(self) -> Iterator[Vec3]:
        """iter(self)"""
        return iter(self._vertices)

    def __getitem__(self, item):
        """vertex = self[item]"""
        if isinstance(item, int):
            return self._vertices[item]
        else:  # slice
            return self.__class__(self._vertices[item], rel_tol=self._rel_tol)

    @property
    def length(self) -> float:
        """Returns the overall length of the polyline."""
        if self._distances:
            return self._distances[-1]
        return 0.0

    @property
    def is_closed(self) -> bool:
        """Returns ``True`` if the polyline is closed
        (first vertex == last vertex).
        """
        if len(self._vertices) > 2:
            return self._vertices[0].isclose(
                self._vertices[-1], rel_tol=self._rel_tol
            )
        return False

    def data(self, index: int) -> Tuple[float, float, Vec3]:
        """Returns the tuple (distance from start, distance from previous vertex,
        vertex). All distances measured along the polyline.
        """
        vertices = self._vertices
        if not vertices:
            raise ValueError("empty polyline")
        distances = self._distances

        if index == 0:
            return 0.0, 0.0, vertices[0]
        prev_distance = distances[index - 1]
        current_distance = distances[index]
        vertex = vertices[index]
        return current_distance, current_distance - prev_distance, vertex

    def vertex_at(self, distance: float) -> Vec3:
        """Returns the interpolated vertex at the given `distance` from the
        start of the polyline.
        """
        if distance < 0.0 or distance > self.length:
            raise ValueError("distance out of range")
        if len(self._vertices) < 2:
            raise ValueError("not enough vertices for interpolation")
        return self._vertex_at(distance)

    def _vertex_at(self, distance: float) -> Vec3:
        # fast method without any checks
        vertices = self._vertices
        distances = self._distances
        index1 = bisect.bisect_left(distances, distance)
        if index1 == 0:
            return vertices[0]
        index0 = index1 - 1
        distance1 = distances[index1]
        distance0 = distances[index0]
        # skip coincident vertices:
        while index0 > 0 and distance0 == distance1:
            index0 -= 1
            distance0 = distances[index0]
        if distance0 == distance1:
            raise ArithmeticError("internal interpolation error")

        factor = (distance - distance0) / (distance1 - distance0)
        return vertices[index0].lerp(vertices[index1], factor=factor)

    def divide(self, count: int) -> Iterator[Vec3]:
        """Returns `count` interpolated vertices along the polyline.
        Argument `count` has to be greater than 2 and the start- and end
        vertices are always included.

        """
        if count < 2:
            raise ValueError(f"invalid count: {count}")
        vertex_at = self._vertex_at
        for distance in linspace(0.0, self.length, count):
            yield vertex_at(distance)

    def divide_by_length(
        self, length: float, force_last: bool = False
    ) -> Iterator[Vec3]:
        """Returns interpolated vertices along the polyline. Each vertex has a
        fix distance `length` from its predecessor. Yields the last vertex if
        argument `force_last` is ``True`` even if the last distance is not equal
        to `length`.

        """
        if length <= 0.0:
            raise ValueError(f"invalid length: {length}")
        if len(self._vertices) < 2:
            raise ValueError("not enough vertices for interpolation")

        total_length: float = self.length
        vertex_at = self._vertex_at
        distance: float = 0.0

        vertex: Vec3 = NULLVEC
        while distance <= total_length:
            vertex = vertex_at(distance)
            yield vertex
            distance += length

        if force_last and not vertex.isclose(self._vertices[-1]):
            yield self._vertices[-1]


def _distances(vertices: Iterable[Vec3]) -> List[float]:
    # distance from start vertex of the polyline to the vertex
    current_station: float = 0.0
    distances: List[float] = []
    prev_vertex = Vec3()
    for vertex in vertices:
        if distances:
            distant_vec = vertex - prev_vertex
            current_station += distant_vec.magnitude
            distances.append(current_station)
        else:
            distances.append(current_station)
        prev_vertex = vertex
    return distances
