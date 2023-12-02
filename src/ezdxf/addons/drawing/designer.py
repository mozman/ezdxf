#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import (
    Sequence,
    Optional,
    Iterable,
    Tuple,
    TYPE_CHECKING,
    Iterator,
    Callable,
)
from typing_extensions import TypeAlias
import abc
import itertools

from ezdxf.colors import RGB
import ezdxf.bbox

from ezdxf.fonts import fonts
from ezdxf.math import Vec2, Matrix44, BoundingBox2d, AnyVec
from ezdxf.path import make_path, Path
from ezdxf.tools.text import replace_non_printable_characters
from ezdxf.render import linetypes
from ezdxf.entities import DXFGraphic, Viewport

from .backend import BackendInterface, BkPath2d, BkPoints2d
from .clipper import ClippingRect
from .config import LinePolicy, TextPolicy, ColorPolicy, Configuration
from .properties import BackendProperties, Filling
from .properties import Properties, RenderContext
from .type_hints import Color
from .unified_text_renderer import UnifiedTextRenderer

if TYPE_CHECKING:
    from ezdxf.layouts import Layout

PatternKey: TypeAlias = Tuple[str, float]
DrawEntitiesCallback: TypeAlias = Callable[[RenderContext, Iterable[DXFGraphic]], None]


class Designer(abc.ABC):
    """The designer separates the frontend from the backend and adds this features:

    - automatically linetype rendering
    - VIEWPORT rendering
    - foreground color mapping according Frontend.config.color_policy

    """

    text_engine = UnifiedTextRenderer()
    default_font_face = fonts.FontFace()
    draw_entities: DrawEntitiesCallback

    @abc.abstractmethod
    def set_draw_entities_callback(self, callback: DrawEntitiesCallback) -> None:
        ...

    @abc.abstractmethod
    def set_config(self, config: Configuration) -> None:
        ...

    @abc.abstractmethod
    def set_current_entity_handle(self, handle: str) -> None:
        ...

    @abc.abstractmethod
    def draw_viewport(
        self,
        vp: Viewport,
        layout_ctx: RenderContext,
        bbox_cache: Optional[ezdxf.bbox.Cache] = None,
    ) -> None:
        """Draw the content of the given viewport current viewport."""
        ...

    @abc.abstractmethod
    def draw_point(self, pos: AnyVec, properties: Properties) -> None:
        ...

    @abc.abstractmethod
    def draw_line(self, start: AnyVec, end: AnyVec, properties: Properties):
        ...

    @abc.abstractmethod
    def draw_solid_lines(
        self, lines: Iterable[tuple[AnyVec, AnyVec]], properties: Properties
    ) -> None:
        ...

    @abc.abstractmethod
    def draw_path(self, path: Path, properties: Properties):
        ...

    @abc.abstractmethod
    def draw_filled_paths(
        self,
        paths: Iterable[Path],
        properties: Properties,
    ) -> None:
        ...

    @abc.abstractmethod
    def draw_filled_polygon(
        self, points: Iterable[AnyVec], properties: Properties
    ) -> None:
        ...

    @abc.abstractmethod
    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
        dxftype: str = "TEXT",
    ) -> None:
        ...

    @abc.abstractmethod
    def finalize(self) -> None:
        ...

    @abc.abstractmethod
    def set_background(self, color: Color) -> None:
        ...

    @abc.abstractmethod
    def enter_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        # gets the full DXF properties information
        ...

    @abc.abstractmethod
    def exit_entity(self, entity: DXFGraphic) -> None:
        ...


