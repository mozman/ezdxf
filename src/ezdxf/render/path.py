# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-07-10
from typing import TYPE_CHECKING, List, Tuple, Iterable
from collections.abc import Sequence
from ezdxf.math import Vector, NULLVEC, Bezier4P

if TYPE_CHECKING:
    from ezdxf.eztypes import LWPolyline, Polyline, Vertex
    from ezdxf.entities.hatch import PolylinePath, EdgePath

__all__ = ['Path']


class Path(Sequence):
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
        return self._start

    @start.setter
    def start(self, location: 'Vertex') -> None:
        self._start = Vector(location)

    @property
    def end(self) -> Vector:
        if self._commands:
            return self._commands[-1][1]
        else:
            return self._start

    @classmethod
    def from_lwpolyline(cls, lwpolyline: 'LWPolyline') -> 'Path':
        pass

    @classmethod
    def from_polyline(cls, polyline: 'Polyline') -> 'Path':
        pass

    @classmethod
    def from_hatch_polyline_path(cls, path: 'PolylinePath') -> 'Path':
        pass

    @classmethod
    def from_hatch_edge_path(cls, path: 'EdgePath') -> 'Path':
        pass

    def line_to(self, location: 'Vertex') -> None:
        self._commands.append(('line', Vector(location)))

    def cubic_to(self, location: 'Vertex', ctrl1: 'Vertex', ctrl2: 'Vertex') -> None:
        self._commands.append(('cubic', Vector(location), Vector(ctrl1), Vector(ctrl2)))

    def approximate(self, segments: int = 20) -> Iterable[Vector]:
        if not self._commands:
            return

        start = self._start
        yield start

        for cmd in self._commands:
            name = cmd[0]
            end_location = cmd[1]
            if name == 'line':
                yield end_location
            elif name == 'cubic':
                pts = iter(Bezier4P((start, cmd[2], cmd[3], end_location)).approximate(segments))
                next(pts)  # skip first vertex
                yield from pts
            else:
                raise ValueError(f'Invalid command: {name}')
            start = end_location
