#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import cast, Dict, Tuple, List
import sys
import math
import pathlib
import ezdxf
from ezdxf import zoom
from ezdxf.entities import MText, DXFGraphic, Textstyle
from ezdxf.layouts import BaseLayout
from ezdxf.math import Matrix44
from ezdxf.tools import text_layout, fonts
from ezdxf.tools.text import (
    MTextParser, MTextContext, TokenType, ParagraphProperties,
    MTextParagraphAlignment,
)

if not ezdxf.options.use_matplotlib:
    print("The Matplotlib package is required.")
    sys.exit(1)

DIR = pathlib.Path('~/Desktop/Outbox').expanduser()

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam " \
              "nonumy eirmod tempor {\C1invidunt ut labore} et dolore magna aliquyam " \
              "erat, sed diam voluptua. At vero eos et accusam et justo duo dolores " \
              "et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est " \
              "Lorem ipsum dolor sit amet."
LEFT = LOREM_IPSUM + "\n\n"
CENTER = r"\pxqc;" + LOREM_IPSUM + "\n\n"
RIGHT = r"\pxqr;" + LOREM_IPSUM + "\n\n"
JUSTIFIED = r"\pi1,qj;" + LOREM_IPSUM + "\n\n"


class FrameRenderer(text_layout.ContentRenderer):
    def __init__(self, attribs: Dict, layout: BaseLayout):
        self.line_attribs = attribs
        self.layout = layout

    def render(self, left: float, bottom: float, right: float,
               top: float, m: Matrix44 = None) -> None:
        pline = self.layout.add_lwpolyline(
            [(left, top), (right, top), (right, bottom), (left, bottom)],
            close=True, dxfattribs=self.line_attribs,
        )
        if m:
            pline.transform(m)

    def line(self, x1: float, y1: float, x2: float, y2: float,
             m: Matrix44 = None) -> None:
        line = self.layout.add_line((x1, y1), (x2, y2),
                                    dxfattribs=self.line_attribs)
        if m:
            line.transform(m)


class TextRenderer(FrameRenderer):
    """ Text content renderer. """

    def __init__(self, text: str, text_attribs: Dict, line_attribs: Dict,
                 layout: BaseLayout):
        super().__init__(line_attribs, layout)
        self.text = text
        self.text_attribs = text_attribs

    def render(self, left: float, bottom: float, right: float,
               top: float, m: Matrix44 = None):
        """ Create/render the text content """
        text = self.layout.add_text(self.text, dxfattribs=self.text_attribs)
        text.set_pos((left, bottom), align='LEFT')
        if m:
            text.transform(m)


class Word(text_layout.Text):
    """ Represent a word as content box for the layout engine. """

    def __init__(self, text: str, ctx: MTextContext, attribs: Dict,
                 xpl: "MTextExplode"):
        # Each content box can have individual properties:
        line_attribs = dict(attribs or {})
        line_attribs.update(get_color_attribs(ctx))
        text_attribs = dict(line_attribs)
        text_attribs.update(xpl.get_text_attribs(ctx))

        font = xpl.get_font(ctx)
        stroke = get_stroke(ctx)
        super().__init__(
            # Width and height of the content are fixed given values and will
            # not be changed by the layout engine:
            width=font.text_width(text),
            height=ctx.cap_height,
            stroke=stroke,
            # Each content box can have it's own rendering object:
            renderer=TextRenderer(text, text_attribs, line_attribs, xpl.layout),
        )


STACKING = {
    "^": text_layout.Stacking.OVER,
    "/": text_layout.Stacking.LINE,
    "#": text_layout.Stacking.SLANTED,
}


class Fraction(text_layout.Fraction):
    def __init__(self, upr: str, lwr: str, type_: str, ctx: MTextContext,
                 attribs: Dict, xpl: "MTextExplode"):
        super().__init__(
            top=Word(upr, ctx, attribs, xpl),
            bottom=Word(lwr, ctx, attribs, xpl),
            stacking=STACKING.get(type_, text_layout.Stacking.LINE),
            # Uses only the generic line renderer to render the divider line,
            # the top- and bottom content boxes use their own render objects.
            renderer=FrameRenderer(attribs, xpl.layout),
        )