class Designer2d(Designer):
    """Designer class for 2D backends."""

    def __init__(self, backend: BackendInterface):
        self.backend = backend
        self.config = Configuration()
        self.pattern_cache: dict[PatternKey, Sequence[float]] = dict()
        try:  # request default font face
            self.default_font_face = fonts.font_manager.get_font_face("")
        except fonts.FontNotFoundError:  # no default font found
            # last resort MonospaceFont which renders only "tofu"
            pass
        self.clipper = ClippingRect()
        self.current_vp_scale = 1.0
        self._current_entity_handle: str = ""
        self._color_mapping: dict[str, str] = dict()

    @property
    def vp_ltype_scale(self) -> float:
        """The linetype pattern should look the same in all viewports
        regardless of the viewport scale.
        """
        return 1.0 / max(self.current_vp_scale, 0.0001)  # max out at 1:10000

    def get_backend_properties(self, properties: Properties) -> BackendProperties:
        try:
            color = self._color_mapping[properties.color]
        except KeyError:
            color = apply_color_policy(
                properties.color, self.config.color_policy, self.config.custom_fg_color
            )
            self._color_mapping[properties.color] = color
        return BackendProperties(
            color,
            properties.lineweight,
            properties.layer,
            properties.pen,
            self._current_entity_handle,
        )

    def set_draw_entities_callback(self, callback: DrawEntitiesCallback) -> None:
        self.draw_entities = callback

    def set_config(self, config: Configuration) -> None:
        self.config = config
        self.backend.configure(self.config)

    def set_current_entity_handle(self, handle: str) -> None:
        assert handle is not None
        self._current_entity_handle = handle

    def draw_viewport(
        self,
        vp: Viewport,
        layout_ctx: RenderContext,
        bbox_cache: Optional[ezdxf.bbox.Cache] = None,
    ) -> None:
        """Draw the content of the given viewport current viewport."""
        if vp.doc is None:
            return
        try:
            msp_limits = vp.get_modelspace_limits()
        except ValueError:  # modelspace limits not detectable
            return
        if self.enter_viewport(vp):
            self.draw_entities(
                layout_ctx.from_viewport(vp),
                filter_vp_entities(vp.doc.modelspace(), msp_limits, bbox_cache),
            )
            self.exit_viewport()

    def enter_viewport(self, vp: Viewport) -> bool:
        """Set current viewport, returns ``True`` for valid viewports."""
        self.current_vp_scale = vp.get_scale()
        m = vp.get_transformation_matrix()
        clipping_path = make_path(vp)
        if len(clipping_path):
            self.clipper.push(BkPath2d(clipping_path), m)
            return True
        return False

    def exit_viewport(self):
        self.clipper.pop()
        self.current_vp_scale = 1.0

    def draw_point(self, pos: AnyVec, properties: Properties) -> None:
        point = Vec2(pos)
        if self.clipper.is_active:
            point = self.clipper.clip_point(point)
            if point is None:
                return
        self.backend.draw_point(point, self.get_backend_properties(properties))

    def draw_line(self, start: AnyVec, end: AnyVec, properties: Properties):
        s = Vec2(start)
        e = Vec2(end)
        if (
            self.config.line_policy == LinePolicy.SOLID
            or len(properties.linetype_pattern) < 2  # CONTINUOUS
        ):
            if self.clipper.is_active:
                points = self.clipper.clip_line(s, e)
                if len(points) != 2:
                    return
                start, end = points
            self.backend.draw_line(start, end, self.get_backend_properties(properties))
        else:
            renderer = linetypes.LineTypeRenderer(self.pattern(properties))
            self.draw_solid_lines(  # includes transformation
                ((s, e) for s, e in renderer.line_segment(s, e)),
                properties,
            )

    def draw_solid_lines(
        self, lines: Iterable[tuple[AnyVec, AnyVec]], properties: Properties
    ) -> None:
        lines2d = [(Vec2(s), Vec2(e)) for s, e in lines]
        if self.clipper.is_active:
            clipped_lines: list[Sequence[Vec2]] = []
            for start, end in lines2d:
                points = self.clipper.clip_line(start, end)
                if points:
                    clipped_lines.append(points)
            lines2d = clipped_lines  # type: ignore
        self.backend.draw_solid_lines(lines2d, self.get_backend_properties(properties))

    def draw_path(self, path: Path, properties: Properties):
        self._draw_path(BkPath2d(path), properties)

    def _draw_path(self, path: BkPath2d, properties: Properties):
        if (
            self.config.line_policy == LinePolicy.SOLID
            or len(properties.linetype_pattern) < 2  # CONTINUOUS
        ):
            if self.clipper.is_active:
                for clipped_path in self.clipper.clip_paths(
                    [path], self.config.max_flattening_distance
                ):
                    self.backend.draw_path(
                        clipped_path, self.get_backend_properties(properties)
                    )
                return
            self.backend.draw_path(path, self.get_backend_properties(properties))
        else:
            renderer = linetypes.LineTypeRenderer(self.pattern(properties))
            vertices = path.flattening(self.config.max_flattening_distance, segments=16)

            self.draw_solid_lines(
                ((Vec2(s), Vec2(e)) for s, e in renderer.line_segments(vertices)),
                properties,
            )

    def draw_filled_paths(
        self,
        paths: Iterable[Path],
        properties: Properties,
    ) -> None:
        self._draw_filled_paths(map(BkPath2d, paths), properties)

    def _draw_filled_paths(
        self,
        paths: Iterable[BkPath2d],
        properties: Properties,
    ) -> None:
        if self.clipper.is_active:
            max_sagitta = self.config.max_flattening_distance
            paths = self.clipper.clip_filled_paths(paths, max_sagitta)
        self.backend.draw_filled_paths(paths, self.get_backend_properties(properties))

    def draw_filled_polygon(
        self, points: Iterable[AnyVec], properties: Properties
    ) -> None:
        self._draw_filled_polygon(BkPoints2d(points), properties)

    def _draw_filled_polygon(self, points: BkPoints2d, properties: Properties) -> None:
        if self.clipper.is_active:
            points = self.clipper.clip_polygon(points)
        self.backend.draw_filled_polygon(
            points, self.get_backend_properties(properties)
        )

    def pattern(self, properties: Properties) -> Sequence[float]:
        """Get pattern - implements pattern caching."""
        if self.config.line_policy == LinePolicy.SOLID:
            scale = 0.0
        else:
            scale = properties.linetype_scale * self.vp_ltype_scale

        key: PatternKey = (properties.linetype_name, scale)
        pattern_ = self.pattern_cache.get(key)
        if pattern_ is None:
            pattern_ = self.create_pattern(properties, scale)
            self.pattern_cache[key] = pattern_
        return pattern_

    def create_pattern(self, properties: Properties, scale: float) -> Sequence[float]:
        """Returns simplified linetype tuple: on-off sequence"""
        if len(properties.linetype_pattern) < 2:
            # Do not return None -> None indicates: "not cached"
            return tuple()
        else:
            min_dash_length = self.config.min_dash_length * self.vp_ltype_scale
            pattern = [
                max(e * scale, min_dash_length) for e in properties.linetype_pattern
            ]
            if len(pattern) % 2:
                pattern.pop()
            return pattern

    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
        dxftype: str = "TEXT",
    ) -> None:
        text_policy = self.config.text_policy
        if not text.strip() or text_policy == TextPolicy.IGNORE:
            return  # no point rendering empty strings
        text = prepare_string_for_rendering(text, dxftype)
        font_face = properties.font
        if font_face is None:
            font_face = self.default_font_face

        try:
            glyph_paths = self.text_engine.get_text_glyph_paths(
                text, font_face, cap_height
            )
        except (RuntimeError, ValueError):
            return
        for p in glyph_paths:
            p.transform_inplace(transform)
        transformed_paths: list[BkPath2d] = glyph_paths

        points: list[Vec2]
        if text_policy == TextPolicy.REPLACE_RECT:
            points = []
            for p in transformed_paths:
                points.extend(p.extents())
            if len(points) < 2:
                return
            rect = BkPath2d.from_vertices(BoundingBox2d(points).rect_vertices())
            self._draw_path(rect, properties)
            return
        if text_policy == TextPolicy.REPLACE_FILL:
            points = []
            for p in transformed_paths:
                points.extend(p.extents())
            if len(points) < 2:
                return
            polygon = BkPoints2d(BoundingBox2d(points).rect_vertices())
            if properties.filling is None:
                properties.filling = Filling()
            self._draw_filled_polygon(polygon, properties)
            return

        if (
            self.text_engine.is_stroke_font(font_face)
            or text_policy == TextPolicy.OUTLINE
        ):
            for text_path in transformed_paths:
                self._draw_path(text_path, properties)
            return

        if properties.filling is None:
            properties.filling = Filling()
        self._draw_filled_paths(transformed_paths, properties)

    def finalize(self) -> None:
        self.backend.finalize()

    def set_background(self, color: Color) -> None:
        self.backend.set_background(color)

    def enter_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        self.backend.enter_entity(entity, properties)

    def exit_entity(self, entity: DXFGraphic) -> None:
        self.backend.exit_entity(entity)


