#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
from typing import Iterable
import pathlib
import random
import ezdxf
from ezdxf import zoom, print_config
from ezdxf.math import Matrix44
from ezdxf.tools import fonts
from ezdxf.tools import text_layout

""" 
This example shows the usage of the internal text_layout module to render 
complex text layouts. The module is designed to render MText like entities,
but could be used for other tasks too. The layout engine supports a multi 
column setup, each column contains paragraphs, and these paragraphs can 
automatically flow across the columns. All locations are relative to each other, 
absolute locations are not supported - tabulators are not supported.

The layout engine knows nothing about the content itself, it just manages 
content boxes of a fixed given width and height and "glue" spaces in between. 
The engine does not alter the size of the content boxes, but resizes the glue 
if necessary. The actual rendering is done by a rendering object associated to 
each content box. 

The only text styling manged by the layout engine is underline, overline and 
strike through multiple content boxes.

Features:

- layout alignment like MText: top-middle-bottom combined with left-center-right
- paragraph alignments: left, right, center, justified
- paragraph indentation: left, right, special first line
- cell alignments: top, center, bottom
- fraction cells: over, slanted, tolerance style
- columns have a fixed height or grows automatically, paragraphs which do not 
  fit "flow" into the following column.
- pass through of transformation matrix to the rendering object

TODO: 

- bullet- and numbered lists
- refinements to replicate MText features as good as possible

Used for:

- drawing add-on to render MTEXT with columns
- explode MTEXT into DXF primitives (TEXT, LINE)

"""
if not ezdxf.options.use_matplotlib:
    print("The Matplotlib package is required.")
    sys.exit(1)

# Type aliases:
Content = Iterable[text_layout.Cell]
Stacking = text_layout.Stacking
ParagraphAlignment = text_layout.ParagraphAlignment

DIR = pathlib.Path("~/Desktop/Outbox").expanduser()
STYLE = "Style0"
FONT = "OpenSans-Regular.ttf"
COLUMN_HEIGHT = 12

print_config()

doc = ezdxf.new()
msp = doc.modelspace()
style = doc.styles.new(STYLE, dxfattribs={"font": FONT})


def measure_space(font):
    return font.text_width(" X") - font.text_width("X")


class SizedFont:
    def __init__(self, height: float):
        self.height = float(height)
        self.font = fonts.make_font(FONT, self.height)
        self.space = measure_space(self.font)

    def text_width(self, text: str):
        return self.font.text_width(text)


fix_sized_fonts = [
    SizedFont(0.18),
    SizedFont(0.35),
    SizedFont(0.50),
    SizedFont(0.70),
    SizedFont(1.00),
]


class FrameRenderer(text_layout.ContentRenderer):
    """Render object to render a frame around a content collection.

    This renderer can be used by collections which just manages content
    but do not represent a content by itself (Layout, Column, Paragraph).

    """

    def __init__(self, color):
        self.color = color

    def render(
        self,
        left: float,
        bottom: float,
        right: float,
        top: float,
        m: Matrix44 = None,
    ) -> None:
        """Render a frame as LWPOLYLINE."""
        pline = msp.add_lwpolyline(
            [(left, top), (right, top), (right, bottom), (left, bottom)],
            close=True,
            dxfattribs={"color": self.color},
        )
        if m:
            pline.transform(m)

    def line(
        self, x1: float, y1: float, x2: float, y2: float, m: Matrix44 = None
    ) -> None:
        """Line renderer used to create underline, overline, strike through
        and fraction dividers.

        """
        line = msp.add_line(
            (x1, y1), (x2, y2), dxfattribs={"color": self.color}
        )
        if m:
            line.transform(m)


class TextRenderer(text_layout.ContentRenderer):
    """Text content renderer."""

    def __init__(self, text, attribs):
        self.text = text
        self.attribs = attribs
        self.line_attribs = {"color": attribs["color"]}

    def render(
        self,
        left: float,
        bottom: float,
        right: float,
        top: float,
        m: Matrix44 = None,
    ):
        """Create/render the text content"""
        text = msp.add_text(self.text, dxfattribs=self.attribs)
        text.set_pos((left, bottom), align="LEFT")
        if m:
            text.transform(m)

    def line(
        self, x1: float, y1: float, x2: float, y2: float, m: Matrix44 = None
    ) -> None:
        """Line renderer used to create underline, overline, strike through
        and fraction dividers.

        """
        line = msp.add_line((x1, y1), (x2, y2), dxfattribs=self.line_attribs)
        if m:
            line.transform(m)


class Word(text_layout.Text):
    """Represent a word as content box for the layout engine."""

    def __init__(self, text: str, font: SizedFont, stroke: int = 0):
        # Each content box can have individual properties:
        attribs = {
            "color": random.choice((1, 2, 3, 4, 6, 7, 7)),
            "height": font.height,
            "style": STYLE,
        }
        super().__init__(
            # Width and height of the content are fixed given values and will
            # not be changed by the layout engine:
            width=font.text_width(text),
            height=font.height,
            stroke=stroke,
            # Each content box can have it's own rendering object:
            renderer=TextRenderer(text, attribs),
        )


def uniform_content(count: int, size: int = 1) -> Content:
    """Create content with one text size."""
    font = fix_sized_fonts[size]
    for word in text_layout.lorem_ipsum(count):
        yield Word(word, font)
        yield text_layout.Space(font.space)


