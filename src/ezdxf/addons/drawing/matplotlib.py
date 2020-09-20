# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import math
from typing import Iterable, TYPE_CHECKING, Optional, Dict
from enum import Enum
import abc

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path
from matplotlib.textpath import TextPath
import numpy as np

from ezdxf.addons.drawing.backend import Backend, prepare_string_for_rendering
from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.text import FontMeasurements
from ezdxf.addons.drawing.type_hints import Color
from ezdxf.math import Vector, Matrix44
from ezdxf.render import Command
from ezdxf.render.linetypes import LineTypeRenderer as EzdxfLineTypeRenderer

if TYPE_CHECKING:
    from ezdxf.eztypes import Layout

# matplotlib docs: https://matplotlib.org/index.html

# line style:
# https://matplotlib.org/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.set_linestyle
# https://matplotlib.org/gallery/lines_bars_and_markers/linestyles.html

# line width:
# https://matplotlib.org/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.set_linewidth
# points unit (pt), 1pt = 1/72 inch, 1pt = 0.3527mm
POINTS = 1.0 / 0.3527  # mm -> points
CURVE4x3 = (Path.CURVE4, Path.CURVE4, Path.CURVE4)


class LineTypeRendering(Enum):
    # matplotlib internal linetype rendering, which is oriented on the output
    # medium and dpi:
    # This method is simpler and faster but may not replicate the results of
    # CAD applications.
    internal = 1

    # Replicate AutoCAD linetype rendering oriented on drawing units and
    # various ltscale factors:
    # Warning: this rendering method break lines into small segments which
    # requires a longer runtime and memory!
    ezdxf = 2


class MatplotlibBackend(Backend):
    def __init__(self, ax: plt.Axes,
                 *,
                 adjust_figure: bool = True,
                 point_size: float = 2.0,
                 point_size_relative: bool = True,
                 font: FontProperties = FontProperties(),
                 use_text_cache: bool = True,
                 linetype_rendering: str = 'internal',
                 linetype_scaling: float = None,
                 ):
        super().__init__()
        self.ax = ax
        self._adjust_figure = adjust_figure
        self._scale_dashes_backup = plt.rcParams['lines.scale_dashes']
        # Disable internal line style scaling by matplotlib
        plt.rcParams['lines.scale_dashes'] = False

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
        self._text = TextRenderer(font, use_text_cache)

        # Detect linetype rendering type:
        try:
            linetype_rendering = LineTypeRendering[
                linetype_rendering.lower()]
        except KeyError:
            raise ValueError(
                f'Unknown linetype rendering type: {linetype_rendering}')

        # Setup line rendering component:
        if linetype_rendering == LineTypeRendering.internal:
            self._line_renderer = InternalLineRenderer(linetype_scaling)
        elif linetype_rendering == LineTypeRendering.ezdxf:
            # This linetype renderer should only be used by "hardcopy" backends!
            # It is just too slow for interactive backends, and the result of
            # the matplotlib line rendering is optimized for displays.
            self._line_renderer = EzdxfLineRenderer(
                # The `min_length` and `max_distance` arguments should be based
                # on the output dpi setting.
                linetype_scaling, min_length=0.01, max_distance=0.01)

    def clear_text_cache(self):
        self._text.clear_cache()

    def _get_z(self) -> int:
        z = self._current_z
        self._current_z += 1
        return z

    def set_background(self, color: Color):
        self.ax.set_facecolor(color)

    def draw_line(self, start: Vector, end: Vector, properties: Properties):
        self._line_renderer.draw_line(
            self.ax, start, end, properties, self._get_z())

    def draw_path(self, path, properties: Properties):
        self._line_renderer.draw_path(self.ax, path, properties, self._get_z())

    def draw_point(self, pos: Vector, properties: Properties):
        color = properties.color
        if self.point_size_relative:
            self.ax.scatter([pos.x], [pos.y], s=self.point_size, c=color,
                            zorder=self._get_z())
        else:
            self.ax.add_patch(Circle((pos.x, pos.y), radius=self.point_size,
                                     facecolor=color, edgecolor=None,
                                     zorder=self._get_z()))

    def draw_filled_polygon(self, points: Iterable[Vector],
                            properties: Properties):
        self.ax.fill(*zip(*((p.x, p.y) for p in points)),
                     color=properties.color, zorder=self._get_z())

    def draw_text(self, text: str, transform: Matrix44, properties: Properties,
                  cap_height: float):
        if not text.strip():
            return  # no point rendering empty strings
        text = prepare_string_for_rendering(text, self.current_entity.dxftype())
        transformed_path = _transform_path(
            self._text.get_text_path(text),
            Matrix44.scale(self._text.get_scale(cap_height)) @ transform
        )
        self.ax.add_patch(
            PathPatch(transformed_path, facecolor=properties.color, linewidth=0,
                      zorder=self._get_z()))

    def get_font_measurements(self, cap_height: float,
                              font: str = None) -> FontMeasurements:
        return self._text.font_measurements.scale_from_baseline(
            desired_cap_height=cap_height)

    def get_text_line_width(self, text: str, cap_height: float,
                            font: str = None) -> float:
        if not text.strip():
            return 0
        dxftype = self.current_entity.dxftype() if self.current_entity else 'TEXT'
        text = prepare_string_for_rendering(text, dxftype)
        path = self._text.get_text_path(text)
        return max(x for x, y in path.vertices) * self._text.get_scale(cap_height)

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
                self.ax.get_figure().set_size_inches(width, height,
                                                     forward=True)
        plt.rcParams['lines.scale_dashes'] = self._scale_dashes_backup


