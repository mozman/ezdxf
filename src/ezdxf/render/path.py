# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-07-10
from typing import TYPE_CHECKING, List, Tuple, Iterable, Sequence
from collections import abc
from enum import Enum
import math
from ezdxf.math import Vector, NULLVEC, Bezier4P, Matrix44, bulge_to_arc, cubic_bezier_from_arc

if TYPE_CHECKING:
    from ezdxf.eztypes import LWPolyline, Polyline, Vertex
    from ezdxf.entities.hatch import PolylinePath, EdgePath

__all__ = ['Path', 'Command']


class Command(Enum):
    LINE = 1
    CUBIC = 2


class Path(abc.Sequence):
    def __init__(self, start: 'Vertex' = NULLVEC):
        self._start = Vector(start)
        self._commands: List[Tuple] = []

    def __len__(self):
        return len(self._commands)

    def __getitem__(self, item):
        return self._commands[item]

    def __iter__(self):
        return iter(self._commands)

    @property
    def start(self) -> Vector:
        """ Path start point. """
        return self._start

    @start.setter
    def start(self, location: 'Vertex') -> None:
        self._start = Vector(location)

    @property
    def end(self) -> Vector:
        """ Path end point. """
        if self._commands:
            return self._commands[-1][1]
        else:
            return self._start

    @classmethod
    def from_lwpolyline(cls, lwpolyline: 'LWPolyline') -> 'Path':
        assert lwpolyline.dxftype() == 'LWPOLYLINE'
        path = cls()
        path._setup_polyline(lwpolyline.points('xyb'), close=lwpolyline.closed)
        return path

    @classmethod
    def from_polyline(cls, polyline: 'Polyline') -> 'Path':
        assert polyline.dxftype() == 'POLYLINE'
        points = [vertex.format('xyb') for vertex in polyline.vertices]
        path = cls()
        path._setup_polyline(points, close=polyline.is_closed)
        return path

    def _setup_polyline(self, points: Iterable[Sequence[float]], close: bool) -> None:
        def bulge_to(p1: Vector, p2: Vector, bulge: float):
            center, start_angle, end_angle, radius = bulge_to_arc(p1, p2, bulge)
            curves = list(
                cubic_bezier_from_arc(Vector(center), radius, math.degrees(start_angle), math.degrees(end_angle)))

            if not curves[0].control_points[0].isclose(p1):
                # reverse all curves
                curves = list(c.reverse() for c in curves)
                curves.reverse()

            for curve in curves:
                pts = curve.control_points
                self.cubic_to(pts[3], pts[1], pts[2])

        prev_point = None
        prev_bulge = 0
        for x, y, bulge in points:
            point = Vector(x, y)
            if prev_point is None:
                self.start = point
                prev_point = point
                prev_bulge = bulge
                continue

            if prev_bulge:
                bulge_to(prev_point, point, prev_bulge)
            else:
                self.line_to(point)
            prev_point = point
            prev_bulge = bulge

        if close and not self.start.isclose(self.end):
            if prev_bulge:
                bulge_to(self.end, self.start, prev_bulge)
            else:
                self.line_to(self.start)

    @classmethod
    def from_hatch_polyline_path(cls, path: 'PolylinePath') -> 'Path':
        pass

    @classmethod
    def from_hatch_edge_path(cls, path: 'EdgePath') -> 'Path':
        pass

    def line_to(self, location: 'Vertex') -> None:
        """ Add a line from actual path end point to `location`.
        """
        self._commands.append((Command.LINE, Vector(location)))

    def cubic_to(self, location: 'Vertex', ctrl1: 'Vertex', ctrl2: 'Vertex') -> None:
        """ Add a cubic bezier curve from actual path end point to `location`, `ctrl1` and
        `ctrl2` are the control points of the cubic bezier curve.
        """
        self._commands.append((Command.CUBIC, Vector(location), Vector(ctrl1), Vector(ctrl2)))

    def approximate(self, segments: int = 20) -> Iterable[Vector]:
        """ Approximate path by vertices, `segments` is the count of approximation segments
        for each cubic bezier curve.
        """
        if not self._commands:
            return

        start = self._start
        yield start

        for cmd in self._commands:
            type_ = cmd[0]
            end_location = cmd[1]
            if type_ == Command.LINE:
                yield end_location
            elif type_ == Command.CUBIC:
                pts = iter(Bezier4P((start, cmd[2], cmd[3], end_location)).approximate(segments))
                next(pts)  # skip first vertex
                yield from pts
            else:
                raise ValueError(f'Invalid command: {type_}')
            start = end_location

    def transform(self, m: 'Matrix44') -> 'Path':
        """ Returns a new transformed path.

        Args:
             m: transformation matrix of type :class:`~ezdxf.math.Matrix44`

        """
        new_path = self.__class__(m.transform(self.start))
        for cmd in self._commands:
            type_ = cmd[0]
            if type_ == Command.LINE:
                new_path.line_to(m.transform(cmd[1]))
            elif type_ == Command.CUBIC:
                loc, ctrl1, ctrl2 = m.transform_vertices(cmd[1:])
                new_path.cubic_to(loc, ctrl1, ctrl2)
            else:
                raise ValueError(f'Invalid command: {type_}')

        return new_path
