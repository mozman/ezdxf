#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterator, Iterable
import string

from .deps import Vec2, NULLVEC2
from .properties import RGB
from .plotter import Plotter
from .polygon_buffer import PolygonBuffer
from .tokenizer import Command, pe_decode


class Interpreter:
    def __init__(self, plotter: Plotter) -> None:
        self.errors: list[str] = []
        self.unsupported_commands: set[str] = set()
        # current plotter:
        self.plotter = plotter
        # real output plotter:
        self.output_plotter = plotter
        # fake plotter as polygon buffer:
        self.polygon_buffer = PolygonBuffer(plotter)
        plotter.reset()

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    def run(self, commands: list[Command]) -> None:
        for name, args in commands:
            method = getattr(self, f"cmd_{name.lower()}", None)
            if method:
                method(args)
            elif name[0] in string.ascii_letters:
                self.unsupported_commands.add(name)

    def enter_polygon_mode(self, status: int):
        if status == 0:
            self.polygon_buffer = PolygonBuffer(self.output_plotter)
            # replace current plotter
            self.plotter = self.polygon_buffer
        elif status == 1:
            self.polygon_buffer.close_polygon()
        else:
            self.add_error(f"invalid status {status} for command PM")

    def exit_polygon_mode(self):
        self.polygon_buffer.close_polygon()
        # restore output plotter
        self.plotter = self.output_plotter

    def cmd_escape(self, _):
        """Embedded PCL5 commands are ignored."""
        pass

    def cmd_pg(self, _):
        """Advance full page - not supported."""
        pass

    def cmd_wu(self, _):
        """Pen width unit selection - not supported."""
        pass

    def cmd_la(self, _):
        """Line attribute selection (line ends and line joins) - not supported."""
        pass

    def cmd_rf(self, _):
        """define raster fill - not supported."""
        pass

    def cmd_tr(self, _):
        """Set transparency mode - not supported. Transparency mode is off, white
        fillings cover graphics beneath.
        """
        pass

    def cmd_in(self, _):
        """Initialize plotter."""
        self.plotter.reset()

    def cmd_df(self, _):
        """Reset to defaults."""
        self.plotter.defaults()

    def cmd_ps(self, args: list[bytes]):
        """Set page size in plotter units - not documented."""
        values = tuple(to_ints(args))
        if len(values) != 2:
            self.add_error("invalid arguments for command PS")
            return
        self.plotter.setup_page(values[0], values[1])

    # Configure pens, line types, fill types
    def cmd_ft(self, args: list[bytes]):
        """Set fill type."""
        fill_type = 1
        spacing = 0.0
        angle = 0.0
        values = tuple(to_floats(args))
        arg_count = len(values)
        if arg_count > 0:
            fill_type = int(values[0])
        if arg_count > 1:
            spacing = values[1]
        if arg_count > 2:
            angle = values[2]
        self.plotter.set_fill_type(fill_type, spacing, angle)

    def cmd_pc(self, args: list[bytes]):
        """Set pen color as RGB tuple."""
        values = list(to_ints(args))
        if len(values) == 4:
            index, r, g, b = values
            self.plotter.set_pen_color(index, RGB(r, g, b))
        else:
            self.add_error("invalid arguments for PC command")



    def cmd_pw(self, args: list[bytes]):
        """Set pen width."""
        arg_count = len(args)
        if arg_count:
            width = to_float(args[0], 0.35)
        else:
            self.add_error("invalid arguments for PW command")
            return
        index = -1
        if arg_count > 1:
            index = to_int(args[1], index)
        self.plotter.set_pen_width(index, width)

    def cmd_sp(self, args: list[bytes]):
        """Select pen."""
        if len(args):
            self.plotter.set_current_pen(to_int(args[0], 1))

    def cmd_np(self, args: list[bytes]):
        """Set number of pens."""
        if len(args):
            self.plotter.set_max_pen_count(to_int(args[0], 2))

    # pen movement:
    def cmd_pd(self, args: list[bytes]):
        """Lower pen down and plot lines."""
        self.plotter.pen_down()
        if len(args):
            self.plotter.plot_polyline(to_points(to_floats(args)))

    def cmd_pu(self, args: list[bytes]):
        """Lift pen up and move pen."""
        self.plotter.pen_up()
        if len(args):
            self.plotter.plot_polyline(to_points(to_floats(args)))

    def cmd_pa(self, args: list[bytes]):
        """Place pen absolute. Plots polylines if pen is down."""
        self.plotter.set_absolute_mode()
        if len(args):
            self.plotter.plot_polyline(to_points(to_floats(args)))

    def cmd_pr(self, args: list[bytes]):
        """Place pen relative.Plots polylines if pen is down."""
        self.plotter.set_relative_mode()
        if len(args):
            self.plotter.plot_polyline(to_points(to_floats(args)))

    # plot commands:
    def cmd_ci(self, args: list[bytes]):
        """Plot full circle."""
        if len(args):
            self.plotter.push_pen_state()
            # implicit pen down!
            self.plotter.pen_down()
            radius = to_float(args[0], 1.0)
            self.plotter.plot_abs_circle(radius)
            self.plotter.pop_pen_state()
        else:
            self.add_error("invalid arguments for CI command")

    def cmd_bz(self, args: list[bytes]):
        """Plot cubic Bezier curves with absolute user coordinates."""
        self._bezier_out(args, self.plotter.plot_abs_cubic_bezier)

    def cmd_br(self, args: list[bytes]):
        """Plot cubic Bezier curves with relative user coordinates."""
        self._bezier_out(args, self.plotter.plot_rel_cubic_bezier)

    @staticmethod
    def _bezier_out(args: list[bytes], output_method):
        kind = 0
        ctrl1 = NULLVEC2
        ctrl2 = NULLVEC2
        for point in to_points(to_floats(args)):
            if kind == 0:
                ctrl1 = point
            elif kind == 1:
                ctrl2 = point
            elif kind == 2:
                end = point
                output_method(ctrl1, ctrl2, end)
            kind = (kind + 1) % 3

    def cmd_pe(self, args: list[bytes]):
        """Plot Polyline Encoded."""
        if len(args):
            data = args[0]
        else:
            self.add_error("invalid arguments for PE command")
            return

        plotter = self.plotter
        # The last pen up/down state remains after leaving the PE command.
        pen_down = True
        # Ignores and preserves the current absolute/relative mode of the plotter.
        absolute = False
        decimal_places = 0
        base = 64
        index = 0
        length = len(data)
        point_queue: list[Vec2] = []

        while index < length:
            char = data[index]
            if char in b":<>=7":
                index += 1
                if char == 58:  # ":" - select pen
                    values, index = pe_decode(data, base=base, start=index)
                    plotter.set_current_pen(int(values[0]))
                    if len(values) > 1:
                        point_queue.extend(to_points(values[1:]))
                elif char == 60:  # "<" -  pen up and goto coordinates
                    pen_down = False
                elif char == 62:  # ">" - fractional data
                    values, index = pe_decode(data, base=base, start=index)
                    decimal_places = int(values[0])
                    if len(values) > 1:
                        point_queue.extend(to_points(values[1:]))
                elif char == 61:  # "=" - next coordinates are absolute
                    absolute = True
                elif char == 55:  # "7" - 7-bit mode
                    base = 32
            else:
                values, index = pe_decode(
                    data, decimal_places=decimal_places, base=base, start=index
                )
                point_queue.extend(to_points(values))

            if point_queue:
                plotter.pen_down()
                if absolute:
                    # next point is absolute: make relative
                    point_queue[0] = point_queue[0] - plotter.user_location
                if not pen_down:
                    target = point_queue.pop(0)
                    plotter.move_to_rel(target)
                    if not point_queue:  # last point in queue
                        plotter.pen_up()
                if point_queue:
                    plotter.plot_rel_polyline(point_queue)
                    point_queue.clear()
                pen_down = True
                absolute = False

    # polygon mode:
    def cmd_pm(self, args: list[bytes]) -> None:
        """Enter/Exit polygon mode."""
        status = 0
        if len(args):
            status = to_int(args[0], status)
        if status == 2:
            self.exit_polygon_mode()
        else:
            self.enter_polygon_mode(status)

    def cmd_fp(self, args: list[bytes]) -> None:
        """Plot filled polygon."""
        fill_method = 0
        if len(args):
            fill_method = to_int(args[0], fill_method)

        paths = self.polygon_buffer.get_paths(fill_method)
        location = self.polygon_buffer.user_location
        self.plotter.plot_filled_polygon(paths, fill_method)
        self.plotter.move_to_abs(location)

    def cmd_ep(self, _) -> None:
        """Plot edged polygon."""
        paths = self.polygon_buffer.get_paths(0)
        location = self.polygon_buffer.user_location
        self.plotter.plot_outline_polygon(paths)
        self.plotter.move_to_abs(location)


def to_floats(args: Iterable[bytes]) -> Iterator[float]:
    for arg in args:
        try:
            yield float(arg)
        except ValueError:
            pass


def to_ints(args: Iterable[bytes]) -> Iterator[int]:
    for arg in args:
        try:
            yield int(arg)
        except ValueError:
            pass


def to_points(values: Iterable[float]) -> list[Vec2]:
    points: list[Vec2] = []
    append_point = False
    buffer: float = 0.0
    for value in values:
        if append_point:
            points.append(Vec2(buffer, value))
            append_point = False
        else:
            buffer = value
            append_point = True
    return points


def to_float(s: bytes, default=0.0) -> float:
    try:
        return float(s)
    except ValueError:
        return default


def to_int(s: bytes, default=0) -> int:
    try:
        return int(s)
    except ValueError:
        return default