def _transform_path(path: Path, transform: Matrix44) -> Path:
    vertices = transform.transform_vertices(
        [Vector(x, y) for x, y in path.vertices])
    return Path([(v.x, v.y) for v in vertices], path.codes)


class TextRenderer:
    def __init__(self, font: FontProperties, use_cache: bool):
        self._font = font
        self._use_cache = use_cache
        self._cache: Dict[str, TextPath] = {}
        self._font_measurements = self._get_font_measurements()

    def clear_cache(self):
        self._cache.clear()

    @property
    def font_measurements(self) -> FontMeasurements:
        return self._font_measurements

    def get_scale(self, desired_cap_height: float) -> float:
        return desired_cap_height / self._font_measurements.cap_height

    def _get_font_measurements(self) -> FontMeasurements:
        upper_x = self.get_text_path('X').vertices[:, 1].tolist()
        lower_x = self.get_text_path('x').vertices[:, 1].tolist()
        lower_p = self.get_text_path('p').vertices[:, 1].tolist()
        return FontMeasurements(
            baseline=min(lower_x),
            cap_top=max(upper_x),
            x_top=max(lower_x),
            bottom=min(lower_p)
        )

    def get_text_path(self, text: str) -> TextPath:
        path = self._cache.get(text, None)
        if path is None:
            # must replace $ with \$ to avoid matplotlib interpreting it as math text
            path = TextPath((0, 0), text.replace('$', '\\$'), size=1, prop=self._font, usetex=False)
            if self._use_cache:
                self._cache[text] = path
        return path


def _get_line_style_pattern(properties: Properties, scale: float):
    """ Return matplotlib line style tuple: (offset, on_off_sequence)

    See examples: https://matplotlib.org/gallery/lines_bars_and_markers/linestyles.html

    """
    if len(properties.linetype_pattern) < 2:
        return 'solid'
    else:
        scale = scale * properties.linetype_scale
        pattern = np.round(np.array(properties.linetype_pattern) * scale)
        pattern = [max(element, 1) for element in pattern]
        if len(pattern) % 2:
            pattern.pop()
        return 0, pattern


