# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-07-10
from typing import TYPE_CHECKING, List, Tuple
from collections.abc import Sequence
from ezdxf.math import Vector, NULLVEC

if TYPE_CHECKING:
    from ezdxf.eztypes import LWPolyline, Polyline
    from ezdxf.entities.hatch import PolylinePath, EdgePath

__all__ = ['Path']


class Path(Sequence):
    def __init__(self, start: Vector = NULLVEC):
        self._start = Vector(start)
        self._commands: List[Tuple] = []

    def __len__(self):
        return self._commands

    def __getitem__(self, item):
        return self._commands[item]

    def __iter__(self):
        return iter(self._commands)

    @property
    def start(self) -> Vector:
        return self._start

    @start.setter
    def start(self, location: Vector) -> None:
        self._start = Vector(location)

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

    def line_to(self, location: Vector) -> None:
        self._commands.append(('line', Vector(location)))

    def cubic_to(self, location: Vector, ctrl1: Vector, ctrl2: Vector) -> None:
        self._commands.append(('cubic-bezier', Vector(location), Vector(ctrl1), Vector(ctrl2)))