def get_font_face(entity: DXFGraphic, doc=None) -> fonts.FontFace:
    """ Returns the :class:`~ezdxf.tools.fonts.FontFace` defined by the
    associated text style. Returns the default font face if the `entity` does
    not have or support the DXF attribute "style".

    Pass a DXF document as argument `doc` to resolve text styles for virtual
    entities which are not assigned to a DXF document. The argument `doc`
    always overrides the DXF document to which the `entity` is assigned to.

    """
    if entity.doc and doc is None:
        doc = entity.doc
    assert doc is not None, "DXF document required"

    style_name = ""
    # This also works for entities which do not support "style",
    # where :code:`style_name = entity.dxf.get("style")` would fail.
    if entity.dxf.hasattr("style"):
        style_name = entity.dxf.style

    font_face = fonts.FontFace()
    if style_name and doc is not None:
        style = cast(Textstyle, doc.styles.get(style_name))
        family, italic, bold = style.get_extended_font_data()
        if family:
            text_style = "italic" if italic else "normal"
            text_weight = "bold" if bold else "normal"
            font_face = fonts.FontFace(
                family=family, style=text_style, weight=text_weight)
        else:
            ttf = style.dxf.font
            if ttf:
                font_face = fonts.get_font_face(ttf)
    return font_face


def mtext_context(mtext: MText) -> MTextContext:
    """ Setup initial MTEXT context. """
    ctx = MTextContext()
    ctx.font_face = get_font_face(mtext)
    ctx.cap_height = mtext.dxf.char_height
    ctx.color = mtext.dxf.color
    rgb = mtext.rgb
    if rgb is not None:
        ctx.rgb = rgb
    return ctx


ALIGN = {
    MTextParagraphAlignment.LEFT: text_layout.FlowTextAlignment.LEFT,
    MTextParagraphAlignment.RIGHT: text_layout.FlowTextAlignment.RIGHT,
    MTextParagraphAlignment.CENTER: text_layout.FlowTextAlignment.CENTER,
    MTextParagraphAlignment.JUSTIFIED: text_layout.FlowTextAlignment.JUSTIFIED,
    MTextParagraphAlignment.DISTRIBUTED: text_layout.FlowTextAlignment.JUSTIFIED,
    MTextParagraphAlignment.DEFAULT: text_layout.FlowTextAlignment.LEFT,
}


def new_paragraph(cells: List, ctx: MTextContext, cap_height: float,
                  line_spacing: float = 1):
    if cells:
        p = ctx.paragraph
        align = ALIGN.get(p.align, text_layout.FlowTextAlignment.LEFT)
        left = p.left * cap_height
        right = p.right * cap_height
        first = left + p.indent * cap_height  # relative to left
        paragraph = text_layout.FlowText(
            align=align,
            indent=(first, left, right),
            line_spacing=line_spacing,
        )
        paragraph.append_content(cells)
    else:
        paragraph = text_layout.EmptyParagraph(
            cap_height=ctx.cap_height, line_spacing=line_spacing)
    return paragraph


def get_stroke(ctx: MTextContext) -> int:
    stroke = 0
    if ctx.underline:
        stroke += text_layout.Stroke.UNDERLINE
    if ctx.strike_through:
        stroke += text_layout.Stroke.STRIKE_THROUGH
    if ctx.overline:
        stroke += text_layout.Stroke.OVERLINE
    return stroke


def get_color_attribs(ctx: MTextContext) -> Dict:
    attribs = {"color": ctx.aci}
    if ctx.rgb is not None:
        attribs["true_color"] = ezdxf.rgb2int(ctx.rgb)
    return attribs


