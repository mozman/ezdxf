# Copyright (c) 2020-2021, Matthew Broadway
# License: MIT License
import math
from typing import (
    Iterable,
    TYPE_CHECKING,
    Optional,
    Dict,
    SupportsFloat,
    Union,
    Any,
)
from collections import defaultdict
from functools import lru_cache

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.textpath import TextPath
import numpy as np

from ezdxf.addons.drawing.backend import Backend, prepare_string_for_rendering
from ezdxf.addons.drawing.properties import Properties, LayoutProperties
from ezdxf.addons.drawing.type_hints import FilterFunc
from ezdxf.tools.fonts import FontMeasurements
from ezdxf.addons.drawing.type_hints import Color
from ezdxf.tools import fonts
from ezdxf.math import Vec3, Matrix44
from ezdxf.path import Command
from ezdxf.render.linetypes import LineTypeRenderer as EzdxfLineTypeRenderer
from .matplotlib_hatch import HATCH_NAME_MAPPING
from .line_renderer import AbstractLineRenderer

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
MATPLOTLIB_DEFAULT_PARAMS: Dict[str, Union[SupportsFloat, str]] = {}


def get_params(params: Optional[Dict]) -> Dict:
    default_params = dict(MATPLOTLIB_DEFAULT_PARAMS)
    default_params.update(params or {})
    return default_params


