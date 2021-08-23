# Copyright (c) 2019-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Tuple, Optional, List, Iterator
import abc

from ezdxf.math import Vec3, Vec2

if TYPE_CHECKING:
    from ezdxf.math import Vertex, AnyVec

__all__ = ["BoundingBox2d", "BoundingBox"]


class AbstractBoundingBox:
    __slots__ = ("extmin", "extmax")

    def __init__(self, vertices: Iterable["Vertex"] = None):
        self.extmax: Optional["AnyVec"] = None
        self.extmin: Optional["AnyVec"] = None
        if vertices is not None:
            try:
                self.extmin, self.extmax = self.extends_detector(vertices)
            except ValueError:
                # No or invalid data creates an empty BoundingBox
                pass

    def __str__(self) -> str:
        return f"[{self.extmin}, {self.extmax}]"

    def __repr__(self) -> str:
        name = self.__class__.__name__
        if self.has_data:
            return f"{name}({self.__str__()})"
        else:
            return f"{name}()"

    def __iter__(self) -> Iterator["AnyVec"]:
        if self.has_data:
            yield self.extmin
            yield self.extmax

    @abc.abstractmethod
    def extends_detector(
        self, vertices: Iterable["Vertex"]
    ) -> Tuple["AnyVec", "AnyVec"]:
        pass

    @abc.abstractmethod
    def inside(self, vertex: "Vertex") -> bool:
        pass

    @abc.abstractmethod
    def intersect(self, other: "AbstractBoundingBox") -> bool:
        pass

    def any_inside(self, vertices: Iterable["Vertex"]) -> bool:
        """Returns ``True`` if any vertex is inside this bounding box.

        Vertices at the box border are inside!
        """
        if self.has_data:
            return any(self.inside(v) for v in vertices)
        return False

    def all_inside(self, vertices: Iterable["Vertex"]) -> bool:
        """Returns ``True`` if all vertices are inside this bounding box.

        Vertices at the box border are inside!
        """
        if self.has_data:
            # all() returns True for an empty set of vertices
            has_any = False
            for v in vertices:
                has_any = True
                if not self.inside(v):
                    return False
            return has_any
        return False

    @property
    def has_data(self) -> bool:
        """Returns ``True`` if bonding box is not empty"""
        return self.extmin is not None

    @property
    def is_empty(self) -> bool:
        """Returns ``True`` if bonding box is empty"""
        return self.extmin is None

    @property
    def size(self):
        """Returns size of bounding box."""
        return self.extmax - self.extmin

    @property
    def center(self):
        """Returns center of bounding box."""
        return self.extmin.lerp(self.extmax)

    def extend(self, vertices: Iterable["Vertex"]) -> None:
        """Extend bounds by `vertices`.

        Args:
            vertices: iterable of Vertex objects

        """
        v = list(vertices)
        if not v:
            return
        if self.has_data:
            v.extend([self.extmin, self.extmax])
        self.extmin, self.extmax = self.extends_detector(v)

    def union(self, other: "AbstractBoundingBox"):
        """Returns a new bounding box as union of this and `other` bounding
        box.
        """
        vertices: List["AnyVec"] = []
        if self.has_data:
            vertices.extend(self)
        if other.has_data:
            vertices.extend(other)
        return self.__class__(vertices)

    def rect_vertices(self) -> Tuple[Vec2, ...]:
        """Returns the corners of the bounding box in the xy-plane as
        :class:`Vec2` objects.
        """
        if self.has_data:  # extmin is not None!
            x0, y0, *_ = self.extmin  # type: ignore
            x1, y1, *_ = self.extmax  # type: ignore
            return Vec2(x0, y0), Vec2(x1, y0), Vec2(x1, y1), Vec2(x0, y1)
        else:
            raise ValueError("empty bounding box")


