#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Sequence
import abc
from .deps import Vec2, Path, Bezier4P
from .properties import Properties

# Page coordinates are always plot units:
# 1 plot unit (plu) = 0.025mm
# 40 plu = 1mm
# 1016 plu = 1 inch
# 3.39 plu = 1 dot @300 dpi
# positive x-axis is horizontal from left to right
# positive y-axis is vertical from bottom to top

class Backend(abc.ABC):
    def draw_cubic_bezier(
        self, properties: Properties, start: Vec2, ctrl1: Vec2, ctrl2: Vec2, end: Vec2
    ) -> None:
        # input coordinates are page coordinates
        curve = Bezier4P([start, ctrl1, ctrl2, end])
        # 10 plu = 0.25 mm
        self.draw_polyline(properties, list(curve.flattening(distance=10)))


    @abc.abstractmethod
    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        # input coordinates are page coordinates
        # argument <points> can be zero, one, two or more points.
        ...

    @abc.abstractmethod
    def draw_filled_polygon_buffer(
        self, properties: Properties, paths: Sequence[Path], fill_method: int
    ) -> None:
        # input coordinates are page coordinates
        ...

    @abc.abstractmethod
    def draw_outline_polygon_buffer(
        self, properties: Properties, paths: Sequence[Path]) -> None:
        # input coordinates are page coordinates
        ...
