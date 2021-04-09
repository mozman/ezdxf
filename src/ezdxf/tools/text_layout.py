#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Sequence, Iterable, Optional, Tuple, List
import abc
import math
import itertools
import enum
from ezdxf.math import Matrix44

"""

Text Layout Engine
==================

The main goal of this text layout engine is to layout words as boxes in 
columns, paragraphs, and (bullet) lists. 

The starting point is a layout engine for MTEXT, which can be used for 
different purposes like the drawing add-on or exploding MTEXT into DXF 
primitives. But the engine is not bound to the MTEXT entity, the MTEXT 
entity just defines the basic requirements.

This engine works on given (text) boxes as input and does not render the glyphs
by itself nor does it have any knowledge about the glyphs, therefore individual 
kerning between letters is not supported in anyway. As consequence the 
"distributed" paragraph alignment of MTEXT can not be supported.

Each input box can have an individual rendering object attached, derived from 
the :class:`ContentRenderer` class, which requires two methods:

1. method :meth:`render` to render the box content like the text or the 
   container background

2. method :meth:`line` to render simple straight lines like under- and over 
   stroke lines or fraction dividers.

Soft hyphens or auto word wrapping is not supported.

Text direction is determined by the client by the given arrangement of the 
input cells, but the vertical flow is always organized in lines from top to 
bottom.

The main work done by the layout engine is the placing of the given content 
cells. The layout engine does not change the size of content cells and only 
adjusts the width of glue cells e.g. "justified" paragraphs.

Switching fonts or changing text size and -color has to be done by the client 
at the process of dividing the input text into text- and glue cells and 
assigning them appropriate rendering functions.

The only text styling provided by the layout engine are strokes above, through 
or below one or more words, which have to span across glue cells.

Content organization
--------------------

The content is divided into containers (layout, column, paragraphs, ...) and
simple boxes for the actual content as cells like words and glue cells like 
spaces or tabs.

The basic content object is a text cell, which represents a single word. 
Fractions of the MTEXT entity are supported by fraction cells. Content cells
have to be separated by mandatory glue cells. 
Non breaking spaces have to be fed into the layout engine as special glue 
element, because it is also a simple space, which should be adjustable in the 
"justified" paragraph alignment. 

Containers
----------

All containers support margins.

1. Layout

    Contains only columns. The size of the layout is determined by the 
    columns inside of the layout. Each column can have a different width.
    
2. Column
    
    Contains only paragraphs. A Column has a fixed width, the height can be
    fixed (MTEXT) or flexible.
    
3. Paragraph

    A paragraph has a fixed width and the height is always flexible.
    A paragraph can contain anything except the high level containers
    Layout and Column.
    
    3.1 FlowText, supports left, right, center and justified alignments;
        indentation for the left side, the right side and the first line; 
        line spacing; no nested paragraphs or bullet lists;
        The final content is distributed as lines (HCellGroup).
        
    3.2 BulletList, the "bullet" can be any text cell, the flow text of each
        list is an paragraph with left aligned text ...

Simple Boxes
------------

Do not support margins.

1. Glue cells

    The height of glue cells is always 0.

    1.1 Space, flexible width but has a minimum width, possible line break
    1.2 Non breaking space, like a space but prevents line break between 
        adjacent text cells
    1.3 Tabulator, the current implementation treats tabulators like spaces. 

2. Content cells

    2.1 Text cell - the height of a text cell is the cap height (height of 
        letter "X"), ascenders and descenders are ignored. 
        This is not a clipping box, the associated render object can still draw 
        outside of the box borders, this box is only used to determine the final 
        layout location.
        
    2.2 Fraction cell ... (MTEXT!)

3. HCellGroup (H for horizontal, a.k.a. Line)
    
    A line contains only simple boxes and has a fixed width. 
    The height is determined by the tallest box of the group. 
    The content cells (words) are connected/separated by mandatory glue cells.

"""

