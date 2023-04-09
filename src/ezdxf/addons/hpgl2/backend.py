#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from typing import Sequence
import abc
from .deps import Vec2, Path
from .properties import Properties


class Backend(abc.ABC):
    @abc.abstractmethod
    def draw_cubic_bezier(
        self, properties: Properties, start: Vec2, ctrl1: Vec2, ctrl2: Vec2, end: Vec2
    ) -> None:
        # input coordinates are page coordinates
        ...

    @abc.abstractmethod
    def draw_circle(
        self, properties: Properties, center: Vec2, rx: float, ry: float
    ) -> None:
        # input coordinates are page coordinates
        ...

    @abc.abstractmethod
    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        # input coordinates are page coordinates
        ...

    @abc.abstractmethod
    def draw_filled_polygon(
        self, properties: Properties, paths: Sequence[Path], fill_method: int
    ) -> None:
        # input coordinates are page coordinates
        ...

    @abc.abstractmethod
    def draw_outline_polygon(
        self, properties: Properties, paths: Sequence[Path]) -> None:
        # input coordinates are page coordinates
        ...
