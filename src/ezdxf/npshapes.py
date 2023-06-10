#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Optional, Iterator, Sequence
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
    BoundingBox2d,
)
from ezdxf.path import AbstractPath, Path2d, Command

try:
    from ezdxf.acc import np_support  # type: ignore  # mypy ???
except ImportError:
    np_support = None

__all__ = [
    "NumpyPath2d",
    "NumpyPoints2d",
    "NumpyShapesException",
    "EmptyShapeError",
    "to_qpainter_path",
]


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

    def bbox(self) -> BoundingBox2d:
        """Returns the bounding box of all vertices."""
        return BoundingBox2d(self.extents())


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

    def control_vertices(self) -> list[Vec2]:
        return self.vertices()

    def __copy__(self) -> Self:
        clone = self.__class__(None)
        clone._commands = self._commands.copy()
        clone._vertices = self._vertices.copy()
        return clone

    def command_codes(self) -> list[int]:
        """Internal API."""
        return list(self._commands)

    clone = __copy__

    def to_path2d(self) -> Path2d:
        """Returns a new :class:`Path2d` instance."""
        vertices = [Vec2(v) for v in self._vertices]
        commands = [Command(c) for c in self._commands]
        return Path2d.from_vertices_and_commands(vertices, commands)

    @classmethod
    def from_vertices(cls, vertices: Iterable[Vec2], close: bool = False) -> Self:
        new_path = cls(None)
        points = list(vertices)
        if len(points) == 0:
            return new_path

        if close and not points[0].isclose(points[-1]):
            points.append(points[0])
        new_path._vertices = np.array(points, dtype=np.float64)
        new_path._commands = np.full(
            len(points) - 1, fill_value=Command.LINE_TO, dtype=np.int8
        )
        return new_path

    @property
    def has_sub_paths(self) -> bool:
        """Returns ``True`` if the path is a :term:`Multi-Path` object that
        contains multiple sub-paths.

        """
        return Command.MOVE_TO in self._commands

    def sub_paths(self) -> list[Self]:
        """Yield all sub-paths as :term:`Single-Path` objects.

        It's safe to call :meth:`sub_paths` on any path-type:
        :term:`Single-Path`, :term:`Multi-Path` and :term:`Empty-Path`.

        """

        def append_sub_path() -> None:
            s: Self = self.__class__(None)
            s._vertices = vertices[vtx_start_index : vtx_index + 1]  # .copy() ?
            s._commands = commands[cmd_start_index:cmd_index]  # .copy() ?
            sub_paths.append(s)

        commands = self._commands
        if len(commands) == 0:
            return []
        if Command.MOVE_TO not in commands:
            return [self]

        sub_paths: list[Self] = []
        vertices = self._vertices
        vtx_start_index = 0
        vtx_index = 0
        cmd_start_index = 0
        cmd_index = 0
        for cmd in commands:
            if cmd == Command.LINE_TO:
                vtx_index += 1
            elif cmd == Command.CURVE3_TO:
                vtx_index += 2
            elif cmd == Command.CURVE4_TO:
                vtx_index += 3
            elif cmd == Command.MOVE_TO:
                append_sub_path()
                # MOVE_TO target vertex is the start vertex of the following path.
                vtx_index += 1
                vtx_start_index = vtx_index
                cmd_start_index = cmd_index + 1
            cmd_index += 1

        if commands[-1] != Command.MOVE_TO:
            append_sub_path()
        return sub_paths

    def has_clockwise_orientation(self) -> bool:
        """Returns ``True`` if 2D path has clockwise orientation.

        Raises:
            TypeError: can't detect orientation of a :term:`Multi-Path` object

        """
        if self.has_sub_paths:
            raise TypeError("can't detect orientation of a multi-path object")
        if np_support is None:
            return has_clockwise_orientation(self.vertices())
        else:
            return np_support.has_clockwise_orientation(self._vertices)

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
            self._commands = np.flip(commands[:-1]).copy()
            self._vertices = np.flip(self._vertices[:-1, ...], axis=0).copy()
        else:
            self._commands = np.flip(commands).copy()
            self._vertices = np.flip(self._vertices, axis=0).copy()
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
                ctrl, end_location = vertices[index : index + 2]
                index += 2
                pts = Vec2.generate(
                    Bezier3P((start, ctrl, end_location)).flattening(distance, segments)
                )
                next(pts)  # skip first vertex
                yield from pts
            elif cmd == Command.CURVE4_TO:
                ctrl1, ctrl2, end_location = vertices[index : index + 3]
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

    # Appending single commands (line_to, move_to, curve3_to, curve4_to) is not
    # efficient, because numpy arrays do not grow dynamically, they are reallocated for
    # every single command! Build basic path by the Python Path2d class and
    # convert the finalized path to a NumpyPath2d instances.
    # Concatenation of NumpyPath2d objects is faster than extending Path2d objects,
    # see profiling/numpy_concatenate.py

    def extend(self, paths: Sequence[NumpyPath2d]) -> None:
        """Extend an existing path by appending additional paths. The paths are
        connected by MOVE_TO commands if the end- and start point of sequential paths
        are not coincident (multi-path).
        """
        if not len(paths):
            return
        if not len(self._commands):
            first = paths[0]
            paths = paths[1:]
        else:
            first = self

        vertices: list[np.ndarray] = [first._vertices]
        commands: list[np.ndarray] = [first._commands]
        end: Vec2 = first.end

        for next_path in paths:
            if len(next_path._commands) == 0:
                continue
            if not end.isclose(next_path.start):
                commands.append(np.array((Command.MOVE_TO,), dtype=np.int8))
                vertices.append(next_path._vertices)
            else:
                vertices.append(next_path._vertices[1:])
            end = next_path.end
            commands.append(next_path._commands)
        self._vertices = np.concatenate(vertices, axis=0)
        self._commands = np.concatenate(commands)

    @staticmethod
    def concatenate(paths: Sequence[NumpyPath2d]) -> NumpyPath2d:
        """Returns a new path of concatenated paths. The paths are connected by
        MOVE_TO commands if the end- and start point of sequential paths are not
        coincident (multi-path).
        """

        if not paths:
            return NumpyPath2d(None)
        first = paths[0].clone()
        first.extend(paths[1:])
        return first


def to_qpainter_path(paths: Iterable[NumpyPath2d]):
    from ezdxf.addons.xqt import QPainterPath, QPointF

    paths = list(paths)
    if len(paths) == 0:
        raise ValueError("one or more paths required")

    qpath = QPainterPath()
    for path in paths:
        vertices = [QPointF(v.x, v.y) for v in path.vertices()]
        qpath.moveTo(vertices[0])
        index = 1
        for cmd in path.command_codes():
            if cmd == Command.LINE_TO:
                qpath.lineTo(vertices[index])
                index += 1
            elif cmd == Command.MOVE_TO:
                qpath.moveTo(vertices[index])
                index += 1
            elif cmd == Command.CURVE3_TO:
                qpath.quadTo(vertices[index], vertices[index + 1])
                index += 2
            elif cmd == Command.CURVE4_TO:
                qpath.cubicTo(vertices[index], vertices[index + 1], vertices[index + 2])
                index += 3
    return qpath