class MatplotlibBackend(Backend):
    def __init__(
        self,
        ax: plt.Axes,
        *,
        adjust_figure: bool = True,
        font: FontProperties = FontProperties(),
        use_text_cache: bool = True,
        params: Dict = None,
    ):
        super().__init__(get_params(params))
        self.ax = ax
        self._adjust_figure = adjust_figure
        self._scale_dashes_backup = plt.rcParams["lines.scale_dashes"]
        # Disable internal line style scaling by matplotlib
        plt.rcParams["lines.scale_dashes"] = False

        # like set_axis_off, except that the face_color can still be set
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)
        for s in self.ax.spines.values():
            s.set_visible(False)

        self.ax.autoscale(False)
        self.ax.set_aspect("equal", "datalim")
        self._current_z = 0
        self._text_renderer = TextRenderer(font, use_text_cache)

        # Setup line rendering component:
        self._line_renderer: MatplotlibLineRenderer
        if self.linetype_renderer == "ezdxf":
            # This linetype renderer should only be used by "hardcopy" backends!
            # It is just too slow for interactive backends, and the result of
            # the matplotlib line rendering is optimized for displays.
            self._line_renderer = EzdxfLineRenderer(self)
        else:
            self._line_renderer = InternalLineRenderer(self)

    def clear_text_cache(self):
        self._text_renderer.clear_cache()

    def _get_z(self) -> int:
        z = self._current_z
        self._current_z += 1
        return z

    def set_background(self, color: Color):
        self.ax.set_facecolor(color)

    def draw_point(self, pos: Vec3, properties: Properties):
        """Draw a real dimensionless point."""
        color = properties.color
        self.ax.scatter([pos.x], [pos.y], s=0.1, c=color, zorder=self._get_z())

    def draw_line(self, start: Vec3, end: Vec3, properties: Properties):
        # matplotlib draws nothing for a zero-length line:
        if start.isclose(end):
            self.draw_point(start, properties)
        else:
            self._line_renderer.draw_line(start, end, properties, self._get_z())

    def draw_path(self, path, properties: Properties):
        self._line_renderer.draw_path(path, properties, self._get_z())

    def draw_filled_paths(
        self,
        paths: Iterable[Path],
        holes: Iterable[Path],
        properties: Properties,
    ):
        fill, hatch = self._get_filling(properties)
        if fill is False and hatch is None:
            return
        if hatch:
            linewidth = self._line_renderer.lineweight(properties)
        else:
            linewidth = 0
        vertices = []
        codes = []
        for path in paths:
            try:
                path = path.counter_clockwise()
            except ValueError:  # cannot detect path orientation
                continue
            v1, c1 = _get_path_patch_data(path)
            vertices.extend(v1)
            codes.extend(c1)

        for hole in holes:
            try:
                hole = hole.clockwise()
            except ValueError:  # cannot detect path orientation
                continue
            v1, c1 = _get_path_patch_data(hole)
            vertices.extend(v1)
            codes.extend(c1)

        patch = PathPatch(
            Path(vertices, codes),
            color=properties.color,
            linewidth=linewidth,
            fill=fill,
            hatch=hatch,
            zorder=self._get_z(),
        )
        self.ax.add_patch(patch)

    def draw_filled_polygon(
        self, points: Iterable[Vec3], properties: Properties
    ):
        self.ax.fill(
            *zip(*((p.x, p.y) for p in points)),
            color=properties.color,
            linewidth=0,
            zorder=self._get_z(),
        )

    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
    ):
        if not text.strip():
            return  # no point rendering empty strings
        font_properties = self.get_font_properties(properties.font)
        assert self.current_entity is not None
        text = prepare_string_for_rendering(text, self.current_entity.dxftype())
        transformed_path = _transform_path(
            self._text_renderer.get_text_path(text, font_properties),
            Matrix44.scale(
                self._text_renderer.get_scale(cap_height, font_properties)
            )
            @ transform,
        )
        self.ax.add_patch(
            PathPatch(
                transformed_path,
                facecolor=properties.color,
                linewidth=0,
                zorder=self._get_z(),
            )
        )

    @lru_cache(maxsize=256)  # fonts.Font is a named tuple
    def get_font_properties(self, font: fonts.FontFace) -> FontProperties:
        font_properties = self._text_renderer.default_font
        if font:
            # Font-definitions are created by the matplotlib FontManger(),
            # but stored as json file and could be altered by an user:
            try:
                font_properties = FontProperties(
                    family=font.family,
                    style=font.style,
                    stretch=font.stretch,
                    weight=font.weight,
                )
            except ValueError:
                pass
        return font_properties

    def get_font_measurements(
        self, cap_height: float, font: fonts.FontFace = None
    ) -> FontMeasurements:
        return self._text_renderer.get_font_measurements(
            self.get_font_properties(font)
        ).scale_from_baseline(desired_cap_height=cap_height)

    def get_text_line_width(
        self, text: str, cap_height: float, font: fonts.FontFace = None
    ) -> float:
        if not text.strip():
            return 0
        dxftype = (
            self.current_entity.dxftype() if self.current_entity else "TEXT"
        )
        text = prepare_string_for_rendering(text, dxftype)
        font_properties = self.get_font_properties(font)
        path = self._text_renderer.get_text_path(text, font_properties)
        return max(x for x, y in path.vertices) * self._text_renderer.get_scale(
            cap_height, font_properties
        )

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
                self.ax.get_figure().set_size_inches(
                    width, height, forward=True
                )
        plt.rcParams["lines.scale_dashes"] = self._scale_dashes_backup

    def _get_filling(self, properties: Properties):
        fill = True
        hatch: Any = None
        assert properties.filling is not None
        name = properties.filling.name.upper()
        if properties.filling.type == 1 and name != "SOLID":
            if self.hatch_pattern == 0:
                # Disable hatch patterns
                fill = False
                hatch = False
            elif self.hatch_pattern == 1:
                # Use predefined hatch pattern by name matching:
                fill = False
                hatch = HATCH_NAME_MAPPING.get(name, r"\\\\")
            else:
                # Draw hatch pattern as solid filling
                fill = True
                hatch = False
        return fill, hatch


def _transform_path(path: Path, transform: Matrix44) -> Path:
    vertices = transform.transform_vertices(
        [Vec3(x, y) for x, y in path.vertices]
    )
    return Path([(v.x, v.y) for v in vertices], path.codes)


