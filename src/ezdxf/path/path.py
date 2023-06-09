# Copyright (c) 2020-2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import abc
from typing import (
    Optional,
    Iterator,
    Iterable,
    Any,
    TypeVar,
    Type,
    Generic,
    Callable,
)
from typing_extensions import Self
from ezdxf.math import (
    Vec3,
    Vec2,
    NULLVEC,
    OCS,
    Bezier3P,
    Bezier4P,
    Matrix44,
    has_clockwise_orientation,
    UVec,
    AbstractBoundingBox,
    BoundingBox2d,
    BoundingBox,
)

from .commands import (
    Command,
    LineTo,
    MoveTo,
    Curve3To,
    Curve4To,
    PathElement,
)

__all__ = ["AbstractPath", "Path", "Path2d"]

MAX_DISTANCE = 0.01
MIN_SEGMENTS = 4
G1_TOL = 1e-4

T = TypeVar("T", Vec2, Vec3)

_slots = ("_vertices", "_start_index", "_commands", "_has_sub_paths", "_user_data")


class AbstractPath(Generic[T], abc.ABC):
    __slots__ = _slots
    _pnt_class: Type[T]

    def __init__(self, start: UVec = NULLVEC):
        # stores all command vertices in a contiguous list:
        self._vertices: list[T] = [self._pnt_class(start)]
        # start index of each command
        self._start_index: list[int] = []
        self._commands: list[Command] = []
        self._has_sub_paths = False
        self._user_data: Any = None  # should be immutable data!

    @classmethod
    def from_vertices_and_commands(
        cls, vertices: list[T], command_codes: list[Command], user_data: Any = None
    ) -> Self:
        """Create path instances from a list of vertices and a list of commands."""
        # Used for fast conversion from NumpyPath2d to Path2d.
        # This is "hacky" but also 8x faster than the correct way using only public
        # methods and properties.
        new_path = cls()
        if len(vertices) == 0:
            return new_path
        new_path._vertices = vertices
        new_path._commands = command_codes
        new_path._start_index = make_vertex_index(command_codes)
        new_path._has_sub_paths = any(cmd == Command.MOVE_TO for cmd in command_codes)
        new_path._user_data = user_data
        return new_path

    @abc.abstractmethod
    def transform(self, m: Matrix44) -> Self:
        """Returns a new transformed path.

        Args:
             m: transformation matrix of type :class:`~ezdxf.math.Matrix44`

        """
        ...

    @abc.abstractmethod
    def bbox(self) -> AbstractBoundingBox:
        """Returns the bounding box of the path control vertices."""
        ...

    def __len__(self) -> int:
        """Returns count of path elements."""
        return len(self._commands)

    def __getitem__(self, item) -> PathElement:
        """Returns the path element at given index, slicing is not supported."""
        if isinstance(item, slice):
            raise TypeError("slicing not supported")
        cmd = self._commands[item]
        index = self._start_index[item]
        vertices = self._vertices
        if cmd == Command.MOVE_TO:
            return MoveTo(vertices[index])
        if cmd == Command.LINE_TO:
            return LineTo(vertices[index])
        if cmd == Command.CURVE3_TO:  # end, ctrl
            return Curve3To(vertices[index + 1], vertices[index])
        if cmd == Command.CURVE4_TO:
            return Curve4To(  # end, ctrl1, ctrl2
                vertices[index + 2],
                vertices[index],
                vertices[index + 1],
            )
        raise ValueError(f"Invalid command: {cmd}")

    def __iter__(self) -> Iterator[PathElement]:
        return (self[i] for i in range(len(self._commands)))

    def commands(self) -> list[PathElement]:
        """Returns all path elements as list."""
        return list(self.__iter__())

    def __copy__(self) -> Self:
        """Returns a new copy of :class:`Path` with shared immutable data."""
        copy = self.__class__()
        # vertices itself are immutable - no copying required
        copy._vertices = self._vertices.copy()
        self._copy_properties(copy)
        return copy

    def _copy_properties(self, clone: AbstractPath) -> None:
        assert len(self._vertices) == len(clone._vertices)
        clone._commands = self._commands.copy()
        clone._start_index = self._start_index.copy()
        clone._has_sub_paths = self._has_sub_paths
        # copy by reference: user data should be immutable data!
        clone._user_data = self._user_data

    clone = __copy__

    @property
    def user_data(self) -> Any:
        """Attach arbitrary user data to a :class:`Path` object.
        The user data is copied by reference, no deep copy is applied
        therefore a mutable state is shared between copies.
        """
        return self._user_data

    @user_data.setter
    def user_data(self, data: Any):
        self._user_data = data

    @property
    def start(self) -> T:
        """:class:`Path` start point, resetting the start point of an empty
        path is possible.
        """
        return self._vertices[0]

    @start.setter
    def start(self, location: UVec) -> None:
        if self._commands:
            raise ValueError("Requires an empty path.")
        else:
            self._vertices[0] = self._pnt_class(location)

    @property
    def end(self) -> T:
        """:class:`Path` end point."""
        return self._vertices[-1]

    def control_vertices(self) -> list[T]:
        """Yields all path control vertices in consecutive order."""
        if self._commands:
            return list(self._vertices)
        return []

    def command_codes(self) -> list[int]:
        """Internal API."""
        return list(self._commands)

    @property
    def is_closed(self) -> bool:
        """Returns ``True`` if the start point is close to the end point."""
        vertices = self._vertices
        if len(vertices) > 1:
            return vertices[0].isclose(vertices[-1])
        return False

    @property
    def has_lines(self) -> bool:
        """Returns ``True`` if the path has any line segments."""
        return Command.LINE_TO in self._commands

    @property
    def has_curves(self) -> bool:
        """Returns ``True`` if the path has any curve segments."""
        return (
            Command.CURVE4_TO in self._commands or Command.CURVE3_TO in self._commands
        )

    @property
    def has_sub_paths(self) -> bool:
        """Returns ``True`` if the path is a :term:`Multi-Path` object that
        contains multiple sub-paths.

        """
        return self._has_sub_paths

    def has_clockwise_orientation(self) -> bool:
        """Returns ``True`` if 2D path has clockwise orientation, ignores
        z-axis of all control vertices.

        Raises:
            TypeError: can't detect orientation of a :term:`Multi-Path` object

        """
        if self.has_sub_paths:
            raise TypeError("can't detect orientation of a multi-path object")
        return has_clockwise_orientation(self._vertices)

    def append_path_element(self, cmd: PathElement) -> None:
        """Append a single path element."""
        t = cmd.type
        if t == Command.LINE_TO:
            self.line_to(cmd.end)  # type: ignore
        elif t == Command.MOVE_TO:
            self.move_to(cmd.end)  # type: ignore
        elif t == Command.CURVE3_TO:
            self.curve3_to(cmd.end, cmd.ctrl)  # type: ignore
        elif t == Command.CURVE4_TO:
            self.curve4_to(cmd.end, cmd.ctrl1, cmd.ctrl2)  # type: ignore
        else:
            raise ValueError(f"Invalid command: {t}")

    def line_to(self, location: UVec) -> None:
        """Add a line from actual path end point to `location`."""
        self._commands.append(Command.LINE_TO)
        self._start_index.append(len(self._vertices))
        self._vertices.append(self._pnt_class(location))

    def move_to(self, location: UVec) -> None:
        """Start a new sub-path at `location`. This creates a gap between the
        current end-point and the start-point of the new sub-path. This converts
        the instance into a :term:`Multi-Path` object.

        If the :meth:`move_to` command is the first command, the start point of
        the path will be reset to `location`.

        """
        commands = self._commands
        if not commands:
            self._vertices[0] = self._pnt_class(location)
            return
        self._has_sub_paths = True
        if commands[-1] == Command.MOVE_TO:
            # replace last move to command
            commands.pop()
            self._vertices.pop()
            self._start_index.pop()
        commands.append(Command.MOVE_TO)
        self._start_index.append(len(self._vertices))
        self._vertices.append(self._pnt_class(location))

    def curve3_to(self, location: UVec, ctrl: UVec) -> None:
        """Add a quadratic Bèzier-curve from actual path end point to
        `location`, `ctrl` is the control point for the quadratic Bèzier-curve.
        """
        self._commands.append(Command.CURVE3_TO)
        self._start_index.append(len(self._vertices))
        self._vertices.extend((self._pnt_class(ctrl), self._pnt_class(location)))

    def curve4_to(self, location: UVec, ctrl1: UVec, ctrl2: UVec) -> None:
        """Add a cubic Bèzier-curve from actual path end point to `location`,
        `ctrl1` and `ctrl2` are the control points for the cubic Bèzier-curve.
        """
        self._commands.append(Command.CURVE4_TO)
        self._start_index.append(len(self._vertices))
        pnt = self._pnt_class
        self._vertices.extend((pnt(ctrl1), pnt(ctrl2), pnt(location)))

    def close(self) -> None:
        """Close path by adding a line segment from the end point to the start
        point.
        """
        if not self.is_closed:
            self.line_to(self.start)

    def close_sub_path(self) -> None:
        """Close last sub-path by adding a line segment from the end point to
        the start point of the last sub-path. Behaves like :meth:`close` for
        :term:`Single-Path` instances.
        """
        if self.has_sub_paths:
            start_point = self._start_of_last_sub_path()
            assert (
                start_point is not None
            ), "internal error: required MOVE_TO command not found"
            if not self.end.isclose(start_point):
                self.line_to(start_point)
        else:
            self.close()

    def _start_of_last_sub_path(self) -> Optional[T]:
        move_to = Command.MOVE_TO
        commands = self._commands
        index = len(commands) - 1
        # The first command at index 0 is never MOVE_TO!
        while index > 0:
            if commands[index] == move_to:
                return self._vertices[self._start_index[index]]
            index -= 1
        return None

    def reversed(self) -> Self:
        """Returns a new :class:`Path` with reversed commands and control
        vertices.

        """
        path = self.clone()
        if not path._commands:
            return path
        if path._commands[-1] == Command.MOVE_TO:
            # The last move_to will become the first move_to.
            # A move_to as first command just moves the start point and can be
            # removed!
            # There are never two consecutive MOVE_TO commands in a Path!
            path._commands.pop()
            path._vertices.pop()
            path._start_index.pop()
            path._has_sub_paths = any(  # is still a multi-path?
                cmd == Command.MOVE_TO for cmd in path._commands
            )
        path._commands.reverse()
        path._vertices.reverse()
        path._start_index = make_vertex_index(path._commands)
        return path

    def clockwise(self) -> Self:
        """Returns new :class:`Path` in clockwise orientation.

        Raises:
            TypeError: can't detect orientation of a :term:`Multi-Path` object

        """
        if self.has_clockwise_orientation():
            return self.clone()
        else:
            return self.reversed()

    def counter_clockwise(self) -> Self:
        """Returns new :class:`Path` in counter-clockwise orientation.

        Raises:
            TypeError: can't detect orientation of a :term:`Multi-Path` object

        """

        if self.has_clockwise_orientation():
            return self.reversed()
        else:
            return self.clone()

    @abc.abstractmethod
    def approximate(self, segments: int = 20) -> Iterator[T]:
        """Approximate path by vertices, `segments` is the count of
        approximation segments for each Bézier curve.

        Does not yield any vertices for empty paths, where only a start point
        is present!

        Approximation of :term:`Multi-Path` objects is possible, but gaps are
        indistinguishable from line segments.

        """
        ...

    @abc.abstractmethod
    def flattening(self, distance: float, segments: int = 4) -> Iterator[T]:
        """Approximate path by vertices and use adaptive recursive flattening
        to approximate Bèzier curves. The argument `segments` is the
        minimum count of approximation segments for each curve, if the distance
        from the center of the approximation segment to the curve is bigger than
        `distance` the segment will be subdivided.

        Does not yield any vertices for empty paths, where only a start point
        is present!

        Flattening of :term:`Multi-Path` objects is possible, but gaps are
        indistinguishable from line segments.

        Args:
            distance: maximum distance from the center of the curve to the
                center of the line segment between two approximation points to
                determine if a segment should be subdivided.
            segments: minimum segment count per Bézier curve

        """
        ...

    def _approximate(self, curve3: Callable, curve4: Callable) -> Iterator[T]:
        if not self._commands:
            return

        start = self._vertices[0]
        yield start

        vertices = self._vertices
        for si, cmd in zip(self._start_index, self._commands):
            if cmd == Command.LINE_TO or cmd == Command.MOVE_TO:
                end_location = vertices[si]
                yield end_location
            elif cmd == Command.CURVE3_TO:
                ctrl, end_location = vertices[si : si + 2]
                pts = curve3(start, ctrl, end_location)
                next(pts)  # skip first vertex
                yield from pts
            elif cmd == Command.CURVE4_TO:
                ctrl1, ctrl2, end_location = vertices[si : si + 3]
                pts = curve4(start, ctrl1, ctrl2, end_location)
                next(pts)  # skip first vertex
                yield from pts
            else:
                raise ValueError(f"Invalid command: {cmd}")
            start = end_location

    def to_wcs(self, ocs: OCS, elevation: float) -> None:
        """Transform path from given `ocs` to WCS coordinates inplace."""
        # Important: requires a 3D path otherwise would change the type of path
        if self._pnt_class is not Vec3:
            raise TypeError("Not supported by 2D paths.")
        self._vertices = list(
            ocs.to_wcs(v.replace(z=elevation)) for v in self._vertices
        )

    def sub_paths(self) -> Iterator[Self]:
        """Yield sub-path as :term:`Single-Path` objects.

        It is safe to call :meth:`sub_paths` on any path-type:
        :term:`Single-Path`, :term:`Multi-Path` and :term:`Empty-Path`.

        """
        path = self.__class__(start=self.start)
        path._user_data = self._user_data
        move_to = Command.MOVE_TO
        for cmd in self.commands():
            if cmd.type == move_to:
                yield path
                path = self.__class__(start=cmd.end)
                path._user_data = self._user_data
            else:
                path.append_path_element(cmd)
        yield path

    def extend_multi_path(self, path: AbstractPath[T]) -> None:
        """Extend the path by another path. The source path is automatically a
        :term:`Multi-Path` object, even if the previous end point matches the
        start point of the appended path. Ignores paths without any commands
        (empty paths).

        """
        if len(path):
            self.move_to(path.start)
            for cmd in path.commands():
                self.append_path_element(cmd)

    def append_path(self, path: AbstractPath[T]) -> None:
        """Append another path to this path. Adds a :code:`self.line_to(path.start)`
        if the end of this path != the start of appended path.

        """
        if len(path) == 0:
            return  # do not append an empty path
        if self._commands:
            if not self.end.isclose(path.start):
                self.line_to(path.start)
        else:
            self.start = path.start
        for cmd in path.commands():
            self.append_path_element(cmd)


