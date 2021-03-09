#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Sequence, Iterable, Optional, Tuple, List
import abc
from ezdxf.math import Matrix44


class ContentRenderer(abc.ABC):
    @abc.abstractmethod
    def render(self, left: float, bottom: float, right: float,
               top: float, m: Matrix44 = None):
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
             m: Matrix44 = None):
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


def insert_location(align: int, width: float, height: float) -> Tuple2f:
    """ Returns the left top corner adjusted to the given alignment.
    """
    left = 0
    top = 0
    center = width / 2
    middle = height / 2
    if align == 1:
        pass
    elif align == 2:
        left, top = (-center, 0)
    elif align == 3:
        left, top = (-width, 0)
    elif align == 4:
        left, top = (0, middle)
    elif align == 5:
        left, top = (-center, middle)
    elif align == 6:
        left, top = (-width, middle)
    elif align == 7:
        left, top = (0, height)
    elif align == 8:
        left, top = (-center, height)
    elif align == 9:
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
    def render(self, x: float = 0, y: float = 0,
               m: Matrix44 = None) -> Iterable:
        pass


class Glue(Box):  # ABC
    EMPTY = tuple()

    def __init__(self, width: float = 0, min_width: float = 0):
        self._min_width: float = min_width
        self._width: float = 0
        self.resize(width)

    def resize(self, width: float):
        self._width = max(width, self._min_width)

    @property
    def total_width(self) -> float:
        return self._width

    @property
    def total_height(self) -> float:
        return 0

    def render(self, x: float = 0, y: float = 0,
               m: Matrix44 = None) -> Iterable:
        return self.EMPTY  # render nothing

    def forward(self, x: float, stops: Sequence[float] = EMPTY) -> float:
        """ Forward cursor (x-coordinate).

        Args:
            x: current cursor coordinate
            stops: designated tab stops

        """
        return x + self._width

    def is_line_break_possible(self) -> bool:
        return True


class Space(Glue):
    pass


class NonBreakingSpace(Glue):
    def is_line_break_possible(self) -> bool:
        return False


class Tab(Glue):
    def forward(self, x: float, stops: Sequence[float] = Glue.EMPTY) -> float:
        for stop in stops:
            if stop > x:
                return stop
        return x + self.total_width


class Cell(Box):  # ABC
    def __init__(self, width: float,
                 height: float,
                 renderer: ContentRenderer):
        self._width = width
        self._height = height
        self._renderer = renderer

    @property
    def total_width(self) -> float:
        return self._width

    @property
    def total_height(self) -> float:
        return self._height

    def render(self, x: float = 0, y: float = 0,
               m: Matrix44 = None) -> Iterable:
        """ (x, y) is the top/left corner """
        yield from self._renderer.render(
            left=x, bottom=y - self.total_height,
            right=x + self.total_width, top=y, m=m)


class Text(Cell):
    pass


class Fraction(Cell):
    pass


class Container(Box):
    def __init__(self, width: float,
                 height: float = None,
                 margins: Sequence[float] = None,
                 render: ContentRenderer = None):
        # content total_width is None for: defined by content
        self._content_width = width

        # content height is None for: defined by content
        self._content_height = height

        # margins are always defined
        self._margins = resolve_margins(margins)

        # content renderer is optional:
        self._render: Optional = render

    @abc.abstractmethod
    def __iter__(self):
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
        if self.content_height is None:
            return 0
        else:
            return self._content_height

    @property
    def total_height(self) -> float:
        return self.content_height + self.top_margin + self.bottom_margin

    def render(self, x: float = 0, y: float = 0,
               m: Matrix44 = None) -> Iterable:
        """ Render container content.

        (x, y) is the top/left corner

        """
        if self._render:
            yield self.render_background(x, y, m)

        x += self.left_margin
        y -= self.top_margin
        self.render_content(x, y, m)

    @abc.abstractmethod
    def render_content(self, x: float = 0, y: float = 0,
                       m: Matrix44 = None) -> Iterable:
        pass

    def render_background(self, x: float, y: float, m: Matrix44):
        """ (x, y) is the top/left corner """
        # Render content background inclusive margins!
        if self._render:
            return self._render.render(
                left=x, bottom=y - self.total_height,
                top=y, right=x + self.total_width, m=m)
        return None


class VContainer(Container, abc.ABC):
    def render_content(self, x: float = 0, y: float = 0,
                       m: Matrix44 = None) -> Iterable:
        """ Top to bottom content rendering.

        (x, y) is the top/left corner

        """
        for entity in self:
            yield from entity.render(x, y, m)
            y -= entity.total_height


