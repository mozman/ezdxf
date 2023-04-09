#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Sequence
from .backend import Backend
from .deps import Vec2, Path
from .properties import Properties
from .plotter import Plotter


class PathBackend(Backend):
    def __init__(self, location: Vec2):
        self.path = Path(location)

    def draw_cubic_bezier(
        self, properties: Properties, start: Vec2, ctrl1: Vec2, ctrl2: Vec2, end: Vec2
    ) -> None:
        ...

    def draw_circle(
        self, properties: Properties, center: Vec2, rx: float, ry
    ) -> None:
        ...

    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        for p in points:
            self.path.line_to(p)

    def draw_filled_polygon(
        self, properties: Properties, paths: Sequence[Path], fill_method: int
    ) -> None:
        raise NotImplementedError()

    def draw_outline_polygon(
        self, properties: Properties, paths: Sequence[Path]) -> None:
        raise NotImplementedError()

    def get_paths(self, fill_method: int) -> Sequence[Path]:
        return list(self.path.sub_paths())

    def close_path(self):
        self.path.close_sub_path()


class PolygonBuffer(Plotter):
    def __init__(self, output_plotter: Plotter):
        super().__init__(PathBackend(output_plotter.page_location))
        self.page = output_plotter.page
        self.properties = output_plotter.properties
        self.is_pen_down = output_plotter.is_pen_down
        self.is_absolute_mode = output_plotter.is_absolute_mode
        self._user_location = output_plotter.user_location
        self.enter_polygon_mode()

    @property
    def path_backend(self) -> PathBackend:
        assert isinstance(self.backend, PathBackend)
        return self.backend

    def close_polygon(self):
        self.path_backend.close_path()

    def get_paths(self, fill_method: int) -> Sequence[Path]:
        self.close_polygon()
        return self.path_backend.get_paths(fill_method)