class Path(AbstractPath[Vec3]):
    __slots__ = _slots
    _pnt_class = Vec3

    def approximate(self, segments: int = 20) -> Iterator[Vec3]:
        def curve3(p0: T, p1: T, p2: T) -> Iterator[Vec3]:
            return iter(Bezier3P((p0, p1, p2)).approximate(segments))

        def curve4(p0: T, p1: T, p2: T, p3: T) -> Iterator[Vec3]:
            return iter(Bezier4P((p0, p1, p2, p3)).approximate(segments))

        return self._approximate(curve3, curve4)

    def flattening(self, distance: float, segments: int = 4) -> Iterator[Vec3]:
        def curve3(p0: T, p1: T, p2: T) -> Iterator[Vec3]:
            if distance == 0.0:
                raise ValueError(f"invalid max distance: 0.0")
            return iter(Bezier3P((p0, p1, p2)).flattening(distance, segments))

        def curve4(p0: T, p1: T, p2: T, p3: T) -> Iterator[Vec3]:
            if distance == 0.0:
                raise ValueError(f"invalid max distance: 0.0")
            return iter(Bezier4P((p0, p1, p2, p3)).flattening(distance, segments))

        return self._approximate(curve3, curve4)

    def to_2d_path(self) -> Path2d:
        """Returns a new 2D path. The conversion is almost as fast as a copy.

        .. versionadded:: 1.1

        """
        path2d = Path2d()
        path2d._vertices = Vec2.list(self._vertices)
        self._copy_properties(path2d)
        return path2d

    def transform(self, m: Matrix44) -> Self:
        """Returns a new transformed 3D path.

        Args:
             m: transformation matrix of type :class:`~ezdxf.math.Matrix44`

        """
        new_path = self.clone()
        new_path._vertices = list(m.transform_vertices(self._vertices))
        return new_path

    def bbox(self) -> BoundingBox:
        """Returns the bounding box of all control vertices as
        :class:`~ezdxf.math.BoundingBox` instance.
        """
        return BoundingBox(self.control_vertices())


