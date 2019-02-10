# Created: 27.01.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Tuple
from .vector import Vector, Vec2

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


class BoundingBox:
    def __init__(self, p1: 'Vertex', p2: 'Vertex'):
        self.extmin, self.extmax = extends([p1, p2])

    def inside(self, vertex: 'Vertex') -> bool:
        x, y, z = Vector(vertex).xyz
        xmin, ymin, zmin = self.extmin.xyz
        xmax, ymax, zmax = self.extmax.xyz
        return (xmin <= x <= xmax) and (ymin <= y <= ymax) and (zmin <= z <= zmax)

    def extend(self, vertices: Iterable['Vertex']) -> None:
        v = [self.extmin, self.extmax]
        v.extend(vertices)
        self.extmin, self.extmax = extends(v)


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
    def __init__(self, p1: 'Vertex', p2: 'Vertex'):
        self.extmin, self.extmax = extends2d([p1, p2])

    def inside(self, vertex: 'Vertex') -> bool:
        v = Vec2(vertex)
        min_ = self.extmin
        max_ = self.extmax
        return (min_.x <= v.x <= max_.x) and (min_.y <= v.y <= max_.y)

    def extend(self, vertices: Iterable['Vertex']) -> None:
        v = [self.extmin, self.extmax]
        v.extend(vertices)
        self.extmin, self.extmax = extends(v)


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