class HContainer(Container, abc.ABC):
    def render_content(self, x: float = 0, y: float = 0,
                       m: Matrix44 = None) -> Iterable:
        """ Left to right content rendering.

        (x, y) is the top/left corner

        """
        for entity in self:
            yield from entity.render(x, y, m)
            x += entity.total_width


class Line(HContainer):
    def __init__(self, width: float,
                 align: int = 0,
                 margins: Sequence[float] = None,
                 render: ContentRenderer = None):
        super().__init__(width, None, margins, render)
        self._align = align
        self._cells: List[Cell] = []

    def __iter__(self):
        return iter(self._cells)


class Paragraph(VContainer):
    def __init__(self, width: float,
                 align: int = 0,
                 indent: Tuple[float, float, float] = None,
                 tab_stops: Sequence[float] = None,
                 margins: Sequence[float] = None,
                 render: ContentRenderer = None):
        super().__init__(width, None, margins, render)
        self._align = int(align)
        if not (0 <= self._align < 5):
            raise ValueError("invalid paragraph alignment (0-4)")
        first, left, right = indent
        self._indent_first = first
        self._indent_left = left
        self._indent_right = right
        self.tab_stops = list(tab_stops) if tab_stops else []
        self._lines: List[Line] = []

    def __iter__(self):
        return iter(self._lines)

    def split(self, height: float) -> Optional['Paragraph']:
        """ Split paragraph if total height is bigger than `height`.

        Returns the separated part of the paragraph.

        """
        pass


class Column(VContainer):
    def __init__(self, width: float,
                 height: float = None,
                 gutter: float = 0,
                 margins: Sequence[float] = None,
                 render: ContentRenderer = None):
        super().__init__(width, height, margins, render)
        # spacing between columns
        self._gutter = gutter
        self._paragraphs: List[Paragraph] = []

    def __iter__(self):
        return iter(self._paragraphs)

    @property
    def content_height(self) -> float:
        if self._content_height is None:
            return self._calculate_content_height()
        else:
            return self._content_height

    def _calculate_content_height(self) -> float:
        return sum(p.total_height for p in self._paragraphs)

    @property
    def gutter(self):
        return self._gutter


class Layout(HContainer):
    def __init__(self, width: float,
                 height: float = None,
                 align: int = 1,
                 margins: Sequence[float] = None,
                 render: ContentRenderer = None):
        super().__init__(width, height, margins, render)
        self._reference_column_width = width
        self.align = align
        self._columns: List[Column] = []

    def __iter__(self):
        return iter(self._columns)

    @property
    def content_width(self):
        width = self._content_width
        if self._columns:
            width = self._calculate_content_width()
        return width

    def _calculate_content_width(self) -> float:
        width = sum(c.total_width + c.gutter for c in self._columns[:-1])
        if len(self._columns) > 1:
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

    def render(self, x: float = 0, y: float = 0,
               m: Matrix44 = None) -> Iterable:
        """ Render content at the insertion point (x, y) with the
        alignment defined by the argument `align`.

        === ================
        1   Top left
        2   Top center
        3   Top right
        4   Middle left
        5   Middle center
        6   Middle right
        7   Bottom left
        8   Bottom center
        9   Bottom right
        === ================

        """

        width = self.total_width
        height = self.total_height
        left, top = insert_location(self.align, width, height)

        # Render content (background) inclusive margins!
        # MText background filling!
        if self._render:
            yield self.render_background(left, top, m)

        x = (x + left) + self.left_margin
        y = (y + top) - self.top_margin
        for column in self:
            yield column.render(x, y, m)
            x += column.total_width + column.gutter

    def append_column(self, width: float = None, height: float = None,
                      gutter: float = 0,
                      margins: Sequence[float] = None,
                      render: ContentRenderer = None) -> Column:
        """ Append a new column to the layout. """
        if not width:
            width = self._reference_column_width
        column = Column(width, height, gutter, margins, render)
        self._columns.append(column)
        return column

    def append_paragraph(self,
                         align: int = 0,
                         indent=(0, 0, 0),
                         tab_stops: Sequence[float] = None,
                         margins: Sequence[float] = None,
                         render: ContentRenderer = None) -> Paragraph:
        """ Append a new paragraph to the next column with available space.

        === =================
            Alignment
        === =================
        0   default
        1   left
        2   right
        3   center
        4   justified
        === =================

        """
        pass
