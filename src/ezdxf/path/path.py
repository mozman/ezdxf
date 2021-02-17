# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Iterable
from collections import abc
import warnings

from ezdxf.math import (
    Vec3, NULLVEC, OCS, Bezier3P, Bezier4P, Matrix44,
    ConstructionEllipse, BSpline, has_clockwise_orientation,
)
from ezdxf.entities import LWPolyline, Polyline, Spline
from .commands import Command, LineTo, Curve3To, Curve4To, AnyCurve, PathElement

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, Ellipse, Arc, Circle

__all__ = ['Path']

MAX_DISTANCE = 0.01
MIN_SEGMENTS = 4
G1_TOL = 1e-4


class Path(abc.Sequence):
    __slots__ = ('_start', '_commands')

    def __init__(self, start: 'Vertex' = NULLVEC):
        self._start = Vec3(start)
        self._commands: List[PathElement] = []

    def __len__(self) -> int:
        return len(self._commands)

    def __getitem__(self, item) -> PathElement:
        return self._commands[item]

    def __iter__(self) -> Iterable[PathElement]:
        return iter(self._commands)

    def __copy__(self) -> 'Path':
        """ Returns a new copy of :class:`Path` with shared immutable data. """
        copy = Path(self._start)
        # immutable data
        copy._commands = list(self._commands)
        return copy

    clone = __copy__

    @property
    def start(self) -> Vec3:
        """ :class:`Path` start point, resetting the start point of an empty
        path is possible.
        """
        return self._start

    @start.setter
    def start(self, location: 'Vertex') -> None:
        if len(self._commands):
            raise ValueError('Requires an empty path.')
        else:
            self._start = Vec3(location)

    @property
    def end(self) -> Vec3:
        """ :class:`Path` end point. """
        if self._commands:
            return self._commands[-1].end
        else:
            return self._start

    @property
    def is_closed(self) -> bool:
        """ Returns ``True`` if the start point is close to the end point. """
        return self._start.isclose(self.end)

    @property
    def has_lines(self) -> bool:
        """ Returns ``True`` if the path has any line segments. """
        return any(cmd.type == Command.LINE_TO for cmd in self._commands)

    @property
    def has_curves(self) -> bool:
        """ Returns ``True`` if the path has any curve segments. """
        return any(cmd.type in AnyCurve for cmd in self._commands)

    def has_clockwise_orientation(self) -> bool:
        """ Returns ``True`` if 2D path has clockwise orientation, ignores
        z-axis of all control vertices.
        """
        return has_clockwise_orientation(self.control_vertices())

    def line_to(self, location: 'Vertex') -> None:
        """ Add a line from actual path end point to `location`.
        """
        self._commands.append(LineTo(end=Vec3(location)))

    def curve3_to(self, location: 'Vertex', ctrl: 'Vertex') -> None:
        """ Add a quadratic Bèzier-curve from actual path end point to
        `location`, `ctrl` is the control point for the quadratic Bèzier-curve.
        """
        self._commands.append(Curve3To(end=Vec3(location), ctrl=Vec3(ctrl)))

    def curve4_to(self, location: 'Vertex', ctrl1: 'Vertex',
                  ctrl2: 'Vertex') -> None:
        """ Add a cubic Bèzier-curve from actual path end point to `location`,
        `ctrl1` and `ctrl2` are the control points for the cubic Bèzier-curve.
        """
        self._commands.append(Curve4To(
            end=Vec3(location), ctrl1=Vec3(ctrl1), ctrl2=Vec3(ctrl2))
        )

    curve_to = curve4_to  # TODO: 2021-01-30, remove compatibility alias

    def close(self) -> None:
        """ Close path by adding a line segment from the end point to the start
        point.
        """
        if not self.is_closed:
            self.line_to(self.start)

    def reversed(self) -> 'Path':
        """ Returns a new :class:`Path` with reversed segments and control
        vertices.
        """
        if len(self) == 0:
            return Path(self.start)

        path = Path(start=self.end)
        for index in range(len(self) - 1, -1, -1):
            cmd = self[index]
            if index > 0:
                prev_end = self[index - 1].end
            else:
                prev_end = self.start

            if cmd.type == Command.LINE_TO:
                path.line_to(prev_end)
            elif cmd.type == Command.CURVE3_TO:
                path.curve3_to(prev_end, cmd.ctrl)
            elif cmd.type == Command.CURVE4_TO:
                path.curve4_to(prev_end, cmd.ctrl2, cmd.ctrl1)
        return path

    def clockwise(self) -> 'Path':
        """ Returns new :class:`Path` in clockwise orientation. """
        if self.has_clockwise_orientation():
            return self.clone()
        else:
            return self.reversed()

    def counter_clockwise(self) -> 'Path':
        """ Returns new :class:`Path` in counter-clockwise orientation. """
        if self.has_clockwise_orientation():
            return self.reversed()
        else:
            return self.clone()

    def approximate(self, segments: int = 20) -> Iterable[Vec3]:
        """ Approximate path by vertices, `segments` is the count of
        approximation segments for each Bézier curve.

        Does not yield any vertices for empty paths, where only a start point
        is present!

        """

        def approx_curve3(s, c, e) -> Iterable[Vec3]:
            return Bezier3P((s, c, e)).approximate(segments)

        def approx_curve4(s, c1, c2, e) -> Iterable[Vec3]:
            return Bezier4P((s, c1, c2, e)).approximate(segments)

        yield from self._approximate(approx_curve3, approx_curve4)

    def flattening(self, distance: float,
                   segments: int = 16) -> Iterable[Vec3]:
        """ Approximate path by vertices and use adaptive recursive flattening
        to approximate Bèzier curves. The argument `segments` is the
        minimum count of approximation segments for each curve, if the distance
        from the center of the approximation segment to the curve is bigger than
        `distance` the segment will be subdivided.

        Does not yield any vertices for empty paths, where only a start point
        is present!

        Args:
            distance: maximum distance from the center of the curve to the
                center of the line segment between two approximation points to
                determine if a segment should be subdivided.
            segments: minimum segment count per Bézier curve

        """

        def approx_curve3(s, c, e) -> Iterable[Vec3]:
            return Bezier3P((s, c, e)).flattening(distance, segments)

        def approx_curve4(s, c1, c2, e) -> Iterable[Vec3]:
            return Bezier4P((s, c1, c2, e)).flattening(distance, segments)

        yield from self._approximate(approx_curve3, approx_curve4)

    def _approximate(self, approx_curve3, approx_curve4) -> Iterable[Vec3]:
        if not self._commands:
            return

        start = self._start
        yield start

        for cmd in self._commands:
            end_location = cmd.end
            if cmd.type == Command.LINE_TO:
                yield end_location
            elif cmd.type == Command.CURVE3_TO:
                pts = iter(
                    approx_curve3(start, cmd.ctrl, end_location)
                )
                next(pts)  # skip first vertex
                yield from pts
            elif cmd.type == Command.CURVE4_TO:
                pts = iter(
                    approx_curve4(start, cmd.ctrl1, cmd.ctrl2, end_location)
                )
                next(pts)  # skip first vertex
                yield from pts
            else:
                raise ValueError(f'Invalid command: {cmd.type}')
            start = end_location

    def transform(self, m: 'Matrix44') -> 'Path':
        """ Returns a new transformed path.

        Args:
             m: transformation matrix of type :class:`~ezdxf.math.Matrix44`

        """
        new_path = self.__class__(m.transform(self.start))
        for cmd in self._commands:

            if cmd.type == Command.LINE_TO:
                new_path.line_to(m.transform(cmd.end))
            elif cmd.type == Command.CURVE3_TO:
                loc, ctrl = m.transform_vertices(
                    (cmd.end, cmd.ctrl)
                )
                new_path.curve3_to(loc, ctrl)
            elif cmd.type == Command.CURVE4_TO:
                loc, ctrl1, ctrl2 = m.transform_vertices(
                    (cmd.end, cmd.ctrl1, cmd.ctrl2)
                )
                new_path.curve4_to(loc, ctrl1, ctrl2)
            else:
                raise ValueError(f'Invalid command: {cmd.type}')

        return new_path

    def to_wcs(self, ocs: OCS, elevation: float):
        """ Transform path from given `ocs` to WCS coordinates inplace. """
        self._start = ocs.to_wcs(self._start.replace(z=elevation))
        for i, cmd in enumerate(self._commands):
            self._commands[i] = cmd.to_wcs(ocs, elevation)

    def add_curves(self, curves: Iterable[Bezier4P]) -> None:
        """ Add multiple cubic Bèzier-curves to the path.

        .. deprecated:: 0.15.3
            replaced by factory function :func:`add_bezier4p`

        """
        warnings.warn(
            'use tool function add_bezier4p(),'
            'will be removed in v0.17.', DeprecationWarning)
        from .tools import add_bezier4p
        add_bezier4p(self, curves)

    def add_bezier3p(self, curves: Iterable[Bezier3P]) -> None:
        """ Add multiple quadratic Bèzier-curves to the path.

        """
        warnings.warn(
            'use tool function add_bezier3p(),'
            'will be removed in v0.17.', DeprecationWarning)
        from .tools import add_bezier3p
        add_bezier3p(self, curves)

    def add_ellipse(self, ellipse: ConstructionEllipse, segments=1,
                    reset=True) -> None:
        """ Add an elliptical arc as multiple cubic Bèzier-curves

        .. deprecated:: 0.15.3
            replaced by factory function :func:`add_ellipse`

        """
        warnings.warn(
            'use tool function add_ellipse(),'
            'will be removed in v0.17.', DeprecationWarning)
        from .tools import add_ellipse
        add_ellipse(self, ellipse, segments, reset)

    def add_spline(self, spline: BSpline, level=4, reset=True) -> None:
        """ Add a B-spline as multiple cubic Bèzier-curves.

        .. deprecated:: 0.15.3
            replaced by factory function :func:`add_spline`

        """
        warnings.warn(
            'use tool function add_spline(),'
            'will be removed in v0.17.', DeprecationWarning)
        from .tools import add_spline
        add_spline(self, spline, level, reset)

    @classmethod
    def from_vertices(cls, vertices: Iterable['Vertex'], close=False) -> 'Path':
        """ Returns a :class:`Path` from given `vertices`.

        .. deprecated:: 0.15.3
            replaced by factory function :func:`from_vertices()`

        """
        warnings.warn(
            'use factory function from_vertices(),'
            'will be removed in v0.17.', DeprecationWarning)
        from .converter import from_vertices
        return from_vertices(vertices, close)

    @classmethod
    def from_lwpolyline(cls, lwpolyline: 'LWPolyline') -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.LWPolyline`
        entity, all vertices transformed to WCS.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(lwpolyline),'
            'will be removed in v0.17.', DeprecationWarning)
        from .converter import make_path
        return make_path(lwpolyline)

    @classmethod
    def from_polyline(cls, polyline: 'Polyline') -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Polyline`
        entity, all vertices transformed to WCS.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(polyline),'
            'will be removed in v0.17.', DeprecationWarning)
        from .converter import make_path
        return make_path(polyline)

    @classmethod
    def from_spline(cls, spline: 'Spline', level: int = 4) -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Spline`.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(polyline),'
            'will be removed in v0.17.', DeprecationWarning)
        from .converter import make_path
        return make_path(spline, level=level)

    @classmethod
    def from_ellipse(cls, ellipse: 'Ellipse', segments: int = 1) -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Ellipse`.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(ellipse),'
            'will be removed in v0.17.', DeprecationWarning)
        from .converter import make_path
        return make_path(ellipse, segments=segments)

    @classmethod
    def from_arc(cls, arc: 'Arc', segments: int = 1) -> 'Path':
        """ Returns a :class:`Path` from an :class:`~ezdxf.entities.Arc`.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(arc),'
            'will be removed in v0.17.', DeprecationWarning)
        from .converter import make_path
        return make_path(arc, segments=segments)

    @classmethod
    def from_circle(cls, circle: 'Circle', segments: int = 1) -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Circle`.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(circle),'
            'will be removed in v0.17.', DeprecationWarning)
        from .converter import make_path
        return make_path(circle, segments=segments)

    def control_vertices(self):
        """ Yields all path control vertices in consecutive order. """
        if len(self):
            yield self.start
            for cmd in self._commands:
                if cmd.type == Command.LINE_TO:
                    yield cmd.end
                elif cmd.type == Command.CURVE3_TO:
                    yield cmd.ctrl
                    yield cmd.end
                elif cmd.type == Command.CURVE4_TO:
                    yield cmd.ctrl1
                    yield cmd.ctrl2
                    yield cmd.end