class TextRenderer:
    def __init__(self, font: FontProperties, use_cache: bool):
        self._default_font = font
        self._use_cache = use_cache

        # Each font has its own text path cache
        # key is hash(FontProperties)
        self._text_path_cache: Dict[int, Dict[str, TextPath]] = defaultdict(
            dict
        )

        # Each font has its own font measurements cache
        # key is hash(FontProperties)
        self._font_measurement_cache: Dict[int, FontMeasurements] = {}

    @property
    def default_font(self) -> FontProperties:
        return self._default_font

    def clear_cache(self):
        self._text_path_cache.clear()

    def get_scale(
        self, desired_cap_height: float, font: FontProperties
    ) -> float:
        return desired_cap_height / self.get_font_measurements(font).cap_height

    def get_font_measurements(self, font: FontProperties) -> FontMeasurements:
        # None is the default font.
        key = hash(font)
        measurements = self._font_measurement_cache.get(key)
        if measurements is None:
            upper_x = self.get_text_path("X", font).vertices[:, 1].tolist()
            lower_x = self.get_text_path("x", font).vertices[:, 1].tolist()
            lower_p = self.get_text_path("p", font).vertices[:, 1].tolist()
            baseline = min(lower_x)
            measurements = FontMeasurements(
                baseline=baseline,
                cap_height=max(upper_x) - baseline,
                x_height=max(lower_x) - baseline,
                descender_height=baseline - min(lower_p),
            )
            self._font_measurement_cache[key] = measurements
        return measurements

    def get_text_path(self, text: str, font: FontProperties) -> TextPath:
        # None is the default font
        cache = self._text_path_cache[hash(font)]  # defaultdict(dict)
        path = cache.get(text, None)
        if path is None:
            if font is None:
                font = self._default_font
            # must replace $ with \$ to avoid matplotlib interpreting it as math text
            path = TextPath(
                (0, 0),
                text.replace("$", "\\$"),
                size=1,
                prop=font,
                usetex=False,
            )
            if self._use_cache:
                cache[text] = path
        return path


def _get_path_patch_data(path):
    codes = [Path.MOVETO]
    vertices = [path.start]
    for cmd in path:
        if cmd.type == Command.LINE_TO:
            codes.append(Path.LINETO)
            vertices.append(cmd.end)
        elif cmd.type == Command.CURVE4_TO:
            codes.extend(CURVE4x3)
            vertices.extend((cmd.ctrl1, cmd.ctrl2, cmd.end))
        else:
            raise ValueError(f"Invalid command: {cmd.type}")
    return [(p.x, p.y) for p in vertices], codes


def qsave(
    layout: "Layout",
    filename: str,
    *,
    bg: Optional[Color] = None,
    fg: Optional[Color] = None,
    dpi: int = 300,
    backend: str = "agg",
    params: dict = None,
    filter_func: FilterFunc = None,
) -> None:
    """Quick and simplified render export by matplotlib.

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
        params: matplotlib backend parameters
        filter_func: filter function which takes a DXFGraphic object as input
            and returns ``True`` if the entity should be drawn or ``False`` if
            the entity should be ignored

    .. versionadded:: 0.14

    .. versionadded:: 0.15
        added argument `params` to pass parameters to the matplotlib backend

    .. versionchanged:: 0.16
        removed arguments `ltype` and `lineweight_scaling`

    .. versionadded:: 0.17
        added argument `filter_func` to filter DXF entities

    """
    from .properties import RenderContext
    from .frontend import Frontend
    import matplotlib

    # Set the backend to prevent warnings about GUIs being opened from a thread
    # other than the main thread.
    old_backend = matplotlib.get_backend()
    matplotlib.use(backend)
    params = params or {}

    # Let the user choose a minimum lineweight:
    if "min_lineweight" not in params:
        # If not set by user, use ~1 pixel
        params["min_lineweight"] = 72 / dpi

    try:
        fig: plt.Figure = plt.figure()
        ax: plt.Axes = fig.add_axes((0, 0, 1, 1))
        ctx = RenderContext(layout.doc)
        layout_properties = LayoutProperties.from_layout(layout)
        if bg is not None:
            layout_properties.set_colors(bg, fg)
        out = MatplotlibBackend(ax, params=params)
        Frontend(ctx, out).draw_layout(
            layout,
            finalize=True,
            filter_func=filter_func,
            layout_properties=layout_properties,
        )
        # transparent=True sets the axes color to fully transparent
        # facecolor sets the figure color
        # (semi-)transparent axes colors do not produce transparent outputs
        # but (semi-)transparent figure colors do.
        fig.savefig(
            filename, dpi=dpi, facecolor=ax.get_facecolor(), transparent=True
        )
        plt.close(fig)
    finally:
        matplotlib.use(old_backend)