class MTextExplode:
    def __init__(self, layout: BaseLayout, doc=None):
        self.layout = layout
        self._doc = doc if doc else layout.doc
        assert self._doc is not None, "DXF document required"
        self._required_text_styles: Dict = {}
        self._font_cache = {}

    def mtext_exploded_text_style(self, font_face: fonts.FontFace) -> str:
        style = 0
        if font_face.is_bold:
            style += 1
        if font_face.is_italic:
            style += 2
        style = str(style) if style > 0 else ""
        # BricsCAD naming convention for exploded MTEXT styles:
        text_style = f"MtXpl_{font_face.family}" + style
        self._required_text_styles[text_style] = font_face
        return text_style

    def get_font(self, ctx: MTextContext) -> fonts.AbstractFont:
        ttf = fonts.find_ttf_path(ctx.font_face)
        key = (ttf, ctx.cap_height, ctx.width_factor)
        font = self._font_cache.get(key)
        if font is None:
            font = fonts.make_font(ttf, ctx.cap_height, ctx.width_factor)
            self._font_cache[key] = font
        return font

    def get_text_attribs(self, ctx: MTextContext) -> Dict:
        attribs = {
            "height": ctx.cap_height,
            "style": self.mtext_exploded_text_style(ctx.font_face),
        }
        if not math.isclose(ctx.width_factor, 1.0):
            attribs["width"] = ctx.width_factor
        if abs(ctx.oblique) > 1e-6:
            attribs["oblique"] = ctx.oblique
        return attribs

    def layout_engine(self, mtext: MText) -> text_layout.Layout:
        def get_base_attribs() -> Dict:
            dxf = mtext.dxf
            attribs = {
                "layer": dxf.layer,
                "color": dxf.color,
            }
            return attribs

        def append_paragraph():
            paragraph = new_paragraph(
                cells, ctx, initial_cap_height, line_spacing)
            layout.append_paragraphs([paragraph])
            cells.clear()

        content = mtext.text
        initial_cap_height = mtext.dxf.char_height
        # same line spacing for all paragraphs
        line_spacing = mtext.dxf.line_spacing_factor
        base_attribs = get_base_attribs()
        ctx = mtext_context(mtext)
        parser = MTextParser(content, ctx)
        layout = text_layout.Layout(width=mtext.dxf.width)
        layout.append_column()
        cells = []
        for token in parser:
            ctx = token.ctx
            if token.type == TokenType.NEW_PARAGRAPH:
                append_paragraph()
            elif token.type == TokenType.NEW_COLUMN:
                append_paragraph()
                # todo: layout.next_column()
            elif token.type == TokenType.SPACE:
                cells.append(self.space(ctx))
            elif token.type == TokenType.NBSP:
                cells.append(self.non_breaking_space(ctx))
            elif token.type == TokenType.TABULATOR:
                cells.append(self.space(ctx))
            elif token.type == TokenType.WORD:
                cells.append(self.word(token.data, ctx, base_attribs))
            elif token.type == TokenType.STACK:
                cells.append(self.fraction(token.data, ctx, base_attribs))

        if cells:
            append_paragraph()

        return layout

    def space(self, ctx: MTextContext):
        return text_layout.Space(width=self.get_font(ctx).space_width())

    def non_breaking_space(self, ctx: MTextContext):
        return text_layout.NonBreakingSpace(
            width=self.get_font(ctx).space_width())

    def word(self, text: str, ctx: MTextContext, attribs: Dict):
        return Word(text, ctx, attribs, self)

    def fraction(self, data: Tuple, ctx: MTextContext, attribs: Dict):
        upr, lwr, type_ = data
        if type_:
            return Fraction(upr, lwr, type_, ctx, attribs, self)
        else:
            return Word(upr, ctx, attribs, self)

    def explode(self, mtext: MText, destroy=True):
        location = mtext.dxf.insert
        align = text_layout.LayoutAlignment(mtext.dxf.attachment_point)
        layout_engine = self.layout_engine(mtext)
        layout_engine.place(align=align)
        m = Matrix44.translate(location.x, location.y, location.z)
        layout_engine.render(m)
        if destroy:
            mtext.destroy()

    def finalize(self):
        def ttf_path(font_face: fonts.FontFace) -> str:
            ttf = font_face.ttf
            if not ttf:
                ttf = fonts.find_ttf_path(font_face)
            return ttf

        text_styles = self._doc.styles
        for name, font_face in self._required_text_styles.items():
            if name not in text_styles:
                style = cast(Textstyle, text_styles.new(name))
                style.dxf.font = ttf_path(font_face)
                style.set_extended_font_data(
                    font_face.family,
                    italic=font_face.is_italic,
                    bold=font_face.is_bold,
                )


def new_doc(content: str, width: float = 30):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    msp.add_mtext(content, dxfattribs={
        "width": width,
        "char_height": 1,
        "color": 7,
        "style": "OpenSans"
    })
    zoom.extents(msp)
    return doc


def explode_mtext(doc):
    msp = doc.modelspace()
    mtext = msp.query("MTEXT").first
    xpl = MTextExplode(msp)
    xpl.explode(mtext)
    xpl.finalize()
    zoom.extents(msp)
    return doc


if __name__ == '__main__':
    doc = new_doc(LEFT + CENTER + RIGHT + JUSTIFIED)
    doc.saveas(DIR / "mtext_source.dxf")
    doc = explode_mtext(doc)
    doc.saveas(DIR / "mtext_xplode.dxf")
