#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Optional, Iterator
from typing_extensions import Self
import abc

import numpy as np
from ezdxf.math import (
    Matrix44,
    Vec2,
    UVec,
    has_clockwise_orientation,
    Bezier3P,
    Bezier4P,
)
from ezdxf.path import AbstractPath, Path2d, Command

__all__ = ["NumpyPath2d", "NumpyPoints2d", "NumpyShapesException", "EmptyShapeError"]


class NumpyShapesException(Exception):
    pass


class EmptyShapeError(NumpyShapesException):
    pass


class NumpyShape2d(abc.ABC):
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


class NumpyPoints2d(NumpyShape2d):
    """Represents an array of 2D points stored as a ndarray."""

    def __init__(self, points: Iterable[UVec]) -> None:
        self._vertices = np.array(Vec2.list(points), dtype=np.float64)

    def __len__(self) -> int:
        return len(self._vertices)


NO_VERTICES = np.array([], dtype=np.float64)
NO_COMMANDS = np.array([], dtype=np.int8)


class NumpyPath2d(NumpyShape2d):
    """Represents a 2D path, the path control vertices and commands are stored as ndarray."""

    def __init__(self, path: Optional[AbstractPath]) -> None:
        if path is None:
            self._vertices = NO_VERTICES
            self._commands = NO_COMMANDS
            return
        if isinstance(path, Path2d):
            vertices = path.control_vertices()
        else:
            vertices = Vec2.list(path.control_vertices())
        if len(vertices) == 0:
            try:  # control_vertices() does not return start point of empty paths
                vertices = [path.start]
            except IndexError:
                vertices = [Vec2()]  # default start point of empty paths
        self._vertices = np.array(vertices, dtype=np.float64)
        self._commands = np.array(path.command_codes(), dtype=np.int8)

    # SupportsControlVertices protocol for ezdxf.path.nesting
    def __len__(self) -> int:
        return len(self._commands)

    @property
    def start(self) -> Vec2:
        """Returns the start point as :class:`~ezdxf.math.Vec2` instance."""
        return Vec2(self._vertices[0])

    @property
    def end(self) -> Vec2:
        """Returns the end point as :class:`~ezdxf.math.Vec2` instance."""
        return Vec2(self._vertices[-1])

    # SupportsControlVertices protocol for ezdxf.path.nesting
    def control_vertices(self) -> list[Vec2]:
        return self.vertices()

    def __copy__(self) -> Self:
        clone = self.__class__(None)
        clone._commands = self._commands.copy()
        clone._vertices = self._vertices.copy()
        return clone

    clone = __copy__

    def to_path2d(self) -> Path2d:
        """Returns a new :class:`Path2d` instance."""
        vertices = [Vec2(v) for v in self._vertices]
        commands = [Command(c) for c in self._commands]
        return Path2d.from_vertices_and_commands(vertices, commands)

    @property
    def has_sub_paths(self) -> bool:
        """Returns ``True`` if the path is a :term:`Multi-Path` object that
        contains multiple sub-paths.

        """
        return Command.MOVE_TO in self._commands

    def has_clockwise_orientation(self) -> bool:
        """Returns ``True`` if 2D path has clockwise orientation.

        Raises:
            TypeError: can't detect orientation of a :term:`Multi-Path` object

        """
        if self.has_sub_paths:
            raise TypeError("can't detect orientation of a multi-path object")
        return has_clockwise_orientation(self.vertices())

    def reverse(self) -> Self:
        """Reverse path orientation inplace."""
        commands = self._commands
        if not len(self._commands):
            return self
        if commands[-1] == Command.MOVE_TO:
            # The last move_to will become the first move_to.
            # A move_to as first command just moves the start point and can be
            # removed!
            # There are never two consecutive MOVE_TO commands in a Path!
            self._commands = np.flip(commands[:-1])
            self._vertices = np.flip(self._vertices[:-1, ...], axis=0)
        else:
            self._commands = np.flip(commands)
            self._vertices = np.flip(self._vertices, axis=0)
        return self

    def clockwise(self) -> Self:
        """Apply clockwise orientation inplace.

        Raises:
            TypeError: can't detect orientation of a :term:`Multi-Path` object

        """
        if not self.has_clockwise_orientation():
            self.reverse()
        return self

    def counter_clockwise(self) -> Self:
        """Apply counter-clockwise orientation inplace.

        Raises:
            TypeError: can't detect orientation of a :term:`Multi-Path` object

        """

        if self.has_clockwise_orientation():
            self.reverse()
        return self

    def flattening(self, distance: float, segments: int = 4) -> Iterator[Vec2]:
        """Flatten path to vertices as :class:`Vec2` instances."""
        if not len(self._commands):
            return

        vertices = self.vertices()
        start = vertices[0]
        yield start
        index = 1
        for cmd in self._commands:
            if cmd == Command.LINE_TO or cmd == Command.MOVE_TO:
                end_location = vertices[index]
                index += 1
                yield end_location
            elif cmd == Command.CURVE3_TO:
                ctrl, end_location = vertices[index: index+2]
                index += 2
                pts = Vec2.generate(
                    Bezier3P((start, ctrl, end_location)).flattening(distance, segments)
                )
                next(pts)  # skip first vertex
                yield from pts
            elif cmd == Command.CURVE4_TO:
                ctrl1, ctrl2, end_location = vertices[index:index+3]
                index += 3
                pts = Vec2.generate(
                    Bezier4P((start, ctrl1, ctrl2, end_location)).flattening(
                        distance, segments
                    )
                )
                next(pts)  # skip first vertex
                yield from pts
            else:
                raise ValueError(f"Invalid command: {cmd}")
            start = end_location