def _get_path_patch_data(path):
    codes = [Path.MOVETO]
    vertices = [path.start]
    for cmd in path:
        if cmd.type == Command.LINE_TO:
            codes.append(Path.LINETO)
            vertices.append(cmd.end)
        elif cmd.type == Command.CURVE_TO:
            codes.extend(CURVE4x3)
            vertices.extend((cmd.ctrl1, cmd.ctrl2, cmd.end))
        else:
            raise ValueError(f'Invalid command: {cmd.type}')
    return [(p.x, p.y) for p in vertices], codes


def qsave(layout: 'Layout', filename: str, *,
          bg: Optional[Color] = None,
          fg: Optional[Color] = None,
          dpi: int = 300,
          backend: str = 'agg',
          ltype: str = 'internal',
          ) -> None:
    """ Quick and simplified render export by matplotlib.

    Args:
        layout: modelspace or paperspace layout to export
        filename: export filename, file extension determines the format e.g.
            "image.png" to save in PNG format.
        bg: override default background color in hex format #RRGGBB or #RRGGBBAA,
            e.g. use bg="#FFFFFF00" to get a transparent background and a black
            foreground color (ACI=7), because a white background #FFFFFF gets a
            black foreground color or vice versa bg="#00000000" for a transparent
            (black) background and a white foreground color.
        fg: override default foreground color in hex format #RRGGBB or #RRGGBBAA,
            requires also `bg` argument. There is no explicit foreground color
            in DXF defined (also not a background color), but the ACI color 7
            has already a variable color value, black on a light background and
            white on a dark background, this argument overrides this (ACI=7)
            default color value.
        dpi: image resolution (dots per inches).
        backend: the matplotlib rendering backend to use (agg, cairo, svg etc)
            (see documentation for `matplotlib.use() <https://matplotlib.org/3.1.1/api/matplotlib_configuration_api.html?highlight=matplotlib%20use#matplotlib.use>`_
            for a complete list of backends)
        ltype: "internal" to use the matplotlib dpi based linetype rendering,
            "ezdxf" to use a drawing unit base linetype rendering.

    .. versionadded:: 0.14

    """
    from .properties import RenderContext
    from .frontend import Frontend
    import matplotlib
    # set the backend to prevent warnings about GUIs being opened from a thread
    # other than the main thread
    old_backend = matplotlib.get_backend()
    matplotlib.use(backend)
    try:
        fig: plt.Figure = plt.figure()
        ax: plt.Axes = fig.add_axes((0, 0, 1, 1))
        ctx = RenderContext(layout.doc)
        ctx.set_current_layout(layout)
        if bg is not None:
            ctx.current_layout.set_colors(bg, fg)
        out = MatplotlibBackend(ax, linetype_rendering=ltype)
        Frontend(ctx, out).draw_layout(layout, finalize=True)
        # transparent=True sets the axes color to fully transparent
        # facecolor sets the figure color
        # (semi-)transparent axes colors do not produce transparent outputs
        # but (semi-)transparent figure colors do.
        fig.savefig(filename, dpi=dpi,
                    facecolor=ax.get_facecolor(), transparent=True)
        plt.close(fig)
    finally:
        matplotlib.use(old_backend)


class AbstractLineRenderer:
    def __init__(self, scale: Optional[float] = None):
        self._pattern_cache = dict()
        self._scale = scale

    @abc.abstractmethod
    def draw_line(self, ax: plt.Axes, start: Vector, end: Vector,
                  properties: Properties, z: float):
        ...

    @abc.abstractmethod
    def draw_path(self, ax: plt.Axes, path, properties: Properties, z: float):
        ...

    @abc.abstractmethod
    def create_pattern(self, properties: Properties, scale: float):
        ...

    def pattern(self, properties: Properties):
        """ Get pattern - implements pattern caching. """
        scale = self._scale * properties.linetype_scale
        key = (properties.linetype_name, scale)
        pattern_ = self._pattern_cache.get(key)
        if pattern_ is None:
            pattern_ = self.create_pattern(properties, scale)
            self._pattern_cache[key] = pattern_
        return pattern_