class BoundingBox(AbstractBoundingBox):
    """3D bounding box.

    Args:
        vertices: iterable of ``(x, y, z)`` tuples or :class:`Vec3` objects

    """

    def extends_detector(
        self, vertices: Iterable["Vertex"]
    ) -> Tuple[Vec3, Vec3]:
        return extends3d(vertices)

    def inside(self, vertex: "Vertex") -> bool:
        """Returns ``True`` if `vertex` is inside this bounding box.

        Vertices at the box border are inside!
        """
        if self.extmin is None or self.extmax is None:
            return False
        x, y, z = Vec3(vertex).xyz
        xmin, ymin, zmin = self.extmin.xyz
        xmax, ymax, zmax = self.extmax.xyz
        return (
            (xmin <= x <= xmax) and (ymin <= y <= ymax) and (zmin <= z <= zmax)
        )

    def intersect(self, other: "AbstractBoundingBox") -> bool:
        """Returns `True` if this bounding box intersects with `other`.

        Touching bounding boxes do not intersect!

        """
        # Source: https://gamemath.com/book/geomtests.html#intersection_two_aabbs
        # Check for a separating axis:
        if (
            self.extmin is None
            or self.extmax is None
            or other.extmin is None
            or other.extmax is None
        ):
            return False

        # Check for a separating axis:
        if self.extmin.x >= other.extmax.x:
            return False
        if self.extmax.x <= other.extmin.x:
            return False
        if self.extmin.y >= other.extmax.y:
            return False
        if self.extmax.y <= other.extmin.y:
            return False
        if self.extmin.z >= other.extmax.z:
            return False
        if self.extmax.z <= other.extmin.z:
            return False
        return True

    def cube_vertices(self) -> Tuple[Vec3, ...]:
        """Returns the 3D corners of the bounding box as :class:`Vec3` objects."""
        if self.extmin is not None and self.extmax is not None:
            x0, y0, z0 = self.extmin
            x1, y1, z1 = self.extmax
            return (
                Vec3(x0, y0, z0),
                Vec3(x1, y0, z0),
                Vec3(x1, y1, z0),
                Vec3(x0, y1, z0),
                Vec3(x0, y0, z1),
                Vec3(x1, y0, z1),
                Vec3(x1, y1, z1),
                Vec3(x0, y1, z1),
            )
        else:
            raise ValueError("empty bounding box")


class BoundingBox2d(AbstractBoundingBox):
    """Optimized 2D bounding box.

    Args:
        vertices: iterable of ``(x, y[, z])`` tuples or :class:`Vec3` objects

    """

    def extends_detector(
        self, vertices: Iterable["Vertex"]
    ) -> Tuple[Vec2, Vec2]:
        return extends2d(vertices)

    def inside(self, vertex: "Vertex") -> bool:
        """Returns ``True`` if `vertex` is inside this bounding box.

        Vertices at the box border are inside!
        """
        if self.extmin is None or self.extmax is None:
            return False
        v = Vec2(vertex)
        min_ = self.extmin
        max_ = self.extmax
        return (min_.x <= v.x <= max_.x) and (min_.y <= v.y <= max_.y)

    def intersect(self, other: "AbstractBoundingBox") -> bool:
        """Returns `True` if this bounding box intersects with `other`.

        Touching bounding boxes do not intersect!

        """
        # Source: https://gamemath.com/book/geomtests.html#intersection_two_aabbs
        if (
            self.extmin is None
            or self.extmax is None
            or other.extmin is None
            or other.extmax is None
        ):
            return False
        # Check for a separating axis:
        if self.extmin.x >= other.extmax.x:
            return False
        if self.extmax.x <= other.extmin.x:
            return False
        if self.extmin.y >= other.extmax.y:
            return False
        if self.extmax.y <= other.extmin.y:
            return False
        return True


def extends3d(vertices: Iterable["Vertex"]) -> Tuple[Vec3, Vec3]:
    minx, miny, minz = None, None, None
    maxx, maxy, maxz = None, None, None
    for v in vertices:
        v = Vec3(v)
        if minx is None:
            minx, miny, minz = v.xyz  # type: ignore
            maxx, maxy, maxz = v.xyz  # type: ignore
        else:
            x, y, z = v.xyz
            if x < minx:
                minx = x
            elif x > maxx:
                maxx = x
            if y < miny:
                miny = y
            elif y > maxy:
                maxy = y
            if z < minz:
                minz = z
            elif z > maxz:
                maxz = z
    if minx is None:
        raise ValueError("No vertices give.")
    return Vec3(minx, miny, minz), Vec3(maxx, maxy, maxz)


def extends2d(vertices: Iterable["Vertex"]) -> Tuple[Vec2, Vec2]:
    minx, miny = None, None
    maxx, maxy = None, None
    for v in vertices:
        v = Vec2(v)
        x, y = v.x, v.y  # type: ignore
        if minx is None:
            minx = x
            maxx = x
            miny = y
            maxy = y
        else:
            if x < minx:
                minx = x
            elif x > maxx:
                maxx = x
            if y < miny:
                miny = y
            elif y > maxy:
                maxy = y
    if minx is None:
        raise ValueError("No vertices give.")
    return Vec2(minx, miny), Vec2(maxx, maxy)