def invert_color(color: Color) -> Color:
    r, g, b = RGB.from_hex(color)
    return RGB(255 - r, 255 - g, 255 - b).to_hex()


def swap_bw(color: str) -> Color:
    color = color.lower()
    if color == "#000000":
        return "#ffffff"
    if color == "#ffffff":
        return "#000000"
    return color


def color_to_monochrome(color: Color, scale: float = 1.0, offset: float = 0.0) -> Color:
    lum = RGB.from_hex(color).luminance * scale + offset
    if lum < 0.0:
        lum = 0.0
    elif lum > 1.0:
        lum = 1.0
    gray = round(lum * 255)
    return RGB(gray, gray, gray).to_hex()


def apply_color_policy(color: Color, policy: ColorPolicy, custom_color: Color) -> Color:
    alpha = color[7:9]
    color = color[:7]
    if policy == ColorPolicy.COLOR_SWAP_BW:
        color = swap_bw(color)
    elif policy == ColorPolicy.COLOR_NEGATIVE:
        color = invert_color(color)
    elif policy == ColorPolicy.MONOCHROME_DARK_BG:  # [0.3, 1.0]
        color = color_to_monochrome(color, scale=0.7, offset=0.3)
    elif policy == ColorPolicy.MONOCHROME_LIGHT_BG:  # [0.0, 0.7]
        color = color_to_monochrome(color, scale=0.7, offset=0.0)
    elif policy == ColorPolicy.MONOCHROME:  # [0.0, 1.0]
        color = color_to_monochrome(color)
    elif policy == ColorPolicy.BLACK:
        color = "#000000"
    elif policy == ColorPolicy.WHITE:
        color = "#ffffff"
    elif policy == ColorPolicy.CUSTOM:
        fg = custom_color
        color = fg[:7]
        alpha = fg[7:9]
    return color + alpha


