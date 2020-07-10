# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import math
from math import degrees
from typing import Optional, Tuple, Iterable

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.patches import Arc, Circle, PathPatch
from matplotlib.path import Path
from matplotlib.textpath import TextPath

from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.text import FontMeasurements
from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.type_hints import Color, Radians
from ezdxf.math import Vector, param_to_angle, Matrix44

# matplotlib docs: https://matplotlib.org/index.html

# line style:
# https://matplotlib.org/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.set_linestyle
# https://matplotlib.org/gallery/lines_bars_and_markers/linestyles.html

# line width:
# https://matplotlib.org/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.set_linewidth
# points unit (pt), 1pt = 1/72 inch, 1pt = 0.3527mm
POINTS = 1.0 / 0.3527  # mm -> points


class MatplotlibBackend(Backend):
    def __init__(self, ax: plt.Axes,
                 *,
                 adjust_figure: bool = True,
                 point_size: float = 2.0,
                 point_size_relative: bool = True,
                 font: FontProperties = FontProperties(),
                 ):
        super().__init__()
        self.ax = ax
        self._adjust_figure = adjust_figure

        # like set_axis_off, except that the face_color can still be set
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)
        for s in self.ax.spines.values():
            s.set_visible(False)

        self.ax.autoscale(False)
        self.ax.set_aspect('equal', 'datalim')
        self._current_z = 0
        self.point_size = point_size
        self.point_size_relative = point_size_relative
        self.font = font
        self._font_measurements = _get_font_measurements(font)

    def _get_z(self) -> int:
        z = self._current_z
        self._current_z += 1
        return z

    def set_background(self, color: Color):
        self.ax.set_facecolor(color)

    def draw_line(self, start: Vector, end: Vector, properties: Properties):
        self.ax.add_line(
            Line2D(
                (start.x, end.x), (start.y, end.y),
                linewidth=properties.lineweight * POINTS,
                color=properties.color,
                zorder=self._get_z()
            ))

    def draw_point(self, pos: Vector, properties: Properties):
        color = properties.color
        if self.point_size_relative:
            self.ax.scatter([pos.x], [pos.y], s=self.point_size, c=color, zorder=self._get_z())
        else:
            self.ax.add_patch(Circle((pos.x, pos.y), radius=self.point_size,
                                     facecolor=color, edgecolor=None, zorder=self._get_z()))

    def draw_filled_polygon(self, points: Iterable[Vector], properties: Properties):
        self.ax.fill(*zip(*((p.x, p.y) for p in points)), color=properties.color, zorder=self._get_z())

    def draw_text(self, text: str, transform: Matrix44, properties: Properties, cap_height: float):
        if not text:
            return  # no point rendering empty strings
        assert '\n' not in text, 'not a single line of text'
        scale = cap_height / self._font_measurements.cap_height
        path = _text_path(text, self.font)
        transformed_path = _transform_path(path, Matrix44.scale(scale) @ transform)
        self.ax.add_patch(PathPatch(transformed_path, facecolor=properties.color, linewidth=0, zorder=self._get_z()))

    def get_font_measurements(self, cap_height: float) -> FontMeasurements:
        return self._font_measurements.scale_from_baseline(desired_cap_height=cap_height)

    def get_text_line_width(self, text: str, cap_height: float) -> float:
        if not text:
            return 0
        assert '\n' not in text, 'not a single line of text'
        path = _text_path(text, self.font)
        scale = cap_height / self._font_measurements.cap_height
        transformed_xs = _transform_path(path, Matrix44.scale(scale)).vertices[:, 0].tolist()
        return max(transformed_xs)

    def draw_arc(self, center: Vector, width: float, height: float, angle: Radians,
                 draw_angles: Optional[Tuple[Radians, Radians]], properties: Properties):
        if min(width, height) < 1e-5:
            return  # matplotlib crashes if the arc has almost 0 size

        if draw_angles is None:
            start_degrees, end_degrees = 0, 360
        else:
            # draw angles are relative to `angle`. The arc is drawn anticlockwise from start to end.
            # draw_angles are *NOT* in the global coordinate system, but instead are angles inside the
            # local coordinate system defined by the major and minor axes of the ellipse
            # (where the ellipse looks like a circle)
            ratio = height / width
            start, end = param_to_angle(ratio, draw_angles[0]), param_to_angle(ratio, draw_angles[1])
            start_degrees, end_degrees = degrees(start), degrees(end)

        arc = Arc(
            (center.x, center.y), width, height,
            color=properties.color,
            linewidth=properties.lineweight * POINTS,
            angle=degrees(angle), theta1=start_degrees, theta2=end_degrees, zorder=self._get_z())
        self.ax.add_patch(arc)

    def clear(self):
        self.ax.clear()

    def finalize(self):
        super().finalize()
        self.ax.autoscale(True)
        if self._adjust_figure:
            minx, maxx = self.ax.get_xlim()
            miny, maxy = self.ax.get_ylim()
            data_width, data_height = maxx - minx, maxy - miny
            if not math.isclose(data_width, 0):
                width, height = plt.figaspect(data_height / data_width)
                self.ax.get_figure().set_size_inches(width, height, forward=True)


def _transform_path(path: Path, transform: Matrix44) -> Path:
    vertices = transform.transform_vertices([Vector(x, y) for x, y in path.vertices])
    return Path([(v.x, v.y) for v in vertices], path.codes)


def _text_path(text: str, font: FontProperties) -> TextPath:
    return TextPath((0, 0), text, size=1, prop=font)


def _get_font_measurements(font: FontProperties = FontProperties()) -> "FontMeasurements":
    upper_x = _text_path('X', font).vertices[:, 1].tolist()
    lower_x = _text_path('x', font).vertices[:, 1].tolist()
    lower_p = _text_path('p', font).vertices[:, 1].tolist()
    return FontMeasurements(
        baseline=min(lower_x),
        cap_top=max(upper_x),
        x_top=max(lower_x),
        bottom=min(lower_p)
    )
