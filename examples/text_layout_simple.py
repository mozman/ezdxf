#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pathlib
import random
import itertools
import ezdxf
from ezdxf import zoom
from ezdxf.math import Matrix44
from ezdxf.tools import fonts
from ezdxf.tools import text_layout

DIR = pathlib.Path('~/Desktop/Outbox').expanduser()
LOREM_IPSUM = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed 
diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed 
diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet 
clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
"""


def lorem_ipsum(count=100):
    return itertools.islice(itertools.cycle(LOREM_IPSUM.split()), count)


STYLE = 'Style0'
FONT = 'OpenSans-Regular.ttf'
CAP_HEIGHT = 0.35

doc = ezdxf.new()
msp = doc.modelspace()
style = doc.styles.new(STYLE, dxfattribs={'font': FONT})
font = fonts.MatplotlibFont(FONT, CAP_HEIGHT)


class FrameRenderer(text_layout.ContentRenderer):
    def __init__(self, color):
        self.color = color

    def render(self, left: float, bottom: float, right: float,
               top: float, m: Matrix44 = None) -> None:
        pline = msp.add_lwpolyline(
            [(left, top), (right, top), (right, bottom), (left, bottom)],
            close=True, dxfattribs={'color': self.color},
        )
        if m:
            pline.transform(m)

    def line(self, x1: float, y1: float, x2: float, y2: float,
             m: Matrix44 = None) -> None:
        pass


class TextRenderer(text_layout.ContentRenderer):
    def __init__(self, text, attribs):
        self.text = text
        self.attribs = attribs

    def render(self, left: float, bottom: float, right: float,
               top: float, m: Matrix44 = None):
        text = msp.add_text(self.text, dxfattribs=self.attribs)
        text.set_pos((left, bottom), align='LEFT')
        if m:
            text.transform(m)

    def line(self, x1: float, y1: float, x2: float, y2: float,
             m: Matrix44 = None) -> None:
        pass


class Word(text_layout.Text):
    def __init__(self, text: str):
        attribs = {
            'color': random.choice((1, 2, 3, 4, 6)),
            'height': CAP_HEIGHT,
            'style': STYLE,
        }
        super().__init__(
            width=font.text_width(text),
            height=CAP_HEIGHT,
            renderer=TextRenderer(text, attribs),
        )


def measure_space(font):
    return font.text_width('X X') - font.text_width('XX')


def build_content(count: int):
    space = measure_space(font)
    for word in lorem_ipsum(count):
        yield Word(word)
        yield text_layout.Space(space)


# Build the content:
paragraph = text_layout.FlowText()
paragraph.append_content(build_content(200))

# Start the layout engine and set default column width:
layout = text_layout.Layout(width=8, margins=(0.5,),
                            renderer=FrameRenderer(2))

# Append the first column with default width and a content height of 12 drawing
# units. At least the first column has to be created by the client.
layout.append_column(height=12, gutter=1)

# Append the content. The content will be distributed across the available
# columns and automatically overflow into adjacent columns if necessary.
# Creates new columns if required by cloning the last column.
layout.append_paragraphs([paragraph])

print(f"Layout has {len(layout)} columns.")
for n, column in enumerate(layout, start=1):
    print(f"  {n}. column has {len(column)} paragraph(s)")

# Place layout in model space, this also triggers the final size calculation:
layout.place(10, 100)

# Render/create entities:
layout.render()

zoom.extents(msp, factor=1.1)
doc.saveas(DIR / "simple_layout.dxf")
