#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable
import abc

import numpy as np
from ezdxf.math import Matrix44, Vec2, UVec
from ezdxf.path import AbstractPath, Path2d, Command

__all__ = ["NumpyPath2d", "NumpyPoints2d", "NumpyShapesException", "EmptyShapeError"]


class NumpyShapesException(Exception):
    pass


class EmptyShapeError(NumpyShapesException):
    pass


class _NumpyShape2d(abc.ABC):
    """This is an optimization to store many 2D paths and polylines in a compact way
    without sacrificing basic functions like transformation and bounding box calculation.
    """

    _vertices: np.ndarray

    def extents(self) -> tuple[Vec2, Vec2]:
        """Returns the extents of the bounding box as tuple (extmin, extmax)."""
        v = self._vertices
        if len(v) > 0:
            return Vec2(v.min(0)), Vec2(v.max(0))
        else:
            raise EmptyShapeError("empty shape has no extends")

    def transform_inplace(self, m: Matrix44) -> None:
        """Transforms the vertices of the shape inplace."""
        v = self._vertices
        if len(v) == 0:
            return
        m.transform_array_inplace(v, 2)

    def vertices(self) -> list[Vec2]:
        """Returns the shape vertices as list of :class:`Vec2`."""
        return Vec2.list(self._vertices)


class NumpyPoints2d(_NumpyShape2d):
    """Represents an array of 2D points stored as a ndarray."""

    def __init__(self, points: Iterable[UVec]) -> None:
        self._vertices = np.array(Vec2.list(points), dtype=np.float64)

    def __len__(self) -> int:
        return len(self._vertices)


class NumpyPath2d(_NumpyShape2d):
    """Represents a 2D path, the path control vertices and commands are stored as ndarray."""

    def __init__(self, path: AbstractPath) -> None:
        vertices = Vec2.list(path.control_vertices())
        if len(vertices) == 0:
            try:  # control_vertices() does not return start point of empty paths
                vertices = [path.start]
            except IndexError:
                vertices = [Vec2()]  # default start point of empty paths
        self._vertices = np.array(vertices, dtype=np.float64)
        self._commands = np.array(path.command_codes(), dtype=np.int8)

    def __len__(self) -> int:
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
