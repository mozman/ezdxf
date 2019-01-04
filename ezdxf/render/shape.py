# Created: 2019-01-04
# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import math
from ezdxf.algebra import Vector
from typing import Union, Sequence, Iterable, List
Vertex = Union[Vector, Sequence[float]]


class Shape:
    """
    Geometry object as vertices list which can be moved, rotated and scaled.

    """
    def __init__(self, vertices: Iterable[Vertex]):
        self.vertices = Vector.list(vertices)  # type: List[Vector]

    def translate(self, vector: Vertex) -> None:
        self.vertices = [v + vector for v in self.vertices]

    def scale(self, sx: float = 1., sy: float = 1., sz: float = 1.) -> None:
        def _scale(x: float, y: float, z: float) -> Vector:
            return Vector(x * sx, y * sy, z * sz)

        self.vertices = [_scale(*v.xyz) for v in self.vertices]

    def scale_uniform(self, scale: float) -> None:
        self.vertices = [v * scale for v in self.vertices]

    def rotate(self, angle: float, center: Vector = None) -> None:
        self.rotate_rad(math.radians(angle), center)

    def rotate_rad(self, angle: float, center: Vector = None) -> None:
        if center is not None:
            self.translate(-center)  # faster than a Matrix44 multiplication
        self.vertices = [v.rot_z_rad(angle) for v in self.vertices]
        if center is not None:
            self.translate(center)  # faster than a Matrix44 multiplication