def random_sized_content(count: int) -> Content:
    """Create content with randomized text size."""

    def size():
        return random.choice([0, 1, 1, 1, 1, 1, 2, 3])

    for word in text_layout.lorem_ipsum(count):
        font = fix_sized_fonts[size()]
        yield Word(word, font)
        yield text_layout.Space(font.space)


def stroke_groups(words: Iterable[str]):
    group = []
    count = 0
    stroke = 0
    for word in words:
        if count == 0:
            if group:
                yield group, stroke
            count = random.randint(1, 4)
            group = [word]
            stroke = random.choice([0, 0, 0, 0, 1, 1, 1, 2, 2, 4])
        else:
            count -= 1
            group.append(word)

    if group:
        yield group, stroke


def stroked_content(count: int, size: int = 1) -> Content:
    """Create content with one text size and groups of words with or without
    strokes.

    """
    font = fix_sized_fonts[size]
    groups = stroke_groups(text_layout.lorem_ipsum(count))
    for group, stroke in groups:
        # strokes should span across spaces in between words:
        # Spaces between words are bound to the preceding content box renderer,
        # MText is more flexible, but this implementation is easy and good
        # enough, otherwise spaces would need a distinct height and a rendering
        # object, both are not implemented for glue objects.
        continue_stroke = stroke + 8 if stroke else 0
        for word in group[:-1]:
            yield Word(word, font=font, stroke=continue_stroke)
            yield text_layout.Space(font.space)
        # strokes end at the last word, without continue stroke:
        yield Word(group[-1], font=font, stroke=stroke)
        yield text_layout.Space(font.space)


class Fraction(text_layout.Fraction):
    """Represents a fraction for the layout engine, which consist of a top-
    and bottom content box, divided by horizontal or slanted line.
    The "tolerance style" has no line between the stacked content boxes.

    This implementation is more flexible than MText, the content boxes can be
    words but also fractions or cell groups.

    """

    def __init__(self, t1: str, t2: str, stacking: Stacking, font: SizedFont):
        top = Word(t1, font)
        bottom = Word(t2, font)
        super().__init__(
            top=top,
            bottom=bottom,
            stacking=stacking,
            # Uses only the generic line renderer to render the divider line,
            # the top- and bottom content boxes use their own render objects.
            renderer=FrameRenderer(color=7),
        )


def fraction_content() -> Content:
    """Create content with one text size and place random fractions between
    words.

    """
    words = list(uniform_content(120))
    for word in words:
        word.valign = text_layout.CellAlignment.BOTTOM

    stacking_options = [Stacking.OVER, Stacking.LINE, Stacking.SLANTED]
    font = SizedFont(0.25)  # fraction font
    for _ in range(10):
        stacking = random.choice(stacking_options)
        top = str(random.randint(1, 1000))
        bottom = str(random.randint(1, 1000))
        pos = random.randint(0, len(words) - 1)
        if isinstance(words[pos], text_layout.Space):
            pos += 1
        words.insert(pos, Fraction(top, bottom, stacking, font))
        words.insert(pos + 1, text_layout.Space(font.space))
    return words


def create_layout(align: "ParagraphAlignment", content: Content):
    # Create a flow text paragraph for the content:
    paragraph = text_layout.Paragraph(align=align)
    paragraph.append_content(content)

    # Start the layout engine and set default column width:
    layout = text_layout.Layout(
        width=8,  # default column width for columns without define width
        margins=(0.5,),  # space around the layout
        # The render object of collections like Layout, Column or Paragraph is
        # called before the render objects of the content managed by the
        # collection.
        # This could be used to render a frame or a background:
        renderer=FrameRenderer(color=2),
    )

    # Append the first column with default width and a content height of 12 drawing
    # units. At least the first column has to be created by the client.
    layout.append_column(height=COLUMN_HEIGHT, gutter=1)

    # Append the content. The content will be distributed across the available
    # columns and automatically overflow into adjacent columns if necessary.
    # The layout engine creates new columns automatically if required by
    # cloning the last column.
    layout.append_paragraphs([paragraph])

    # Content- and total size is always up to date, only the final location
    # has to be updated by calling Layout.place().
    print()
    print(f"Layout has {len(layout)} columns.")
    print(f"Layout total width: {layout.total_width}")
    print(f"Layout total height: {layout.total_height}")

    for n, column in enumerate(layout, start=1):
        print()
        print(f"  {n}. column has {len(column)} paragraph(s)")
        print(f"  Column total width: {column.total_width}")
        print(f"  Column total height: {column.total_height}")

    # It is recommended to place the layout at origin (0, 0) and use a
    # transformation matrix to move the layout to the final location in
    # the DXF target layout - the model space in this example.
    # Set final layout location in the xy-plane with alignment:
    layout.place(align=text_layout.LayoutAlignment.BOTTOM_LEFT)

    # It is possible to add content after calling place(), but place has to be
    # called again before calling the render() method of the layout.
    return layout


def create(content: Content, y: float) -> None:
    x: float = 0
    for align in list(ParagraphAlignment)[1:]:
        # Build and place the layout at (0, 0):
        layout = create_layout(align, content)
        # Render and move the layout to the final location:
        m = Matrix44.translate(x, y, 0)
        layout.render(m)
        x += layout.total_width + 2


dy = COLUMN_HEIGHT + 3
create(list(uniform_content(200)), 0)
create(list(random_sized_content(200)), dy)
create(list(stroked_content(200)), 2 * dy)
create(fraction_content(), 3 * dy)

zoom.extents(msp, factor=1.1)
doc.saveas(str(DIR / "text_layout.dxf"))
