#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import enum
from typing import NamedTuple, Union

from ezdxf.math import Vec3, OCS

__all__ = [
    "Command",
    "AnyCurve",
    "PathElement",
    "LineTo",
    "Curve3To",
    "Curve4To",
    "MoveTo",
]


@enum.unique
class Command(enum.IntEnum):
    START_PATH = -1  # external command, not use in Path()
    LINE_TO = 1  # (LINE_TO, end vertex)
    CURVE3_TO = 2  # (CURVE3_TO, end vertex, ctrl) quadratic bezier
    CURVE4_TO = 3  # (CURVE4_TO, end vertex, ctrl1, ctrl2) cubic bezier
    MOVE_TO = 4  # (MOVE_TO, end vertex), creates a gap and starts a sub-path


class LineTo(NamedTuple):
    end: Vec3

    @property
    def type(self):
        return Command.LINE_TO

    def to_wcs(self, ocs: OCS, elevation: float):
        return LineTo(end=ocs.to_wcs(self.end.replace(z=elevation)))


class MoveTo(NamedTuple):
    end: Vec3

    @property
    def type(self):
        return Command.MOVE_TO

    def to_wcs(self, ocs: OCS, elevation: float):
        return MoveTo(end=ocs.to_wcs(self.end.replace(z=elevation)))


class Curve3To(NamedTuple):
    end: Vec3
    ctrl: Vec3

    @property
    def type(self):
        return Command.CURVE3_TO

    def to_wcs(self, ocs: OCS, elevation: float):
        return Curve3To(
            end=ocs.to_wcs(self.end.replace(z=elevation)),
            ctrl=ocs.to_wcs(self.ctrl.replace(z=elevation)),
        )


class Curve4To(NamedTuple):
    end: Vec3
    ctrl1: Vec3
    ctrl2: Vec3

    @property
    def type(self):
        return Command.CURVE4_TO

    def to_wcs(self, ocs: OCS, elevation: float):
        return Curve4To(
            end=ocs.to_wcs(self.end.replace(z=elevation)),
            ctrl1=ocs.to_wcs(self.ctrl1.replace(z=elevation)),
            ctrl2=ocs.to_wcs(self.ctrl2.replace(z=elevation)),
        )


AnyCurve = (Command.CURVE3_TO, Command.CURVE4_TO)
PathElement = Union[LineTo, Curve3To, Curve4To, MoveTo]
