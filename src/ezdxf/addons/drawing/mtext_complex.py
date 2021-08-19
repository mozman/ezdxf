#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, List, Optional, Tuple, Dict
import copy
from ezdxf import colors
from ezdxf.lldxf import const
from ezdxf.entities import MText
from ezdxf.tools import text_layout as tl, fonts
from ezdxf.math import Matrix44, Vec3
from ezdxf.addons.mtxpl import (
    make_default_tab_stops,
    super_glue,
    new_paragraph,
    get_stroke,
    STACKING,
)

from .backend import Backend
from .properties import Properties, RenderContext, rgb_to_hex
from .type_hints import Color
from ezdxf.tools.text import (
    MTextParser,
    MTextContext,
    TokenType,
    AbstractFont,
)

__all__ = ["complex_mtext_renderer"]


def corner_vertices(
    left: float,
    bottom: float,
    right: float,
    top: float,
    m: Matrix44 = None,
) -> Iterable[Vec3]:
    corners = [  # closed polygon: fist vertex  == last vertex
        (left, top),
        (right, top),
        (right, bottom),
        (left, bottom),
        (left, top),
    ]
    if m is None:
        return Vec3.generate(corners)
    else:
        return m.transform_vertices(corners)


class FrameRenderer(tl.ContentRenderer):
    def __init__(self, properties: Properties, backend: Backend):
        self.properties = properties
        self.backend = backend

    def render(
        self,
        left: float,
        bottom: float,
        right: float,
        top: float,
        m: Matrix44 = None,
    ) -> None:
        self._render_outline(list(corner_vertices(left, bottom, right, top, m)))

    def _render_outline(self, vertices: List[Vec3]) -> None:
        backend = self.backend
        properties = self.properties
        prev = vertices.pop(0)
        for vertex in vertices:
            backend.draw_line(prev, vertex, properties)
            prev = vertex

    def line(
        self, x1: float, y1: float, x2: float, y2: float, m: Matrix44 = None
    ) -> None:
        points = [(x1, y1), (x2, y2)]
        if m is not None:
            p1, p2 = m.transform_vertices(points)
        else:
            p1, p2 = Vec3.generate(points)
        self.backend.draw_line(p1, p2, self.properties)


class ColumnBackgroundRenderer(FrameRenderer):
    def __init__(
        self,
        properties: Properties,
        backend: Backend,
        bg_properties: Properties = None,
        offset: float = 0,
        text_frame: bool = False,
    ):
        super().__init__(properties, backend)
        self.bg_properties = bg_properties
        self.offset = offset  # background border offset
        self.has_text_frame = text_frame

    def render(
        self,
        left: float,
        bottom: float,
        right: float,
        top: float,
        m: Matrix44 = None,
    ) -> None:
        # Important: this is not a clipping box, it is possible to
        # render anything outside of the given borders!
        offset = self.offset
        vertices = list(
            corner_vertices(
                left - offset, bottom - offset, right + offset, top + offset, m
            )
        )
        if self.bg_properties is not None:
            self.backend.draw_filled_polygon(vertices, self.bg_properties)
        if self.has_text_frame:
            self._render_outline(vertices)


class TextRenderer(FrameRenderer):
    """Text content renderer."""

    def __init__(
        self,
        text: str,
        cap_height: float,
        width_factor: float,
        oblique: float,
        properties: Properties,
        backend: Backend,
    ):
        super().__init__(properties, backend)
        self.text = text
        self.cap_height = cap_height
        self.width_factor = width_factor
        self.oblique = oblique

    def render(
        self,
        left: float,
        bottom: float,
        right: float,
        top: float,
        m: Matrix44 = None,
    ):
        """Create/render the text content"""
        # TODO: apply width_factor and oblique angle
        t = Matrix44.translate(left, bottom, 0)
        if m is None:
            m = t
        else:
            m = t * m
        self.backend.draw_text(self.text, m, self.properties, self.cap_height)


