# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

from typing import TYPE_CHECKING
from .vector import Vector

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


class Matrix33:
    """ Simple 3x3 Matrix """
    # faster transformation than Matrix44
    __slots__ = ('ux', 'uy', 'uz')

    def __init__(self, ux: 'Vertex' = (1, 0, 0), uy: 'Vertex' = (0, 1, 0), uz: 'Vertex' = (0, 0, 1)):
        self.ux = Vector(ux)
        self.uy = Vector(uy)
        self.uz = Vector(uz)

    def transpose(self) -> 'Matrix33':
        return Matrix33(
            (self.ux.x, self.uy.x, self.uz.x),
            (self.ux.y, self.uy.y, self.uz.y),
            (self.ux.z, self.uy.z, self.uz.z),
        )

    def transform(self, vector: 'Vertex') -> Vector:
        px, py, pz = Vector(vector)
        ux = self.ux
        uy = self.uy
        uz = self.uz
        x = px * ux.x + py * uy.x + pz * uz.x
        y = px * ux.y + py * uy.y + pz * uz.y
        z = px * ux.z + py * uy.z + pz * uz.z
        return Vector(x, y, z)

    def determinant(self) -> float:
        """ Returns determinant. """
        e11, e12, e13 = self.ux
        e21, e22, e23 = self.uy
        e31, e32, e33 = self.uz

        return e11 * e22 * e33 + e12 * e23 * e31 + \
               e13 * e21 * e32 - e13 * e22 * e31 - \
               e11 * e23 * e32 - e12 * e21 * e33