LOREM_IPSUM = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed 
diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed 
diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet 
clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
"""


def lorem_ipsum(count=100):
    return itertools.islice(itertools.cycle(LOREM_IPSUM.split()), count)


class ContentRenderer(abc.ABC):
    @abc.abstractmethod
    def render(self, left: float, bottom: float, right: float,
               top: float, m: Matrix44 = None) -> None:
        """ Render content into the given borders (lower left and upper right
        corners).

        Args:
            left: x coordinate of the left border
            bottom: y coordinate of the bottom border
            right: x coordinate of the right border
            top: y coordinate of the top border
            m: transformation Matrix44

        """
        pass

    @abc.abstractmethod
    def line(self, x1: float, y1: float, x2: float, y2: float,
             m: Matrix44 = None) -> None:
        """ Draw a line from (x1, y1) to (x2, y2). """
        pass


Tuple4f = Tuple[float, float, float, float]
Tuple2f = Tuple[float, float]


def resolve_margins(margins: Optional[Sequence[float]]) -> Tuple4f:
    """ Returns the box margins in CSS like order: top, right, bottom, left.
    """
    if margins is None:
        return 0, 0, 0, 0
    count = len(margins)
    if count == 4:  # CSS: top, right, bottom, left
        return margins[0], margins[1], margins[2], margins[3]
    elif count == 3:  # CSS: top, right, bottom, left=right
        return margins[0], margins[1], margins[2], margins[1]
    elif count == 2:  # CSS: top, right, bottom=top, left=right
        return margins[0], margins[1], margins[0], margins[1]
    elif count == 1:  # CSS: top, right=top, bottom=top, left=top
        return margins[0], margins[0], margins[0], margins[0]


class LayoutAlignment(enum.IntEnum):
    TOP_LEFT = 1
    TOP_CENTER = 2
    TOP_RIGHT = 3
    MIDDLE_LEFT = 4
    MIDDLE_CENTER = 5
    MIDDLE_RIGHT = 6
    BOTTOM_LEFT = 7
    BOTTOM_CENTER = 8
    BOTTOM_RIGHT = 9


def insert_location(align: LayoutAlignment,
                    width: float, height: float) -> Tuple2f:
    """ Returns the left top corner adjusted to the given alignment.
    """
    left = 0
    top = 0
    center = width / 2
    middle = height / 2
    if align == LayoutAlignment.TOP_LEFT:
        pass
    elif align == LayoutAlignment.TOP_CENTER:
        left, top = (-center, 0)
    elif align == LayoutAlignment.TOP_RIGHT:
        left, top = (-width, 0)
    elif align == LayoutAlignment.MIDDLE_LEFT:
        left, top = (0, middle)
    elif align == LayoutAlignment.MIDDLE_CENTER:
        left, top = (-center, middle)
    elif align == LayoutAlignment.MIDDLE_RIGHT:
        left, top = (-width, middle)
    elif align == LayoutAlignment.BOTTOM_LEFT:
        left, top = (0, height)
    elif align == LayoutAlignment.BOTTOM_CENTER:
        left, top = (-center, height)
    elif align == LayoutAlignment.BOTTOM_RIGHT:
        left, top = (-width, height)
    return left, top


class Box(abc.ABC):

    @property
    @abc.abstractmethod
    def total_width(self) -> float:
        pass

    @property
    @abc.abstractmethod
    def total_height(self) -> float:
        pass

    @abc.abstractmethod
    def place(self, x: float, y: float):
        """ (x, y) is the top/left corner """
        pass

    @abc.abstractmethod
    def final_location(self) -> Tuple[float, float]:
        """ Returns the final location as the top/left corner """
        pass

    @abc.abstractmethod
    def render(self, m: Matrix44 = None) -> None:
        """ Render content at the final location. """
        pass


class Cell(Box):  # ABC
    is_visible = False

    def place(self, x: float, y: float):
        # Base cells do not render anything, therefore placing the content is
        # not necessary
        pass

    def final_location(self) -> Tuple[float, float]:
        # Base cells do not render anything, therefore final location is not
        # important
        return 0, 0

    def render(self, m: Matrix44 = None) -> None:
        pass


class Glue(Cell):  # ABC
    EMPTY = tuple()

    def __init__(self, width: float, min_width: float = None,
                 max_width: float = None):
        self._width: float = float(width)
        self._min_width = float(min_width) if min_width else self._width
        self._max_width: Optional[float] = max_width

    def resize(self, width: float):
        max_width = self._max_width
        if max_width is not None:
            width = min(max_width, width)
        self._width = max(width, self._min_width)

    @property
    def can_shrink(self):
        return self._min_width < self._width

    @property
    def can_grow(self):
        return self._max_width is None or self._width < self._max_width

    @property
    def total_width(self) -> float:
        return self._width

    @property
    def total_height(self) -> float:
        return 0

    def to_space(self) -> 'Space':
        return Space(self._width, self._min_width, self._max_width)


class Space(Glue):
    pass


class NonBreakingSpace(Glue):
    pass


class CellAlignment(enum.IntEnum):
    BOTTOM = 0
    CENTER = 1
    TOP = 2


class ContentCell(Cell):  # ABC
    """ Represents visible content like text or fractions.

    Supported vertical alignments (IntEnum):

        === =================
        int CellAlignment
        === =================
        0   BOTTOM
        1   CENTER
        2   TOP
        === =================

    """
    is_visible = True

    def __init__(self, width: float,
                 height: float,
                 valign: CellAlignment = CellAlignment.BOTTOM,
                 renderer: ContentRenderer = None):
        self._final_x = None
        self._final_y = None
        self._width = float(width)
        self._height = float(height)
        self.valign = CellAlignment(valign)  # public attribute read/write
        self.renderer = renderer

    def set_final_location(self, x: float, y: float):
        self._final_x = x
        self._final_y = y

    def final_location(self):
        return self._final_x, self._final_y

    @property
    def total_width(self) -> float:
        return self._width

    @property
    def total_height(self) -> float:
        return self._height

    def place(self, x: float, y: float):
        """ (x, y) is the top/left corner """
        self._final_x = x
        self._final_y = y


class Stroke:
    # no enum because bit values can be combined: UNDERLINE + OVERLINE
    NO_STROKE = 0
    UNDERLINE = 1
    STRIKE_THROUGH = 2
    OVERLINE = 4
    CONTINUE = 8  # continue stroke to following text cell


class Text(ContentCell):
    """ Represents visible text content.

    Supported strokes as bit values (flags), can be combined:

        === =================
        int Stroke
        === =================
        0   NO_STROKE
        1   UNDERLINE
        2   STRIKE THROUGH
        4   OVERLINE
        8   CONTINUE
        === =================

    The CONTINUE flag extends the stroke of the current text cell across the
    glue cells to the following text cell.

    """

    def __init__(self, width: float,
                 height: float,
                 valign: CellAlignment = CellAlignment.BOTTOM,
                 stroke: int = Stroke.NO_STROKE,
                 renderer: ContentRenderer = None):
        super().__init__(width, height, valign, renderer)
        self.stroke = int(stroke)  # public attribute read/write

    def render(self, m: Matrix44 = None) -> None:
        left, top = self.final_location()
        height = self.total_height
        bottom = top - height
        right = left + self.total_width
        renderer = self.renderer

        # render content
        renderer.render(
            left=left, bottom=bottom,
            right=right, top=top, m=m)

    def render_stroke(self,
                      extend_left: float = 0,
                      extend_right: float = 0,
                      m: Matrix44 = None) -> None:
        left, top = self.final_location()
        left -= extend_left
        height = self.total_height
        bottom = top - height
        right = left + self.total_width + extend_right
        renderer = self.renderer

        # render underline, strike through, overline
        spacing = height / 5  # ???
        if self.stroke & Stroke.UNDERLINE:
            y = bottom - spacing
            renderer.line(left, y, right, y, m)
        if self.stroke & Stroke.STRIKE_THROUGH:
            y = (top + bottom) / 2
            renderer.line(left, y, right, y, m)
        if self.stroke & Stroke.OVERLINE:
            y = top + spacing
            renderer.line(left, y, right, y, m)


def render_text_strokes(cells: List[Cell], m: Matrix44 = None) -> None:
    """ Render text cell strokes across glue cells. """

    # Should be called for container with horizontal arranged text cells
    # like HCellGroup to create underline, overline and strike trough
    # features.
    # Can not render strokes across line breaks!
    def stroke_extension():
        extend = 0
        i = index + 1
        count = len(cells)
        while i < count:
            cell = cells[i]
            # extend stroke only across adjacent glue cells:
            if isinstance(cell, Glue):
                extend += cell.total_width
            else:
                break
            i += 1
        return extend

    for index, cell in enumerate(cells):
        if isinstance(cell, Text) and cell.stroke:
            extend = stroke_extension() if cell.stroke & Stroke.CONTINUE else 0
            cell.render_stroke(extend_right=extend, m=m)


class Stacking(enum.IntEnum):
    OVER = 0
    LINE = 1
    SLANTED = 2


class Fraction(ContentCell):
    """ Represents visible fractions.

    Supported stacking A/B (IntEnum):

        === =========== =========
        int Stacking    Description
        === =========== =========
        0   OVER        A over B, without horizontal line
        1   LINE        A over B, horizontal line between
        2   SLANTED     A slanted line B
        === =========== =========

    """

    def __init__(self, width: float,
                 height: float,
                 valign: CellAlignment = CellAlignment.BOTTOM,
                 renderer: ContentRenderer = None):
        super().__init__(width, height, valign, renderer)
        self._stacking = Stacking.OVER
        self._top_content: Optional[ContentCell] = None
        self._bottom_content: Optional[ContentCell] = None

    def set_content(self, top: ContentCell, bottom: ContentCell,
                    stacking: Stacking = Stacking.OVER):
        self._top_content = top
        self._bottom_content = bottom
        self._stacking = stacking

        # update content dimensions
        if self._stacking == Stacking.SLANTED:
            self._height = top.total_height + bottom.total_height
            self._width = top.total_width + bottom.total_width
        else:
            self._height = 1.2 * (top.total_height + bottom.total_height)
            self._width = max(top.total_width, bottom.total_width)

    def place(self, x: float, y: float):
        """ (x, y) is the top/left corner """
        self._final_x = x
        self._final_y = y
        width = self.total_width
        height = self.total_height
        top_content = self._top_content
        bottom_content = self._bottom_content
        if top_content is None or bottom_content is None:
            raise ValueError('no content set')

        if self._stacking == Stacking.SLANTED:
            top_content.place(x, y)  # left/top
            x += width - bottom_content.total_width
            y -= height + bottom_content.total_height
            bottom_content.place(x, y)  # right/bottom
        else:
            center = x + width / 2
            x = center - top_content.total_width / 2
            top_content.place(x, y)  # center/top
            x = center - bottom_content.total_width / 2
            y -= height + bottom_content.total_height
            bottom_content.place(x, y)  # center/bottom

    def render(self, m: Matrix44 = None) -> None:
        self._top_content.render(m)
        self._bottom_content.render(m)
        if self._stacking == Stacking.LINE:
            pass
        elif self._stacking == Stacking.SLANTED:
            pass


_content = {Text, Fraction}
_glue = {Space, NonBreakingSpace}
_no_break = {Text, Fraction, NonBreakingSpace}


def normalize_cells(cells: Iterable[Cell]) -> List[Cell]:
    def replace_pending_nbsp_by_spaces():
        index = len(content) - 1
        while index >= 0:
            cell = content[index]
            if type(cell) is NonBreakingSpace:
                content[index] = cell.to_space()
                index -= 1
            else:
                return

    def is_useless_nbsp():
        try:
            peek = type(cells[index + 1])
        except IndexError:
            return True
        if prev not in _no_break or peek not in _no_break:
            return True
        return False

    content = []
    cells = list(cells)
    prev = None
    for index, cell in enumerate(cells):
        current = type(cell)
        if current in _content:
            if prev in _content:
                raise ValueError('no glue between content cells')
        elif current is NonBreakingSpace and is_useless_nbsp():
            cell = cell.to_space()
            current = type(cell)
            replace_pending_nbsp_by_spaces()

        prev = current
        content.append(cell)

    # remove pending glue:
    while content and (type(content[-1]) in _glue):
        content.pop()

    return content


class HCellGroup(ContentCell):
    """ Stores content in horizontal order and does not render itself.
    Recursive data structure, a HCellGroup can contain cell groups as well.

    This is not a real container class, from outside it behaves like a
    single opaque cell with a fixed width and height determined by the
    extents of its content.

    """

    def __init__(self, cells: Iterable[Cell] = None,
                 valign=CellAlignment.BOTTOM):
        super().__init__(0, 0, valign=valign)
        self._cells: List[Cell] = []
        if cells:
            self.extend(cells)

    def __iter__(self):
        return iter(self._cells)

    def place(self, x: float, y: float):
        super().place(x, y)
        group_height = self.total_height
        cx = x
        for cell in self._cells:
            cy = y
            if isinstance(cell, ContentCell) and \
                    cell.valign != CellAlignment.TOP:
                dy = cell.total_height - group_height
                if cell.valign == CellAlignment.CENTER:
                    dy /= 2.0
                cy += dy

            cell.place(cx, cy)
            cx += cell.total_width

    def append(self, cell: Cell):
        self._height = max(cell.total_height, self._height)
        self._width += cell.total_width
        self._cells.append(cell)

    def extend(self, cells: Iterable[Cell]):
        for cell in cells:
            self.append(cell)

    def render(self, m: Matrix44 = None) -> None:
        for cell in self._cells:
            if cell.is_visible:
                cell.render(m)

        # HCellGroup can contain Text cells:
        render_text_strokes(self._cells, m)

    def grow(self, target_width: float) -> None:
        self._apply_justified_alignment(target_width)
        self.update_width()

    def update_width(self):
        self._width = sum(cell.total_width for cell in self._cells)

    def _glue_cells(self):
        return [cell for cell in self._cells if isinstance(cell, Glue)]

    def _apply_justified_alignment(self, target_width: float) -> None:
        # TODO: ignore "short" lines
        success = False
        spaces: List[Glue] = self._glue_cells()
        if len(spaces) == 0:  # no spaces to grow
            return

        while not success:
            success = True
            # total line width could be bigger than width!
            space_to_distribute = target_width - self.total_width
            if space_to_distribute < 1e-6:
                return

            growable_spaces = [space for space in spaces if space.can_grow]
            count = len(growable_spaces)
            if count == 0:  # no spaces to grow
                return

            delta_space = space_to_distribute / count
            for space in growable_spaces:
                new_size = space.total_width + delta_space
                space.resize(new_size)
                if not math.isclose(new_size, space.total_width):
                    # space can't grow that much
                    success = False
                    # but grow remaining spaces


class Container(Box):
    def __init__(self, width: float,
                 height: float = None,
                 margins: Sequence[float] = None,
                 renderer: ContentRenderer = None):
        self._final_x = None
        self._final_y = None

        # _content_width is None for: defined by content
        self._content_width = width

        # _content_height is None for: defined by content
        self._content_height = height

        # margins are always defined
        self._margins = resolve_margins(margins)

        # content renderer is optional:
        self.renderer: Optional = renderer

    def place(self, x: float, y: float):
        self._final_x = x
        self._final_y = y
        self.place_content()

    def final_location(self):
        if not self.is_placed():
            raise ValueError('Container is not placed.')
        return self._final_x, self._final_y

    def is_placed(self) -> bool:
        return self._final_x is not None and self._final_y is not None

    @abc.abstractmethod
    def __iter__(self) -> Box:
        pass

    @property
    def top_margin(self) -> float:
        return self._margins[0]

    @property
    def right_margin(self) -> float:
        return self._margins[1]

    @property
    def bottom_margin(self) -> float:
        return self._margins[2]

    @property
    def left_margin(self) -> float:
        return self._margins[3]

    @property
    def content_width(self) -> float:
        if self._content_width is None:
            return 0
        else:
            return self._content_width

    @property
    def total_width(self) -> float:
        return self.content_width + self.right_margin + self.left_margin

    @property
    def content_height(self) -> float:
        if self._content_height is None:
            return 0
        else:
            return self._content_height

    @property
    def has_flex_height(self):
        return self._content_height is None

    @property
    def total_height(self) -> float:
        return self.content_height + self.top_margin + self.bottom_margin

    def render(self, m: Matrix44 = None) -> None:
        """ Render container content.

        (x, y) is the top/left corner
        """
        if not self.is_placed():
            raise ValueError('Layout has to be placed before rendering')
        if self.renderer:
            self.render_background(m)
        self.render_content(m)

    @abc.abstractmethod
    def place_content(self):
        """ Place container content at the final location. """
        pass

    def render_content(self, m: Matrix44 = None) -> None:
        """ Render content at the final location. """
        for entity in self:
            entity.render(m)

    def render_background(self, m: Matrix44) -> None:
        """ Render background at the final location. """
        # Render content background inclusive margins!
        # (x, y) is the top/left corner
        x, y = self.final_location()
        if self.renderer:
            self.renderer.render(
                left=x, bottom=y - self.total_height,
                top=y, right=x + self.total_width, m=m)


class Paragraph(Container):  # ABC
    @abc.abstractmethod
    def distribute_content(self, height: float = None):
        pass

    @abc.abstractmethod
    def set_total_width(self, width: float):
        pass


class FlowTextAlignment(enum.IntEnum):
    DEFAULT = 0
    LEFT = 1
    RIGHT = 2
    CENTER = 3
    JUSTIFIED = 4


class FlowText(Paragraph):
    """ Single paragraph of flow text.

    Supported paragraph alignments (IntEnum):

        === =================
        int FlowTextAlignment
        === =================
        0   DEFAULT
        1   LEFT
        2   RIGHT
        3   CENTER
        4   JUSTIFIED
        === =================

    Paragraph indentation is supported by three values given as argument
    `indent`. The first value defines the left indentation of the first line,
    the following two values define the common line indentation for the left
    and right side. The indentation value is a positive value, measured from
    the border towards the inside of the paragraph.
    Negative values can be used, but are not tested nor officially supported.

    Line spacing is 3-on-5 and is based on the cap height, e.g. for a
    cap height of 1.0 the leading (distance from base line to base line)
    is 1.667. The `line_spacing` argument is an additional stretching factor.

    """
    _LEFT_AND_JUSTIFIED = (FlowTextAlignment.LEFT, FlowTextAlignment.JUSTIFIED)

    def __init__(self, width: float = None,  # defined by parent container
                 align: FlowTextAlignment = FlowTextAlignment.DEFAULT,
                 indent: Tuple[float, float, float] = (0, 0, 0),
                 line_spacing: float = 1,
                 margins: Sequence[float] = None,
                 renderer: ContentRenderer = None):
        super().__init__(width, None, margins, renderer)
        self._align = align
        first, left, right = indent
        self._indent_first = first
        self._indent_left = left
        self._indent_right = right
        self._line_spacing = line_spacing

        # contains the raw and not distributed content:
        self._cells: List[Cell] = []

        # contains the final distributed content:
        self._lines: List[HCellGroup] = []

    def __iter__(self):
        return iter(self._lines)

    def set_total_width(self, width: float):
        self._content_width = width - self.left_margin - self.right_margin
        if self._content_width < 1e-6:
            raise ValueError('invalid width, no usable space left')

    def place_content(self):
        x, y = self.final_location()
        x += self.left_margin
        y -= self.top_margin
        justified_alignment = self._align == FlowTextAlignment.JUSTIFIED
        first = True
        available_width = self.line_width(first)
        for line in self._lines:
            if justified_alignment:
                line.grow(available_width)
            x_final = self._left_border(x, line, first, available_width)
            line.place(x_final, y)
            y -= leading(line.total_height, self._line_spacing)
            if first:
                first = False
                available_width = self.line_width(first)

    def _left_border(self, x: float, line: HCellGroup, first: bool,
                     available_width: float) -> float:
        """ Apply indentation and paragraph alignment """
        alignment = self._align
        if alignment == FlowTextAlignment.DEFAULT:
            alignment = FlowTextAlignment.LEFT

        left_indent = self._indent_first if first else self._indent_left
        left_border = x + left_indent
        if alignment in FlowText._LEFT_AND_JUSTIFIED:
            return left_border

        right_border = left_border + available_width
        if alignment == FlowTextAlignment.RIGHT:
            return right_border - line.total_width
        elif alignment == FlowTextAlignment.CENTER:
            center = (right_border + left_border) / 2
            return center - line.total_width / 2
        return left_border

    def _calculate_content_height(self) -> float:
        """ Returns the actual content height determined by the distributed
        lines.
        """
        return sum(
            leading(line.total_height, self._line_spacing)
            for line in self._lines
        )

    def distribute_content(self, height: float = None) -> Optional['FlowText']:
        """ Distribute the raw content into lines. Returns the cells which do
        not fit as a new paragraph.

        Args:
            height: available total height (margins + content), ``None`` for
                unrestricted paragraph height

        """

        # This method does not apply indentation or alignment,
        # see place_content() method.

        def remove_line_breaking_space(cells: List[Cell]):
            """ Remove last space """
            if cells and isinstance(cells[-1], Space):
                cells.pop()

        def next_group(cells):
            """ Returns the next group:

                - single content Text or Fraction
                - single Space or Tab
                - content connected by nbsp

            """
            group = []
            if cells:
                next_t = type(cells[-1])
                if next_t is NonBreakingSpace:
                    group.append(cells.pop())
                    group.extend(next_group(cells))
                elif next_t in _content:
                    group.append(cells.pop())
                    if cells and isinstance(cells[-1], NonBreakingSpace):
                        group.extend(next_group(cells))
                else:
                    group.append(cells.pop())
            return group

        def group_width(group: Iterable[Cell]):
            return sum(c.total_width for c in group)

        def append_line(cells_):
            nonlocal first
            first = False
            self._lines.append(cells_)

        # Refactoring required:
        # using indices into `cells` instead creating temp copies.

        cells = normalize_cells(self._cells)
        cells.reverse()
        undo = cells
        first = True
        paragraph_height = self.top_margin + self.bottom_margin
        while cells:
            if height is not None:  # is restricted
                # shallow copy current cell state for undo, if not enough space
                # for next line:
                undo = list(cells)
            available_space = self.line_width(first)
            line = []
            while cells and available_space:
                tmp_cells = list(cells)
                group = next_group(tmp_cells)
                width = group_width(group)
                if width <= available_space:
                    # add group to current line
                    cells = tmp_cells
                    line.extend(group)
                    available_space -= width
                else:  # not enough space for current group
                    # first group in current line?
                    if not line:
                        # add group as a line, which extends beyond borders!
                        cells = tmp_cells
                        line = group
                    available_space = 0

                if abs(available_space) < 1e-6:
                    remove_line_breaking_space(line)
                    remove_line_breaking_space(cells)

            if line:
                line_cells = HCellGroup(line)
                if height is None:  # unrestricted height
                    append_line(line_cells)
                else:  # height is restricted
                    # The line height is only defined if the content
                    # of the line is known:
                    line_height = line_cells.total_height
                    if paragraph_height + line_height > height:
                        # Not enough space for the new line:
                        cells = undo
                        break
                    else:
                        append_line(line_cells)
                        paragraph_height += leading(
                            line_height, self._line_spacing)

        # Delete raw content:
        self._cells = []

        # Update content height:
        self._content_height = self._calculate_content_height()

        # If not all cells could be processed, put them into a new paragraph
        # and return it to the caller.
        if cells:
            cells.reverse()
            return self._create_new_flow_text(cells, first)
        else:
            return None

    def _create_new_flow_text(self, cells: List[Cell],
                              first: bool) -> 'FlowText':
        # First line of the paragraph included?
        indent_first = self._indent_first if first else self._indent_left
        indent = (indent_first, self._indent_left, self._indent_right)
        flow_text = FlowText(
            self._content_width,
            self._align,
            indent,
            self._line_spacing,
            self._margins,
            self.renderer
        )
        flow_text.append_content(cells)
        return flow_text

    def line_width(self, first: bool) -> float:
        indent = self._indent_right
        indent += self._indent_first if first else self._indent_left
        return self.content_width - indent

    def append_content(self, content: Iterable[Cell]):
        self._cells.extend(content)


def leading(cap_height: float, line_spacing: float = 1.0) -> float:
    """ Returns the distance from baseline to baseline.

    Args:
        cap_height: cap height of the line
        line_spacing: line spacing factor as percentage of 3-on-5 spacing

    """
    # 3-on-5 line spacing = 5/3 = 1.667
    return cap_height * 1.667 * line_spacing


class BulletList(Paragraph):
    pass


class Column(Container):
    def __init__(self, width: float,
                 height: float = None,
                 gutter: float = 0,
                 margins: Sequence[float] = None,
                 renderer: ContentRenderer = None):
        super().__init__(width, height, margins, renderer)
        # spacing between columns
        self._gutter = gutter
        self._paragraphs: List[Paragraph] = []

    def clone_empty(self) -> 'Column':
        return self.__class__(
            width=self.content_width,
            height=self.content_height,
            gutter=self.gutter,
            margins=(self.top_margin, self.right_margin,
                     self.bottom_margin, self.left_margin),
            renderer=self.renderer
        )

    def __iter__(self):
        return iter(self._paragraphs)

    def __len__(self):
        return len(self._paragraphs)

    @property
    def content_height(self) -> float:
        """ Returns the current content height for flexible columns and the
        max. content height otherwise.
        """
        max_height = self.max_content_height
        if max_height is None:
            return self.used_content_height()
        else:
            return max_height

    def used_content_height(self) -> float:
        return sum(p.total_height for p in self._paragraphs)

    @property
    def gutter(self):
        return self._gutter

    @property
    def max_content_height(self) -> Optional[float]:
        return self._content_height

    @property
    def has_free_space(self) -> bool:
        if self.max_content_height is None:  # flexible height column
            return True
        return self.used_content_height() < self.max_content_height

    def place_content(self):
        x, y = self.final_location()
        x += self.left_margin
        y -= self.top_margin
        for p in self._paragraphs:
            p.place(x, y)
            y -= p.total_height

    def append_paragraphs(
            self, paragraphs: Iterable[Paragraph]) -> List[Paragraph]:
        remainer = []
        for paragraph in paragraphs:
            if remainer:
                remainer.append(paragraph)
                continue
            paragraph.set_total_width(self.content_width)
            if self.has_flex_height:
                height = None
            else:
                height = self.max_content_height - self.used_content_height()
            rest = paragraph.distribute_content(height)
            self._paragraphs.append(paragraph)
            if rest is not None:
                remainer.append(rest)
        return remainer


class Layout(Container):
    def __init__(self, width: float,
                 height: float = None,
                 margins: Sequence[float] = None,
                 renderer: ContentRenderer = None):
        super().__init__(width, height, margins, renderer)
        self._reference_column_width = width
        self._current_column = 0
        self._columns: List[Column] = []

    def __iter__(self):
        return iter(self._columns)

    def __len__(self):
        return len(self._columns)

    @property
    def content_width(self):
        width = self._content_width
        if self._columns:
            width = self._calculate_content_width()
        return width

    def _calculate_content_width(self) -> float:
        width = sum(c.total_width + c.gutter for c in self._columns[:-1])
        if self._columns:
            width += self._columns[-1].total_width
        return width

    @property
    def content_height(self):
        height = self._content_height
        if self._columns:
            height = self._calculate_content_height()
        elif height is None:
            height = 0
        return height

    def _calculate_content_height(self) -> float:
        return max(c.total_height for c in self._columns)

    def place(self, x: float = 0, y: float = 0,
              align: LayoutAlignment = LayoutAlignment.TOP_LEFT):
        """ Place layout and all sub-entities at the final location, relative
        to the insertion point (x, y) by the alignment defined by the argument
        `align` (IntEnum).

        === ================
        int LayoutAlignment
        === ================
        1   TOP_LEFT
        2   TOP_CENTER
        3   TOP_RIGHT
        4   MIDDLE_LEFT
        5   MIDDLE_CENTER
        6   MIDDLE_RIGHT
        7   BOTTOM_LEFT
        8   BOTTOM_CENTER
        9   BOTTOM_RIGHT
        === ================

        It is possible to add content after calling :meth:`place`, but
        :meth:`place` has to be called again before calling :meth:`render`.

        It is recommended to place the layout at origin (0, 0) and use a
        transformation matrix to move the layout to the final location in
        the target DXF layout.

        """

        width = self.total_width
        height = self.total_height
        left, top = insert_location(align, width, height)
        super().place(x + left, y + top)

    def place_content(self):
        """ Place content at the final location. """
        x, y = self.final_location()
        x = x + self.left_margin
        y = y - self.top_margin
        for column in self:
            column.place(x, y)
            x += column.total_width + column.gutter

    def append_column(self, width: float = None, height: float = None,
                      gutter: float = 0,
                      margins: Sequence[float] = None,
                      renderer: ContentRenderer = None) -> Column:
        """ Append a new column to the layout. """
        if not width:
            width = self._reference_column_width
        column = Column(width, height, gutter=gutter, margins=margins,
                        renderer=renderer)
        self._columns.append(column)
        return column

    def append_paragraphs(self, paragraphs: Iterable[Paragraph]):
        remainer = list(paragraphs)
        # 1. fill existing columns:
        columns = self._columns
        while self._current_column < len(columns):
            column = columns[self._current_column]
            remainer = column.append_paragraphs(remainer)
            if len(remainer) == 0:
                return
            self._current_column += 1

        # 2. create additional columns
        while remainer:
            column = self._new_column()
            self._current_column = len(self._columns) - 1
            remainer = column.append_paragraphs(remainer)
            if self._current_column > 100:
                raise ValueError("Internal error - not enough space!?")

    def _new_column(self) -> Column:
        if len(self._columns) == 0:
            raise ValueError("no column exist")
        empty = self._columns[-1].clone_empty()
        self._columns.append(empty)
        return empty