class Word(tl.Text):
    """Represent a word as content box for the layout engine."""

    def __init__(
        self,
        text: str,
        ctx: MTextContext,
        properties: Properties,
        renderer: "ComplexMTextRenderer",
    ):
        font = renderer.get_font(ctx)
        stroke = get_stroke(ctx)
        super().__init__(
            # Width and height of the content are fixed given values and will
            # not be changed by the layout engine:
            width=font.text_width(text),
            height=ctx.cap_height,
            valign=tl.CellAlignment(ctx.align),
            stroke=stroke,
            # Each content box can have it's own rendering object:
            renderer=TextRenderer(
                text,
                ctx.cap_height,
                ctx.width_factor,
                ctx.oblique,
                renderer.new_text_properties(properties, ctx),
                renderer.backend,
            ),
        )


class Fraction(tl.Fraction):
    def __init__(
        self,
        upr: str,
        lwr: str,
        type_: str,
        ctx: MTextContext,
        properties: Properties,
        renderer: "ComplexMTextRenderer",
    ):
        super().__init__(
            top=Word(upr, ctx, properties, renderer),
            bottom=Word(lwr, ctx, properties, renderer),
            stacking=STACKING.get(type_, tl.Stacking.LINE),
            # Uses only the generic line renderer to render the divider line,
            # the top- and bottom content boxes use their own render objects.
            renderer=FrameRenderer(properties, renderer.backend),
        )


def complex_mtext_renderer(
    ctx: RenderContext, backend: Backend, mtext: MText, properties: Properties
) -> None:
    renderer = ComplexMTextRenderer(ctx, backend, mtext, properties)
    align = tl.LayoutAlignment(mtext.dxf.attachment_point)
    layout_engine = renderer.layout_engine()
    layout_engine.place(align=align)
    layout_engine.render(mtext.ucs().matrix)