class InternalLineRenderer(AbstractLineRenderer):
    def __init__(self, scale: Optional[float] = None):
        if scale is None:
            # Arbitrary choice, may change in the future!
            scale = 10.0 * POINTS
        super().__init__(scale)

    def draw_line(self, ax: plt.Axes, start: Vector, end: Vector,
                  properties: Properties, z: float):
        ax.add_line(
            Line2D(
                (start.x, end.x), (start.y, end.y),
                linewidth=properties.lineweight * POINTS,
                linestyle=self.pattern(properties),
                color=properties.color,
                zorder=z,
            ))

    def draw_path(self, ax: plt.Axes, path, properties: Properties, z: float):
        vertices, codes = _get_path_patch_data(path)
        patch = PathPatch(
            Path(vertices, codes),
            linewidth=properties.lineweight * POINTS,
            linestyle=self.pattern(properties),
            color=properties.color,
            fill=bool(properties.filling),
            zorder=z
        )
        ax.add_patch(patch)

    def create_pattern(self, properties: Properties, scale: float):
        """ Return matplotlib line style tuple: (offset, on_off_sequence) or
        "solid".

        See examples: https://matplotlib.org/gallery/lines_bars_and_markers/linestyles.html

        """
        if len(properties.linetype_pattern) < 2:
            return 'solid'
        else:
            pattern = np.round(np.array(properties.linetype_pattern) * scale)
            pattern = [max(element, 1) for element in pattern]
            if len(pattern) % 2:
                pattern.pop()
            return 0, pattern


class EzdxfLineRenderer(AbstractLineRenderer):
    def __init__(self, scale: Optional[float] = None,
                 min_length: float = 0.1,
                 max_distance: float = 0.01):
        if scale is None:
            scale = 1.0
        super().__init__(scale)
        # Minimum dash length to be displayed by matplotlib
        self._min_dash_length = min_length
        # Maximum distance for adaptive recursive curve flattening
        self._max_distance = max_distance

    def draw_line(self, ax: plt.Axes, start: Vector, end: Vector,
                  properties: Properties, z: float):
        pattern = self.pattern(properties)
        lineweight = properties.lineweight * POINTS
        color = properties.color
        if len(pattern) < 2:
            ax.add_line(
                Line2D(
                    (start.x, end.x), (start.y, end.y),
                    linewidth=lineweight,
                    color=color,
                    zorder=z,
                ))
        else:
            renderer = EzdxfLineTypeRenderer(pattern)
            for s, e in renderer.line_segment(start, end):
                ax.add_line(
                    Line2D(
                        (s.x, e.x), (s.y, e.y),
                        linewidth=lineweight,
                        color=color,
                        zorder=z,
                    ))

    def draw_path(self, ax: plt.Axes, path, properties: Properties, z: float):
        pattern = self.pattern(properties)
        lineweight = properties.lineweight * POINTS
        color = properties.color
        if len(pattern) < 2:
            vertices, codes = _get_path_patch_data(path)
            patch = PathPatch(
                Path(vertices, codes),
                linewidth=lineweight,
                color=color,
                fill=bool(properties.filling),
                zorder=z
            )
            ax.add_patch(patch)
        else:
            renderer = EzdxfLineTypeRenderer(pattern)
            for s, e in renderer.line_segments(
                    path.flattening(self._max_distance, segments=16)):
                ax.add_line(
                    Line2D(
                        (s.x, e.x), (s.y, e.y),
                        linewidth=lineweight,
                        color=color,
                        zorder=z,
                    ))

    def create_pattern(self, properties: Properties, scale: float):
        """ Returns simplified linetype tuple: on_off_sequence """
        if len(properties.linetype_pattern) < 2:
            return tuple()
        else:
            pattern = [max(e * scale, self._min_dash_length) for e in
                       properties.linetype_pattern]
            if len(pattern) % 2:
                pattern.pop()
            return pattern