def filter_vp_entities(
    msp: Layout,
    limits: Sequence[float],
    bbox_cache: Optional[ezdxf.bbox.Cache] = None,
) -> Iterator[DXFGraphic]:
    """Yields all DXF entities that need to be processed by the given viewport
    `limits`. The entities may be partially of even complete outside the viewport.
    By passing the bounding box cache of the modelspace entities,
    the function can filter entities outside the viewport to speed up rendering
    time.

    There are two processing modes for the `bbox_cache`:

        1. The `bbox_cache` is``None``: all entities must be processed,
           pass through mode
        2. If the `bbox_cache` is given but does not contain an entity,
           the bounding box is computed and added to the cache.
           Even passing in an empty cache can speed up rendering time when
           multiple viewports need to be processed.

    Args:
        msp: modelspace layout
        limits: modelspace limits of the viewport, as tuple (min_x, min_y, max_x, max_y)
        bbox_cache: the bounding box cache of the modelspace entities

    """

    # WARNING: this works only with top-view viewports
    # The current state of the drawing add-on supports only top-view viewports!
    def is_visible(e):
        entity_bbox = bbox_cache.get(e)
        if entity_bbox is None:
            # compute and add bounding box
            entity_bbox = ezdxf.bbox.extents((e,), fast=True, cache=bbox_cache)
        if not entity_bbox.has_data:
            return True
        # Check for separating axis:
        if min_x >= entity_bbox.extmax.x:
            return False
        if max_x <= entity_bbox.extmin.x:
            return False
        if min_y >= entity_bbox.extmax.y:
            return False
        if max_y <= entity_bbox.extmin.y:
            return False
        return True

    if bbox_cache is None:  # pass through all entities
        yield from msp
        return

    min_x, min_y, max_x, max_y = limits
    if not bbox_cache.has_data:
        # fill cache at once
        ezdxf.bbox.extents(msp, fast=True, cache=bbox_cache)

    for entity in msp:
        if is_visible(entity):
            yield entity


def prepare_string_for_rendering(text: str, dxftype: str) -> str:
    assert "\n" not in text, "not a single line of text"
    if dxftype in {"TEXT", "ATTRIB", "ATTDEF"}:
        text = replace_non_printable_characters(text, replacement="?")
        text = text.replace("\t", "?")
    elif dxftype == "MTEXT":
        text = replace_non_printable_characters(text, replacement="▯")
        text = text.replace("\t", "        ")
    else:
        raise TypeError(dxftype)
    return text