CMD_SIZE = {
    Command.MOVE_TO: 1,
    Command.LINE_TO: 1,
    Command.CURVE3_TO: 2,
    Command.CURVE4_TO: 3,
}


def make_vertex_index(command_codes: Iterable[Command]) -> list[int]:
    cmd_size = CMD_SIZE
    start: int = 1
    start_index: list[int] = []
    for code in command_codes:
        start_index.append(start)
        start += cmd_size[code]
    return start_index


class Path2d(AbstractPath[Vec2]):
    __slots__ = _slots
    _pnt_class = Vec2

    def approximate(self, segments: int = 20) -> Iterator[Vec2]:
        def curve3(p0: T, p1: T, p2: T) -> Iterator[Vec2]:
            return Vec2.generate(Bezier3P((p0, p1, p2)).approximate(segments))

        def curve4(p0: T, p1: T, p2: T, p3: T) -> Iterator[Vec2]:
            return Vec2.generate(Bezier4P((p0, p1, p2, p3)).approximate(segments))

        return self._approximate(curve3, curve4)

    def flattening(self, distance: float, segments: int = 4) -> Iterator[Vec2]:
        def curve3(p0: T, p1: T, p2: T) -> Iterator[Vec2]:
            if distance == 0.0:
                raise ValueError(f"invalid max distance: 0.0")
            return Vec2.generate(Bezier3P((p0, p1, p2)).flattening(distance, segments))

        def curve4(p0: T, p1: T, p2: T, p3: T) -> Iterator[Vec2]:
            if distance == 0.0:
                raise ValueError(f"invalid max distance: 0.0")
            return Vec2.generate(
                Bezier4P((p0, p1, p2, p3)).flattening(distance, segments)
            )

        return self._approximate(curve3, curve4)

    def to_3d_path(self, elevation: float = 0.0) -> Path:
        """Returns a new 3D path, the z-axis of all vertices is set to `elevation`.
        The conversion is almost as fast as a copy.
        """
        path3d = Path()
        elevation = float(elevation)
        path3d._vertices = [Vec3(v.x, v.y, elevation) for v in self._vertices]
        self._copy_properties(path3d)
        return path3d

    def transform(self, m: Matrix44) -> Self:
        """Returns a new transformed 2D path.

        Args:
             m: transformation matrix of type :class:`~ezdxf.math.Matrix44`

        """
        new_path = self.clone()
        new_path._vertices = list(m.fast_2d_transform(self._vertices))
        return new_path

    def bbox(self) -> BoundingBox2d:
        """Returns the bounding box of all control vertices as :class:`~ezdxf.math.BoundingBox2d` instance.
        """
        return BoundingBox2d(self.control_vertices())
