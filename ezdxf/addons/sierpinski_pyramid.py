# Author:  mozman <me@mozman.at>
# Purpose: sierpinski pyramid
# module belongs to package ezdxf
# Created: 07.12.2016
# License: MIT License

import math
from .mesh import Mesh, OptimizedMesh

HEIGHT4 = 1. / math.sqrt(2.)  # pyramid4 height (* length)
HEIGHT3 = math.sqrt(6.) / 3.  # pyramid3 height (* length)

DY1_FACTOR = math.tan(math.pi/6.) / 2.  # inner circle radius
DY2_FACTOR = 0.5 / math.cos(math.pi/6.)  # outer circle radius


class SierpinskyPyramid:
    def __init__(self, location=(0., 0., 0.), length=1., level=1, sides=4):
        self.sides = sides
        self.pyramids = sierpinsky_pyramid(location=location, length=length, level=level, sides=sides)

    def vertices(self):
        for location, length in self.pyramids:
            yield self._calc_vertices(location, length)
    __iter__ = vertices

    def _calc_vertices(self, location, length):
        len2 = length / 2.
        x, y, z = location
        if self.sides == 4:
            return [
                (x-len2, y-len2, z),
                (x+len2, y-len2, z),
                (x+len2, y+len2, z),
                (x-len2, y+len2, z),
                (x, y, z + length * HEIGHT4)
            ]
        elif self.sides == 3:
            dy1 = length * DY1_FACTOR
            dy2 = length * DY2_FACTOR
            return [
                (x-len2, y-dy1, z),
                (x+len2, y-dy1, z),
                (x, y+dy2, z),
                (x, y, z + length * HEIGHT3)
            ]
        else:
            raise ValueError("sides has to be 3 or 4.")

    def faces(self):
        if self.sides == 4:
            return [
                (0, 1, 2, 3),
                (0, 1, 4),
                (1, 2, 4),
                (2, 3, 4),
                (3, 0, 4)
            ]
        elif self.sides == 3:
            return [
                (0, 1, 2),
                (0, 1, 3),
                (1, 2, 3),
                (2, 0, 3)
            ]
        else:
            raise ValueError("sides has to be 3 or 4.")

    def render(self, layout, merge=False, dxfattribs=None):
        faces = self.faces()  # all pyramid faces have the same vertex order
        if merge:
            mesh = OptimizedMesh()
            for vertices in self:
                mesh.add_mesh(vertices, faces)
            mesh.render(layout, dxfattribs)
        else:
            for vertices in self:  # iterate over all pyramids
                mesh = Mesh()
                mesh.add_mesh(vertices, faces)
                mesh.render(layout, dxfattribs)


def sierpinsky_pyramid(location=(0., 0., 0.), length=1., level=1, sides=4):
    """ Build a Sierpinski pyramid.

    Args:
        location: base center point of the pyramid
        length: base length of the pyramid
        level: recursive building levels, has to 1 ot bigger
        sides: 3 or 4 sided pyramids supported

    Returns: list of pyramid vertices

    """
    level = int(level)
    if level < 1:
        raise ValueError("level has to be 1 or bigger.")
    pyramids = _sierpinsky_pyramid(location, length, sides)
    for _ in range(level-1):
        next_level_pyramids = []
        for location, length in pyramids:
            next_level_pyramids.extend(_sierpinsky_pyramid(location, length, sides))
        pyramids = next_level_pyramids
    return pyramids


def _sierpinsky_pyramid(location=(0., 0., 0.), length=1., sides=4):
    if sides == 3:
        return sierpinsky_pyramid_3(location, length)
    elif sides == 4:
        return sierpinsky_pyramid_4(location, length)
    else:
        raise ValueError("sides has to be 3 or 4.")


def sierpinsky_pyramid_4(location=(0., 0., 0.), length=1.):
    """ Build a 4-sided Sierpinski pyramid. Pyramid height = length of the base square!

    Args:
        location: base center point of the pyramid
        length: base length of the pyramid

    Returns: list of (location, length) tuples, representing the sierpinski pyramid

    """
    len2 = length / 2
    len4 = length / 4
    x, y, z = location
    return [
        ((x-len4, y-len4, z), len2),
        ((x+len4, y-len4, z), len2),
        ((x-len4, y+len4, z), len2),
        ((x+len4, y+len4, z), len2),
        ((x, y, z + len2 * HEIGHT4), len2)
    ]


def sierpinsky_pyramid_3(location=(0., 0., 0.), length=1.):
    """ Build a 3-sided Sierpinski pyramid (tetraeder).

    Args:
        location: base center point of the pyramid
        length: base length of the pyramid

    Returns: list of (location, length) tuples, representing the sierpinski pyramid

    """
    dy1 = length * DY1_FACTOR * 0.5
    dy2 = length * DY2_FACTOR * 0.5
    len2 = length / 2
    len4 = length / 4
    x, y, z = location
    return [
        ((x-len4, y-dy1, z), len2),
        ((x+len4, y-dy1, z), len2),
        ((x, y+dy2, z), len2),
        ((x, y, z + len2 * HEIGHT3), len2)
    ]
