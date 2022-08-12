# Copyright (c) 2020-2022, Matthew Broadway
# License: MIT License
import math
from abc import ABCMeta
from typing import (
    Iterable,
    Iterator,
    TYPE_CHECKING,
    Optional,
    Dict,
    List,
    Sequence,
    Tuple,
)
from collections import defaultdict
from functools import lru_cache
import logging

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
from ezdxf.math import Vec2, Vec3, Matrix44
from ezdxf.math.triangulation import mapbox_earcut_2d
import ezdxf.path

from .config import Configuration, LinePolicy, HatchPolicy
from .line_renderer import AbstractLineRenderer

if TYPE_CHECKING:
    from ezdxf.eztypes import Layout

logger = logging.getLogger("ezdxf")
# matplotlib docs: https://matplotlib.org/index.html

# line style:
# https://matplotlib.org/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.set_linestyle
# https://matplotlib.org/gallery/lines_bars_and_markers/linestyles.html

# line width:
# https://matplotlib.org/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.set_linewidth
# points unit (pt), 1pt = 1/72 inch, 1pt = 0.3527mm
POINTS = 1.0 / 0.3527  # mm -> points
CURVE4x3 = (Path.CURVE4, Path.CURVE4, Path.CURVE4)


class MatplotlibBackend(Backend):
    def __init__(
        self,
        ax: plt.Axes,
        *,
        adjust_figure: bool = True,
        font: FontProperties = FontProperties(),
        use_text_cache: bool = True,
    ):
        super().__init__()
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
        self._line_renderer: MatplotlibLineRenderer

    def configure(self, config: Configuration) -> None:
        if config.min_lineweight is None:
            # If not set by user, use ~1 pixel
            config = config.with_changes(
                min_lineweight=72 / self.ax.get_figure().dpi
            )
        super().configure(config)
        # LinePolicy.ACCURATE is handled by the frontend since v0.18.1
        self._line_renderer = InternalLineRenderer(
            config, self.ax, solid_only=(config.line_policy == LinePolicy.SOLID)
        )

    def clear_text_cache(self):
        self._text_renderer.clear_cache()

    def _get_z(self) -> int:
        z = self._current_z
        self._current_z += 1
        return z

    def set_background(self, color: Color):
        self.ax.set_facecolor(color)

    def set_clipping_path(
        self, path: ezdxf.path.Path = None, scale: float = 1.0
    ) -> bool:
        from matplotlib.transforms import Transform

        if path:
            # This does not work!!!
            mpl_path = ezdxf.path.to_matplotlib_path([path])
            self.ax.set_clip_path(mpl_path, Transform())
        else:
            self.ax.set_clip_path(None)
        return True  # confirm clipping support

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

    def draw_solid_lines(
        self,
        lines: Iterable[Tuple[Vec3, Vec3]],
        properties: Properties,
    ):
        """Fast method to draw a bunch of solid lines with the same properties."""
        color = properties.color
        lineweight = self._line_renderer.lineweight(properties)
        _lines = []
        point_x = []
        point_y = []
        z = self._get_z()
        for s, e in lines:
            if s.isclose(e):
                point_x.append(s.x)
                point_y.append(s.y)
            else:
                _lines.append(((s.x, s.y), (e.x, e.y)))

        self.ax.scatter(point_x, point_y, s=0.1, c=color, zorder=z)
        self.ax.add_collection(
            LineCollection(
                _lines,
                linewidths=lineweight,
                color=color,
                zorder=z,
                capstyle="butt",
            )
        )

    def draw_path(self, path: ezdxf.path.Path, properties: Properties):
        self._line_renderer.draw_path(path, properties, self._get_z())

    def draw_filled_paths(
        self,
        paths: Iterable[ezdxf.path.Path],
        holes: Iterable[ezdxf.path.Path],
        properties: Properties,
    ):
        # Hatch patterns are handled by the frontend since v0.18.1
        if self.config.hatch_policy == HatchPolicy.SHOW_OUTLINE:
            return
        linewidth = 0
        oriented_paths: List[ezdxf.path.Path] = []
        for path in paths:
            try:
                path = path.counter_clockwise()
            except ValueError:  # cannot detect path orientation
                continue
            oriented_paths.append(path)

        for hole in holes:
            try:
                hole = hole.clockwise()
            except ValueError:  # cannot detect path orientation
                continue
            oriented_paths.append(hole)

        try:
            patch = PathPatch(
                ezdxf.path.to_matplotlib_path(oriented_paths),
                color=properties.color,
                linewidth=linewidth,
                fill=True,
                zorder=self._get_z(),
            )
        except ValueError as e:
            logger.info(
                f"ignored matplotlib error in draw_filled_paths(): {str(e)}"
            )
        else:
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
        font_properties = self._text_renderer.get_font_properties(
            properties.font
        )
        assert self.current_entity is not None
        text = prepare_string_for_rendering(text, self.current_entity.dxftype())
        try:
            text_path = self._text_renderer.get_text_path(text, font_properties)
        except (RuntimeError, ValueError):
            return

        transformed_path = _transform_path(
            text_path,
            Matrix44.scale(
                self._text_renderer.get_scale(cap_height, font_properties)
            )
            @ transform,
        )
        try:
            patch = PathPatch(
                transformed_path,
                facecolor=properties.color,
                linewidth=0,
                zorder=self._get_z(),
            )
        except ValueError as e:
            logger.info(f"ignored matplotlib error in draw_text(): {str(e)}")
        else:
            self.ax.add_patch(patch)

    def get_font_measurements(
        self, cap_height: float, font: fonts.FontFace = None
    ) -> FontMeasurements:
        return self._text_renderer.get_font_measurements(
            self._text_renderer.get_font_properties(font)
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
        return self._text_renderer.get_text_line_width(text, cap_height, font)

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


def _transform_path(path: Path, transform: Matrix44) -> Path:
    vertices = transform.transform_vertices(
        [Vec3(x, y) for x, y in path.vertices]
    )
    return Path([(v.x, v.y) for v in vertices], path.codes)  # type: ignore


@lru_cache(maxsize=256)  # fonts.Font is a named tuple
def _get_font_properties(font: fonts.FontFace) -> Optional[FontProperties]:
    # Font-definitions are created by the matplotlib FontManger(),
    # but stored as json file and could be altered by an user:
    font_properties = None
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

    def get_font_properties(
        self, font: Optional[fonts.FontFace]
    ) -> FontProperties:
        if font is None:
            return self.default_font
        font_properties = _get_font_properties(font)
        if font_properties is None:
            return self.default_font
        return font_properties

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

    def get_text_line_width(
        self, text: str, cap_height: float, font: Optional[fonts.FontFace]
    ) -> float:
        font_properties = self.get_font_properties(font)
        try:
            path = self.get_text_path(text, font_properties)
        except (RuntimeError, ValueError):
            return 0.0
        return max(x for x, y in path.vertices) * self.get_scale(
            cap_height, font_properties
        )

    def get_ezdxf_path(
        self, text: str, font: FontProperties
    ) -> ezdxf.path.Path:
        try:
            text_path = self.get_text_path(text, font)
        except (RuntimeError, ValueError):
            return ezdxf.path.Path()
        return ezdxf.path.multi_path_from_matplotlib_path(text_path)

    def get_tessellation(
        self,
        text: str,
        font: FontProperties,
        *,
        max_flattening_distance: float = 0.01,
    ) -> Iterator[Sequence[Vec2]]:
        """Triangulate text into faces.

        !!! Does not work for any arbitrary text !!!
        """
        for polygon in ezdxf.path.nesting.group_paths(
            list(self.get_ezdxf_path(text, font).sub_paths())
        ):
            if len(polygon) == 0:
                continue
            exterior = polygon[0]
            holes = polygon[1:]
            yield from mapbox_earcut_2d(
                exterior.flattening(max_flattening_distance),
                [hole.flattening(max_flattening_distance) for hole in holes],
            )


def _get_aspect_ratio(ax: plt.Axes) -> float:
    minx, maxx = ax.get_xlim()
    miny, maxy = ax.get_ylim()
    data_width, data_height = maxx - minx, maxy - miny
    if abs(data_height) > 1e-9:
        return data_width / data_height
    return 1.0


def _get_width_height(
    ratio: float, width: float, height: float
) -> Tuple[float, float]:
    if width == 0.0 and height == 0.0:
        raise ValueError("invalid (width, height) values")
    if width == 0.0:
        width = height * ratio
    elif height == 0.0:
        height = width / ratio
    return width, height


def qsave(
    layout: "Layout",
    filename: str,
    *,
    bg: Optional[Color] = None,
    fg: Optional[Color] = None,
    dpi: int = 300,
    backend: str = "agg",
    config: Configuration = None,
    filter_func: FilterFunc = None,
    size_inches: Optional[Tuple[float, float]] = None,
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
        size_inches: paper size in inch as `(width, height)` tuple, which also
            defines the size in pixels = (`width` * `dpi`) x (`height` * `dpi`).
            If `width` or `height` is 0.0 the value is calculated by the aspect
            ratio of the drawing.
        backend: the matplotlib rendering backend to use (agg, cairo, svg etc)
            (see documentation for `matplotlib.use() <https://matplotlib.org/3.1.1/api/matplotlib_configuration_api.html?highlight=matplotlib%20use#matplotlib.use>`_
            for a complete list of backends)
        config: drawing parameters
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

    .. versionchanged:: 0.17
        `params` argument replaced by `config` argument

    .. versionchanged:: 0.18
        added argument `size_inches`

    """
    from .properties import RenderContext
    from .frontend import Frontend
    import matplotlib

    # Set the backend to prevent warnings about GUIs being opened from a thread
    # other than the main thread.
    old_backend = matplotlib.get_backend()
    matplotlib.use(backend)
    if config is None:
        config = Configuration.defaults()

    try:
        fig: plt.Figure = plt.figure(dpi=dpi)
        ax: plt.Axes = fig.add_axes((0, 0, 1, 1))
        ctx = RenderContext(layout.doc)
        layout_properties = LayoutProperties.from_layout(layout)
        if bg is not None:
            layout_properties.set_colors(bg, fg)
        out = MatplotlibBackend(ax)
        Frontend(ctx, out, config).draw_layout(
            layout,
            finalize=True,
            filter_func=filter_func,
            layout_properties=layout_properties,
        )
        # transparent=True sets the axes color to fully transparent
        # facecolor sets the figure color
        # (semi-)transparent axes colors do not produce transparent outputs
        # but (semi-)transparent figure colors do.
        if size_inches is not None:
            ratio = _get_aspect_ratio(ax)
            w, h = _get_width_height(ratio, size_inches[0], size_inches[1])
            fig.set_size_inches(w, h, True)
        fig.savefig(
            filename, dpi=dpi, facecolor=ax.get_facecolor(), transparent=True
        )
        plt.close(fig)
    finally:
        matplotlib.use(old_backend)


class MatplotlibLineRenderer(AbstractLineRenderer, metaclass=ABCMeta):
    def __init__(self, config: Configuration, ax: plt.Axes):
        super().__init__(config)
        self.ax = ax

    @property
    def lineweight_scaling(self) -> float:
        return self._config.lineweight_scaling * POINTS


# Scaling factor for internal renderer, just guessing here:
ISO_LIN_PATTERN_FACTOR = 3.0 * POINTS
ANSI_LIN_PATTERN_FACTOR = ISO_LIN_PATTERN_FACTOR * 2.54


class InternalLineRenderer(MatplotlibLineRenderer):
    """matplotlib internal linetype rendering, which is oriented on the output
    medium and dpi: This method is simpler and faster but may not replicate the
    results of CAD applications.
    """

    def __init__(self, config: Configuration, ax: plt.Axes, solid_only: bool):
        super().__init__(config, ax)
        self._solid_only = solid_only

    def draw_line(
        self, start: Vec3, end: Vec3, properties: Properties, z: float
    ):
        self.ax.add_line(
            Line2D(
                (start.x, end.x),
                (start.y, end.y),
                linewidth=self.lineweight(properties),
                linestyle="solid"
                if self._solid_only
                else self.linetype(properties),
                color=properties.color,
                zorder=z,
            )
        )

    def draw_path(self, path, properties: Properties, z: float):
        mpl_path = ezdxf.path.to_matplotlib_path([path])
        try:
            patch = PathPatch(
                mpl_path,
                linewidth="solid"
                if self._solid_only
                else self.lineweight(properties),
                linestyle=self.linetype(properties),
                fill=False,
                color=properties.color,
                zorder=z,
            )
        except ValueError as e:
            logger.info(f"ignored matplotlib error: {str(e)}")
        else:
            self.ax.add_patch(patch)

    @property
    def measurement_scale(self) -> float:
        return (
            ISO_LIN_PATTERN_FACTOR
            if self._config.measurement
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
