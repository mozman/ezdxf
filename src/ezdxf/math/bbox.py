# Created: 27.01.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Tuple
from .vector import Vector, Vec2

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


class BoundingBox:
    """ 3D bounding box.

    Args:
        vertices: iterable of ``(x, y, z)`` tuples or :class:`Vector` objects

    """

    def __init__(self, vertices: Iterable['Vertex'] = None):
        if vertices is None:
            self.extmax = None
            self.extmin = None
        else:
            self.extmin, self.extmax = extends(vertices)

    @property
    def has_data(self) -> bool:
        """ Returns ``True`` if data is available """
        return self.extmin is not None

    def inside(self, vertex: 'Vertex') -> bool:
        """ Returns ``True`` if `vertex` is inside bounding box. """
        x, y, z = Vector(vertex).xyz
        xmin, ymin, zmin = self.extmin.xyz
        xmax, ymax, zmax = self.extmax.xyz
        return (xmin <= x <= xmax) and (ymin <= y <= ymax) and (zmin <= z <= zmax)

    def extend(self, vertices: Iterable['Vertex']) -> None:
        """ Extend bounds by `vertices`.

        Args:
            vertices: iterable of ``(x, y, z)`` tuples or :class:`Vector` objects

        """
        v = list(vertices)
        if self.has_data:
            v.extend([self.extmin, self.extmax])
        self.extmin, self.extmax = extends(v)

    @property
    def size(self) -> Vector:
        """ Returns size of bounding box. """
        return self.extmax - self.extmin

    @property
    def center(self) -> Vector:
        """ Returns center of bounding box. """
        return self.extmin.lerp(self.extmax)


def extends(vertices: Iterable['Vertex']) -> Tuple[Vector, Vector]:
    minx, miny, minz = None, None, None
    maxx, maxy, maxz = None, None, None
    for v in vertices:
        v = Vector(v)
        if minx is None:
            minx, miny, minz = v.xyz
            maxx, maxy, maxz = v.xyz
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
    return Vector(minx, miny, minz), Vector(maxx, maxy, maxz)


class BoundingBox2d:
    """ Optimized 2D bounding box.

    Args:
        vertices: iterable of ``(x, y[, z])`` tuples or :class:`Vector` objects

    """

    def __init__(self, vertices: Iterable['Vertex'] = None):
        if vertices is None:
            self.extmax = None
            self.extmin = None
        else:
            self.extmin, self.extmax = extends2d(vertices)

    @property
    def has_data(self) -> bool:
        """ Returns ``True`` if data is available """
        return self.extmin is not None

    def inside(self, vertex: 'Vertex') -> bool:
        """ Returns ``True`` if `vertex` is inside bounding box. """
        v = Vec2(vertex)
        min_ = self.extmin
        max_ = self.extmax
        return (min_.x <= v.x <= max_.x) and (min_.y <= v.y <= max_.y)

    def extend(self, vertices: Iterable['Vertex']) -> None:
        """ Extend bounds by `vertices`.

        Args:
            vertices: iterable of ``(x, y[, z])`` tuples or :class:`Vector` objects

        """
        v = list(vertices)
        if self.has_data:
            v.extend([self.extmin, self.extmax])
        self.extmin, self.extmax = extends2d(v)

    @property
    def size(self) -> Vec2:
        """ Returns size of bounding box. """
        return self.extmax - self.extmin

    @property
    def center(self) -> Vec2:
        """ Returns center of bounding box. """
        return self.extmin.lerp(self.extmax)


def extends2d(vertices: Iterable['Vertex']) -> Tuple[Vec2, Vec2]:
    minx, miny = None, None
    maxx, maxy = None, None
    for v in vertices:
        v = Vec2(v)
        x, y = v.x, v.y
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
    return Vec2((minx, miny)), Vec2((maxx, maxy))
