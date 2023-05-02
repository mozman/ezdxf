#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable
import numpy as np
from ezdxf.math import BoundingBox2d, Matrix44, Vec2, Vec3
from ezdxf.path import AbstractPath, Path2d, Command

__all__ = ["NumpyPath2d", "NumpyPolyline2d"]


class _NumpyShape2d:
    """This is an optimization to store many 2D paths and polylines in a compact way
    without sacrificing basic functions like transformation and bounding box calculation.
    """

    _vertices: np.ndarray

    def bbox(self) -> BoundingBox2d:
        """Returns the 2d bounding box of the shape vertices."""
        if len(self._vertices) == 0:
            return BoundingBox2d()
        return BoundingBox2d((self._vertices.min(0), self._vertices.max(0)))

    def transform_inplace(self, m: Matrix44 | np.ndarray) -> None:
        """Transforms the vertices of the shape inplace."""
        v = self._vertices
        if len(v) == 0:
            return
        if isinstance(m, Matrix44):
            m = np.array(m.get_2d_transformation(), dtype=np.double)
            m.shape = (3, 3)
        v = np.matmul(np.concatenate((v, np.ones((v.shape[0], 1))), axis=1), m)
        self._vertices = v[:, :-1]

    def vertices(self) -> list[Vec2]:
        """Returns the shape vertices as list of :class:`Vec2`."""
        return Vec2.list(self._vertices)


class NumpyPolyline2d(_NumpyShape2d):
    """Represents a 2D Polyline, the polyline vertices are stored as a numpy array.
    Optimized for compactness not for speed.
    """

    def __init__(self, polyline: Iterable[Vec2 | Vec3]):
        self._vertices = np.array(Vec2.list(polyline), dtype=np.double)

    def __len__(self):
        return len(self._vertices)


class NumpyPath2d(_NumpyShape2d):
    """Represents a 2D path, the path control vertices  and commands are stored as
    numpy arrays. Optimized for compactness not for speed.
    """

    def __init__(self, path: AbstractPath):
        self._vertices = np.array(Vec2.list(path.control_vertices()), dtype=np.double)
        self._commands = np.array(path.command_codes(), dtype=np.int8)

    def __len__(self):
        return len(self._commands)

    def to_path2d(self) -> Path2d:
        v = self._vertices
        if len(v) == 0:
            return Path2d()
        path = Path2d(v[0])
        index = 1
        for command in self._commands:
            if command == Command.MOVE_TO:
                path.move_to(v[index])
                index += 1
            elif command == Command.LINE_TO:
                path.line_to(v[index])
                index += 1
            elif command == Command.CURVE3_TO:
                path.curve3_to(v[index + 1], v[index])
                index += 2
            elif command == Command.CURVE4_TO:
                path.curve4_to(v[index + 2], v[index], v[index + 1])
                index += 3
            else:
                raise ValueError(f"invalid command: {command}")
        return path
