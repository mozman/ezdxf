#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Sequence, Iterable, Optional, Tuple, List
import abc
from ezdxf.math import Matrix44


class ContentRenderer(abc.ABC):
    @abc.abstractmethod
    def render(self, left: float, bottom: float, right: float, top: float,
               m: Matrix44 = None):
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
    elif count == 1: # CSS: top, right=top, bottom=top, left=top
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
    def __init__(self, width: float,
                 height: float = None,
                 margins: Sequence[float] = None,
                 content: ContentRenderer = None):
        # content total_width is None for: defined by content
        self._content_width = width

        # content height is None for: defined by content
        self._content_height = height

        # margins are always defined
        self._margins = resolve_margins(margins)

        # content renderer is optional:
        self._content: Optional = content

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

    @abc.abstractmethod
    def render(self, x: float = 0, y: float = 0,
               m: Matrix44 = None) -> Iterable:
        pass

    def render_background(self, x: float, y: float, m: Matrix44):
        # Render content background inclusive margins!
        if self._content:
            return self._content.render(
                left=x, bottom=y - self.total_height,
                right=x + self.total_width, top=y, m=m)
        return None


class Column(Box):
    def __init__(self, width: float,
                 height: float = None,
                 gutter: float = 0,
                 margins: Sequence[float] = None,
                 content: ContentRenderer = None):
        super().__init__(width, height, margins, content)
        # spacing between columns
        self._gutter = gutter
        self._paragraphs: List[Box] = []

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

    def render(self, x: float = 0, y: float = 0,
               m: Matrix44 = None) -> Iterable:
        if self._content:
            yield self.render_background(x, y, m)

        x += self.left_margin
        y -= self.top_margin
        for paragraph in self._paragraphs:
            yield from paragraph.render(x, y, m)
            y -= paragraph.total_height

    def add_paragraph(self):
        self._content_height = None


class Layout(Box):
    def __init__(self, width: float,
                 height: float = None,
                 align: int = 1,
                 margins: Sequence[float] = None,
                 content: ContentRenderer = None):
        super().__init__(width, height, margins, content)
        self._reference_column_width = width
        self.align = align
        self._columns: List[Column] = []

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
        if self._content:
            yield self.render_background(left, top, m)

        x = (x + left) + self.left_margin
        y = (y + top) - self.top_margin
        for column in self._columns:
            yield column.render(x, y, m)
            x += column.total_width + column.gutter

    def add_column(self, width: float = None, height: float = None,
                   gutter: float = 0, margins=None, content=None):
        if not width:
            width = self._reference_column_width
        self._columns.append(Column(width, height, gutter, margins, content))