class ComplexMTextRenderer:
    def __init__(
        self,
        ctx: RenderContext,
        backend: Backend,
        mtext: MText,
        properties: Properties,
    ):
        self.ctx = ctx
        self.backend = backend
        self.mtext = mtext
        self.properties = properties
        self._font_cache: Dict[Tuple[str, float, float], AbstractFont] = {}

    def layout_engine(self) -> tl.Layout:
        def append_paragraph():
            paragraph = new_paragraph(
                cells,
                ctx,
                initial_cap_height,
                line_spacing,
                width,
                default_stops,
            )
            layout.append_paragraphs([paragraph])
            cells.clear()

        def column_heights():
            if columns.heights:  # dynamic manual
                heights = list(columns.heights)
                # last height has to be auto height = None
                heights[-1] = None
            else:  # static, dynamic auto
                heights = [columns.defined_height] * columns.count
            return heights

        mtext = self.mtext
        content = mtext.all_columns_raw_content()
        initial_cap_height = mtext.dxf.char_height

        # same line spacing for all paragraphs
        line_spacing = mtext.dxf.line_spacing_factor
        ctx = mtext_context(mtext, self.properties)
        parser = MTextParser(content, ctx)
        bg_renderer = self.make_bg_renderer()
        width = mtext.dxf.width
        default_stops = make_default_tab_stops(initial_cap_height, width)
        layout = tl.Layout(width=width)
        if mtext.has_columns:
            columns = mtext.columns
            assert columns is not None
            for height in column_heights():
                layout.append_column(
                    width=columns.width,
                    height=height,
                    gutter=columns.gutter_width,
                    renderer=bg_renderer,
                )
        else:
            # column with auto height and default width
            layout.append_column(renderer=bg_renderer)

        cells = []
        for token in parser:
            ctx = token.ctx
            if token.type == TokenType.NEW_PARAGRAPH:
                append_paragraph()
            elif token.type == TokenType.NEW_COLUMN:
                append_paragraph()
                layout.next_column()
            elif token.type == TokenType.SPACE:
                cells.append(self.space(ctx))
            elif token.type == TokenType.NBSP:
                cells.append(self.non_breaking_space(ctx))
            elif token.type == TokenType.TABULATOR:
                cells.append(self.tabulator(ctx))
            elif token.type == TokenType.WORD:
                if cells and isinstance(cells[-1], Word):
                    # property change inside a word, create an unbreakable
                    # connection between those two parts of the same word.
                    cells.append(super_glue())
                cells.append(self.word(token.data, ctx))
            elif token.type == TokenType.STACK:
                cells.append(self.fraction(token.data, ctx))

        if cells:
            append_paragraph()

        return layout

    def make_bg_renderer(self):
        dxf = self.mtext.dxf
        bg_fill = dxf.get("bg_fill", 0)

        bg_aci = None
        bg_true_color = None
        bg_properties: Optional[Properties] = None
        has_text_frame = False
        offset = 0
        if bg_fill:
            # The fill scale is a multiple of the initial char height and
            # a scale of 1, fits exact the outer border
            # of the column -> offset = 0
            offset = dxf.char_height * (dxf.get("box_fill_scale", 1.5) - 1)
            if bg_fill & const.MTEXT_BG_COLOR:
                if dxf.hasattr("bg_fill_color"):
                    bg_aci = dxf.bg_fill_color

                if dxf.hasattr("bg_fill_true_color"):
                    bg_aci = None
                    bg_true_color = dxf.bg_fill_true_color

                if (bg_fill & 3) == 3:  # canvas color = bit 0 and 1 set
                    # can not detect canvas color from DXF document!
                    # do not draw any background:
                    bg_aci = None
                    bg_true_color = None

            if bg_fill & const.MTEXT_TEXT_FRAME:
                has_text_frame = True
            bg_properties = self.new_bg_properties(bg_aci, bg_true_color)

        return ColumnBackgroundRenderer(
            self.properties,
            self.backend,
            bg_properties,
            offset=offset,
            text_frame=has_text_frame,
        )

    def space_width(self, ctx: MTextContext) -> float:
        return self.get_font(ctx).space_width()

    def space(self, ctx: MTextContext):
        return tl.Space(width=self.space_width(ctx))

    def tabulator(self, ctx: MTextContext):
        return tl.Tabulator(width=self.space_width(ctx))

    def non_breaking_space(self, ctx: MTextContext):
        return tl.NonBreakingSpace(width=self.space_width(ctx))

    def word(self, text: str, ctx: MTextContext):
        return Word(text, ctx, self.properties, self)

    def fraction(self, data: Tuple, ctx: MTextContext):
        upr, lwr, type_ = data
        if type_:
            return Fraction(upr, lwr, type_, ctx, self.properties, self)
        else:
            return Word(upr, ctx, self.properties, self)

    def resolve_aci_color(self, aci: int) -> Color:
        return self.ctx.resolve_aci_color(aci, self.properties.layer)

    def get_font(self, ctx: MTextContext) -> fonts.AbstractFont:
        ttf = fonts.find_ttf_path(ctx.font_face)
        key = (ttf, ctx.cap_height, ctx.width_factor)
        font = self._font_cache.get(key)
        if font is None:
            font = fonts.make_font(ttf, ctx.cap_height, ctx.width_factor)
            self._font_cache[key] = font
        return font

    def new_text_properties(
        self, properties: Properties, ctx: MTextContext
    ) -> Properties:
        new_properties = copy.copy(properties)
        if ctx.rgb is None:
            new_properties.color = self.resolve_aci_color(ctx.aci)
        else:
            new_properties.color = rgb_to_hex(ctx.rgb)
        new_properties.font = ctx.font_face
        return new_properties

    def new_bg_properties(
        self, aci: Optional[int], true_color: Optional[int]
    ) -> Properties:
        new_properties = copy.copy(self.properties)
        new_properties.color = (  # canvas background color
            self.ctx.current_layout_properties.background_color
        )
        if true_color is None:
            if aci is not None:
                new_properties.color = self.resolve_aci_color(aci)
            # else canvas background color
        else:
            new_properties.color = rgb_to_hex(colors.int2rgb(true_color))
        return new_properties


def mtext_context(mtext: MText, properties: Properties) -> MTextContext:
    """Setup initial MTEXT context."""
    ctx = MTextContext()
    ctx.font_face = properties.font  # type: ignore
    ctx.cap_height = mtext.dxf.char_height
    ctx.aci = mtext.dxf.color
    rgb = mtext.rgb
    if rgb is not None:
        ctx.rgb = rgb
    return ctx