class MatplotlibLineRenderer(AbstractLineRenderer):
    @property
    def lineweight_scaling(self) -> float:
        return self._backend.lineweight_scaling * POINTS

    # noinspection PyUnresolvedReferences
    @property
    def ax(self) -> plt.Axes:
        return self._backend.ax  # type: ignore # MatplotlibBackend


# Scaling factor for internal renderer, just guessing here:
ISO_LIN_PATTERN_FACTOR = 3.0 * POINTS
ANSI_LIN_PATTERN_FACTOR = ISO_LIN_PATTERN_FACTOR * 2.54


class InternalLineRenderer(MatplotlibLineRenderer):
    """matplotlib internal linetype rendering, which is oriented on the output
    medium and dpi: This method is simpler and faster but may not replicate the
    results of CAD applications.
    """

    def draw_line(
        self, start: Vec3, end: Vec3, properties: Properties, z: float
    ):
        self.ax.add_line(
            Line2D(
                (start.x, end.x),
                (start.y, end.y),
                linewidth=self.lineweight(properties),
                linestyle=self.linetype(properties),
                color=properties.color,
                zorder=z,
            )
        )

    def draw_path(self, path, properties: Properties, z: float):
        vertices, codes = _get_path_patch_data(path)
        patch = PathPatch(
            Path(vertices, codes),
            linewidth=self.lineweight(properties),
            linestyle=self.linetype(properties),
            fill=False,
            color=properties.color,
            zorder=z,
        )
        self.ax.add_patch(patch)

    @property
    def measurement_scale(self) -> float:
        return (
            ISO_LIN_PATTERN_FACTOR
            if self.measurement
            else ANSI_LIN_PATTERN_FACTOR
        )

    def create_pattern(self, properties: Properties, scale: float):
        """Return matplotlib line style tuple: (offset, on_off_sequence) or
        "solid".

        See examples: https://matplotlib.org/gallery/lines_bars_and_markers/linestyles.html

        """
        if len(properties.linetype_pattern) < 2:
            return "solid"
        else:
            pattern = np.round(np.array(properties.linetype_pattern) * scale)
            pattern = [max(element, 1) for element in pattern]
            if len(pattern) % 2:
                pattern.pop()
            return 0, pattern


class EzdxfLineRenderer(MatplotlibLineRenderer):
    """Replicate AutoCAD linetype rendering oriented on drawing units and
    various ltscale factors. This rendering method break lines into small
    segments which causes a longer rendering time!
    """

    def draw_line(
        self, start: Vec3, end: Vec3, properties: Properties, z: float
    ):
        pattern = self.pattern(properties)
        lineweight = self.lineweight(properties)
        render_linetypes = bool(self.linetype_scaling)
        color = properties.color
        if len(pattern) < 2 or not render_linetypes:
            self.ax.add_line(
                Line2D(
                    (start.x, end.x),
                    (start.y, end.y),
                    linewidth=lineweight,
                    color=color,
                    zorder=z,
                )
            )
        else:
            renderer = EzdxfLineTypeRenderer(pattern)
            lines = LineCollection(
                [
                    ((s.x, s.y), (e.x, e.y))
                    for s, e in renderer.line_segment(start, end)
                ],
                linewidths=lineweight,
                color=color,
                zorder=z,
            )
            lines.set_capstyle("butt")
            self.ax.add_collection(lines)

    def draw_path(self, path, properties: Properties, z: float):
        pattern = self.pattern(properties)
        lineweight = self.lineweight(properties)
        render_linetypes = bool(self.linetype_scaling)
        color = properties.color
        if len(pattern) < 2 or not render_linetypes:
            vertices, codes = _get_path_patch_data(path)
            patch = PathPatch(
                Path(vertices, codes),
                linewidth=lineweight,
                color=color,
                fill=False,
                zorder=z,
            )
            self.ax.add_patch(patch)
        else:
            renderer = EzdxfLineTypeRenderer(pattern)
            segments = renderer.line_segments(
                path.flattening(self.max_flattening_distance, segments=16)
            )
            lines = LineCollection(
                [((s.x, s.y), (e.x, e.y)) for s, e in segments],
                linewidths=lineweight,
                color=color,
                zorder=z,
            )
            lines.set_capstyle("butt")
            self.ax.add_collection(lines)
