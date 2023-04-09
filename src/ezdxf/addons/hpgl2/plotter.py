#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations

from typing import Sequence, Iterator

from .deps import Vec2, Path, NULLVEC2
from .properties import RGB, Properties
from .backend import Backend
from .page import Page, get_page_size


class Plotter:
    def __init__(self, backend: Backend) -> None:
        self.backend = backend
        self.page = Page(0, 0)
        self.properties = Properties()
        self.is_pen_down: bool = False
        self.is_absolute_mode = True
        self.is_polygon_mode = False
        self._user_location = NULLVEC2
        self.pen_state_stack: list[bool] = []
        self.reset()

    @property
    def user_location(self) -> Vec2:
        """Returns the current pen location as point in the user coordinate system."""
        return self._user_location

    @property
    def page_location(self) -> Vec2:
        """Returns the current pen location as page point in plotter units."""
        location = self.user_location
        return self.page.page_point(location.x, location.y)

    def defaults(self) -> None:
        """DF command"""
        self.properties.reset()
        self.is_pen_down = False
        self.set_absolute_mode()
        self.exit_polygon_mode()
        self.pen_state_stack.clear()

    def reset(self) -> None:
        """IN command"""
        self.defaults()
        size_x, size_y = get_page_size("ISO A0")
        self.setup_page(size_x, size_y)
        self._user_location = NULLVEC2

    def setup_page(self, size_x: int, size_y: int):
        self.page = Page(size_x, size_y)
        self.properties.set_page_size(size_x, size_y)

    def pen_up(self) -> None:
        self.is_pen_down = False

    def pen_down(self) -> None:
        self.is_pen_down = True

    def push_pen_state(self) -> None:
        self.pen_state_stack.append(self.is_pen_down)

    def pop_pen_state(self) -> None:
        if len(self.pen_state_stack):
            self.is_pen_down = self.pen_state_stack.pop()

    def move_to(self, location: Vec2) -> None:
        if self.is_absolute_mode:
            self.move_to_abs(location)
        else:
            self.move_to_rel(location)

    def move_to_abs(self, user_location: Vec2) -> None:
        self._user_location = user_location

    def move_to_rel(self, user_location: Vec2) -> None:
        self._user_location += user_location

    def set_absolute_mode(self) -> None:
        self.is_absolute_mode = True

    def set_relative_mode(self) -> None:
        self.is_absolute_mode = False

    def set_current_pen(self, index: int) -> None:
        self.properties.set_current_pen(index)

    def set_max_pen_count(self, index: int) -> None:
        self.properties.set_max_pen_count(index)

    def set_pen_width(self, index: int, width: float) -> None:
        self.properties.set_pen_width(index, width)

    def set_pen_color(self, index: int, color: RGB) -> None:
        self.properties.set_pen_color(index, color)

    def set_fill_type(self, fill_type: int, spacing: float, angle: float) -> None:
        if fill_type in (3, 4):  # adjust spacing between hatching lines
            spacing = max(self.page.scale_length(spacing))
        self.properties.set_fill_type(fill_type, spacing, angle)

    def enter_polygon_mode(self) -> None:
        self.is_polygon_mode = True

    def exit_polygon_mode(self) -> None:
        self.is_polygon_mode = False

    def edge_polygon(self) -> None:
        pass

    def plot_polyline(self, points: Sequence[Vec2]):
        if not points:
            return
        if self.is_absolute_mode:
            self.plot_abs_polyline(points)
        else:
            self.plot_rel_polyline(points)

    def plot_abs_polyline(self, points: Sequence[Vec2]):
        # input coordinates are user coordinates
        if not points:
            return
        current_page_location = self.page_location
        self.move_to_abs(points[-1])  # user coordinates!
        if self.is_pen_down:
            # convert to page coordinates:
            points = self.page.page_points(points)
            # insert current page location as starting point:
            points.insert(0, current_page_location)
            # draw polyline in absolute page coordinates:
            self.backend.draw_polyline(self.properties, points)

    def plot_rel_polyline(self, points: Sequence[Vec2]):
        # input coordinates are user coordinates
        if not points:
            return
        # convert to absolute user coordinates:
        self.plot_abs_polyline(
            tuple(rel_to_abs_points_dynamic(self.user_location, points))
        )

    def plot_abs_circle(self, radius: float):
        # radius in user units
        if self.is_pen_down:
            # convert radius to page units:
            rx, ry = self.page.scale_length(radius)
            # draw circle in absolute page coordinates:
            self.backend.draw_circle(self.properties, self.page_location, rx, ry)

    def plot_abs_cubic_bezier(self, ctrl1: Vec2, ctrl2: Vec2, end: Vec2):
        # input coordinates are user coordinates
        current_page_location = self.page_location
        self.move_to_abs(end)  # user coordinates!
        if self.is_pen_down:
            # convert to page coordinates:
            ctrl1, ctrl2, end = self.page.page_points((ctrl1, ctrl2, end))
            # draw cubic bezier curve in absolute page coordinates:
            self.backend.draw_cubic_bezier(
                self.properties, current_page_location, ctrl1, ctrl2, end
            )

    def plot_rel_cubic_bezier(self, ctrl1: Vec2, ctrl2: Vec2, end: Vec2):
        # input coordinates are user coordinates
        ctrl1, ctrl2, end = rel_to_abs_points_static(
            self.user_location, (ctrl1, ctrl2, end)
        )
        self.plot_abs_cubic_bezier(ctrl1, ctrl2, end)

    def plot_filled_polygon(self, paths: Sequence[Path], fill_method: int):
        # input coordinates are page coordinates!
        self.backend.draw_filled_polygon(self.properties, paths, fill_method)

    def plot_outline_polygon(self, paths: Sequence[Path]):
        # input coordinates are page coordinates!
        self.backend.draw_outline_polygon(self.properties, paths)


def rel_to_abs_points_dynamic(current: Vec2, points: Sequence[Vec2]) -> Iterator[Vec2]:
    """Returns the absolute location of increment points, each point is an increment
    of the previous point starting at the current pen location.
    """
    for point in points:
        current += point
        yield current


def rel_to_abs_points_static(current: Vec2, points: Sequence[Vec2]) -> Iterator[Vec2]:
    """Returns the absolute location of increment points, all points are relative
    to the current pen location.
    """
    for point in points:
        yield current + point
