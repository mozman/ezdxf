# Copyright (c) 2010-2022, Manfred Moitzi
# License: MIT License
"""Add-on for drawing simple tables by DXF primitives. This add-on does not
create ACAD_TABLE entities!

Cells can contain MTEXT or BLOCK references, or you can create your own
cell type by extending the CustomCell() class.

A Cell can span over multiple columns and/or rows.
Text cells can contain text with an arbitrary rotation angle, or letters can be
stacked from top to bottom.

BlockCells contains block references (INSERT) created from a block
definition (BLOCK), if the block definition contains attribute definitions
(ATTDEF), attribs will be added to the block reference (ATTRIB).

This add-on exist for porting :mod:`dxfwrite` projects to :mod:`ezdxf`.

"""
from __future__ import annotations
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Optional,
    Sequence,
    TYPE_CHECKING,
    TypeVar,
)
from copy import deepcopy

from ezdxf.lldxf import const
from ezdxf.enums import MAP_FLAGS_TO_STRING_ALIGN, MAP_STRING_ALIGN_TO_FLAGS
from .mtext import MText
from ezdxf.math import UVec, Vec2

if TYPE_CHECKING:
    from ezdxf.layouts import BlockLayout
    from ezdxf.eztypes import GenericLayoutType

DEFAULT_TABLE_BGLAYER = "TABLEBACKGROUND"
DEFAULT_TABLE_FGLAYER = "TABLECONTENT"
DEFAULT_TABLE_GRIDLAYER = "TABLEGRID"
DEFAULT_TABLE_HEIGHT = 1.0
DEFAULT_TABLE_WIDTH = 2.5
DEFAULT_TEXTSTYLE = "STANDARD"
DEFAULT_CELL_TEXT_HEIGHT = 0.7
DEFAULT_CELL_LINESPACING = 1.5
DEFAULT_CELL_XSCALE = 1.0
DEFAULT_CELL_YSCALE = 1.0
DEFAULT_CELL_TEXTCOLOR = const.BYLAYER
DEFAULT_CELL_BG_COLOR = None
DEFAULT_CELL_HMARGIN = 0.1
DEFAULT_CELL_VMARGIN = 0.1
DEFAULT_BORDER_COLOR = 5
DEFAULT_BORDER_LINETYPE = "BYLAYER"
DEFAULT_BORDER_STATUS = True
DEFAULT_BORDER_PRIORITY = 50

VISIBLE = 1
HIDDEN = 0

T = TypeVar("T", bound="Cell")


class Table:
    """Table object similar to an HTML table.

    The table object contains the table data cells.
    """

    def __init__(self, insert: UVec, nrows: int, ncols: int, default_grid=True):
        """
        Args:
            insert: insert location as or :class:`~ezdxf.math.UVec`
            nrows: row count
            ncols: column count
            default_grid: draw a grid of solid lines if ``True``, otherwise
                draw only explicit defined borders, the default grid has a
                priority of 50.

        """
        self.insert = Vec2(insert)
        self.nrows: int = nrows
        self.ncols: int = ncols
        self.row_heights: list[float] = [DEFAULT_TABLE_HEIGHT] * nrows
        self.col_widths: list[float] = [DEFAULT_TABLE_WIDTH] * ncols
        self.bglayer: str = DEFAULT_TABLE_BGLAYER
        self.fglayer: str = DEFAULT_TABLE_FGLAYER
        self.gridlayer: str = DEFAULT_TABLE_GRIDLAYER
        self.styles: dict[str, CellStyle] = {"default": CellStyle()}
        if not default_grid:
            default_style = self.get_cell_style("default")
            default_style.set_border_status(False, False, False, False)

        self._cells: dict[tuple[int, int], Cell] = {}  # data cells
        self.frames: list[Frame] = []  # border frame objects
        # data contains the resulting dxf entities
        self.data = None
        self.empty_cell = Cell(self)  # represents all empty cells

    def set_col_width(self, column: int, value: float):
        """Set column width in drawing units.

        Args:
            column: zero based column index
            value: new column width in drawing units

        """
        self.col_widths[column] = float(value)

    def set_row_height(self, row: int, value: float):
        """Set row height in drawing units.

        Args:
            row: zero based row index
            value: new row height in drawing units
        """
        self.row_heights[row] = float(value)

    def text_cell(
        self,
        row: int,
        col: int,
        text: str,
        span: tuple[int, int] = (1, 1),
        style="default",
    ) -> TextCell:
        """Create a new text cell at location (row, col), with `text` as
        content, the `text` can be a line breaks ``'\\n'``. The final cell can
        spread over several cells defined by the argument `span`.

        """
        cell = TextCell(self, text, style=style, span=span)
        return self.set_cell(row, col, cell)

    def block_cell(
        self,
        row: int,
        col: int,
        blockdef: BlockLayout,
        span: tuple[int, int] = (1, 1),
        attribs=None,
        style="default",
    ) -> BlockCell:
        """Create a new block cell at position (row, col).

        Content is a block reference inserted by an INSERT entity,
        attributes will be added if the block definition contains ATTDEF. Assignments
        are defined by attribs-key to attdef-tag association.

        Example: attribs = {'num': 1} if an ATTDEF with tag=='num' in
        the block definition exists, an attrib with text=str(1) will be
        created and added to the insert entity.

        The cell spans over 'span' cells and has the cell style with the
        name 'style'.
        """
        if attribs is None:
            attribs = {}
        cell = BlockCell(
            self, blockdef, style=style, attribs=attribs, span=span
        )
        return self.set_cell(row, col, cell)

    def set_cell(self, row: int, col: int, cell: T) -> T:
        """
        Insert a cell at position (row, col).
        """
        row, col = self.validate_index(row, col)
        self._cells[row, col] = cell
        return cell

    def get_cell(self, row: int, col: int) -> Cell:
        """Get cell at location (row, col)."""
        row, col = self.validate_index(row, col)
        try:
            return self._cells[row, col]
        except KeyError:
            return self.empty_cell  # empty cell with default style

    def validate_index(self, row: int, col: int) -> tuple[int, int]:
        row = int(row)
        col = int(col)
        if row < 0 or row >= self.nrows or col < 0 or col >= self.ncols:
            raise IndexError("cell index out of range")
        return row, col

    def frame(self, row, col, width=1, height=1, style="default") -> Frame:
        """Create a Frame object which frames the cell area starting at(row, col)
        covering `width` columns and `height` rows.

        """
        frame = Frame(self, pos=(row, col), span=(height, width), style=style)
        self.frames.append(frame)
        return frame

    def new_cell_style(self, name: str, **kwargs) -> CellStyle:
        """Create a new Style object `name`, overwrites exiting styles.

        Args:
            name: style name as string
            kwargs: see Style.get_default_cell_style()

        """
        assert (
            isinstance(name, str) and name != ""
        ), "name has to be a non-empty string"
        style: CellStyle = deepcopy(self.get_cell_style("default"))
        style.update(kwargs)
        if "align" in kwargs:
            align = kwargs.get("align", "LEFT")
            halign, valign = MAP_STRING_ALIGN_TO_FLAGS.get(align, (0, 0))
            style.halign = halign
            style.valign = valign
        else:
            halign = kwargs.get("halign", 0)
            valign = kwargs.get("valign", 0)
            style.align = MAP_FLAGS_TO_STRING_ALIGN[halign, valign]  # type: ignore

        self.styles[name] = style
        return style

    @staticmethod
    def new_border_style(
        color: int = const.BYLAYER,
        status=True,
        priority: int = 100,
        linetype: str = "BYLAYER",
    ) -> BorderStyle:
        """Create a new border style.

        Args:
            status: ``True`` for visible, ``False`` for invisible
            color: :ref:`ACI`
            linetype: linetype name, default is "BYLAYER"
            priority: drawing priority, higher priorities cover lower priorities

        """
        border_style = BorderStyle()
        border_style.color = color
        border_style.linetype = linetype
        border_style.status = status
        border_style.priority = priority
        return border_style

    def get_cell_style(self, name: str) -> CellStyle:
        """
        Get cell style by name.
        """
        return self.styles[name]

    def iter_visible_cells(
        self, visibility_map: VisibilityMap
    ) -> Iterator[tuple[int, int, Cell]]:
        """
        Iterate over all visible cells.

        Returns: a generator which yields all visible cells as tuples: (row , col, cell)
        """
        return (
            (row, col, self.get_cell(row, col)) for row, col in visibility_map
        )

    def render(self, layout: GenericLayoutType, insert: Optional[UVec] = None):
        """
        Render table to layout object.
        """
        _insert = self.insert  # backup value
        if insert is not None:
            self.insert = Vec2(insert)
        visibility_map = VisibilityMap(self)
        grid = Grid(self)
        grid.render_lines(layout, visibility_map)
        for row, col, cell in self.iter_visible_cells(visibility_map):
            grid.render_cell_background(layout, row, col, cell)
            grid.render_cell_content(layout, row, col, cell)

        self.insert = _insert  # restore value


class VisibilityMap:
    """Stores the visibility of the table cells."""

    def __init__(self, table: Table):
        """
        Create the visibility map for table.
        """
        self.table: Table = table
        self._hidden_cells: set[tuple[int, int]] = set()
        self._create_visibility_map()

    def _create_visibility_map(self):
        """
        Set visibility for all existing cells.
        """
        for row, col in iter(self):
            cell = self.table.get_cell(row, col)
            self._set_span_visibility(row, col, cell.span)

    def _set_span_visibility(self, row: int, col: int, span: tuple[int, int]):
        """
        Set the visibility of the given cell.

        The cell itself is visible, all other cells in the span-range
        (tuple: width, height) are invisible, they are covered by the
        main cell (row, col).
        """

        if span != (1, 1):
            nrows, ncols = span
            for rowx in range(nrows):
                for colx in range(ncols):
                    # switch all cells in span range to invisible
                    self.hide(row + rowx, col + colx)
        # switch content cell visible
        self.show(row, col)

    def show(self, row: int, col: int):
        """
        Show cell (row, col).
        """
        try:
            self._hidden_cells.remove((row, col))
        except KeyError:
            pass

    def hide(self, row: int, col: int) -> None:
        """
        Hide cell (row, col).
        """
        self._hidden_cells.add((row, col))

    def iter_all_cells(self) -> Iterator[tuple[int, int]]:
        """
        Iterate over all cell indices, yields (row, col) tuples.
        """
        for row in range(self.table.nrows):
            for col in range(self.table.ncols):
                yield row, col

    def is_visible_cell(self, row: int, col: int) -> bool:
        """
        True if cell (row, col)  is visible, else False.
        """
        return (row, col) not in self._hidden_cells

    def __iter__(self) -> Iterator[tuple[int, int]]:
        """
        Iterate over all visible cells.
        """
        return (
            (row, col)
            for (row, col) in self.iter_all_cells()
            if self.is_visible_cell(row, col)
        )


class CellStyle:
    """Cell style object."""

    def __init__(self, data: Optional[dict[str, Any]] = None):
        # textstyle is ignored by block cells
        self.textstyle = "STANDARD"
        # text height in drawing units, ignored by block cells
        self.textheight = DEFAULT_CELL_TEXT_HEIGHT
        # line spacing in percent = <textheight>*<linespacing>, ignored by block cells
        self.linespacing = DEFAULT_CELL_LINESPACING
        # text stretch or block reference x-axis scaling factor
        self.xscale = DEFAULT_CELL_XSCALE
        # block reference y-axis scaling factor, ignored by text cells
        self.yscale = DEFAULT_CELL_YSCALE
        # dxf color index, ignored by block cells
        self.textcolor = DEFAULT_CELL_TEXTCOLOR
        # text or block rotation in degrees
        self.rotation = 0.0
        # Letters are stacked top-to-bottom, but not rotated
        self.stacked = False
        # simple combined align parameter, like 'TOP_CENTER', see also MText.VALID_ALIGN
        self.align = "TOP_CENTER"  # higher priority than 'haling' and 'valign'
        # horizontal alignment (const.LEFT, const.CENTER, const.RIGHT)
        self.halign = const.CENTER
        # vertical alignment (const.TOP, const.MIDDLE, const.BOTTOM)
        self.valign = const.TOP
        # left and right margin in drawing units
        self.hmargin = DEFAULT_CELL_HMARGIN
        # top and bottom margin
        self.vmargin = DEFAULT_CELL_VMARGIN
        # background color, dxf color index, ignored by block cells
        self.bgcolor = DEFAULT_CELL_BG_COLOR
        # left border style
        self.left = BorderStyle()
        # top border style
        self.top = BorderStyle()
        # right border style
        self.right = BorderStyle()
        # bottom border style
        self.bottom = BorderStyle()
        if data:
            self.update(data)

    def __getitem__(self, k: str) -> Any:
        return self.__dict__[k]

    def __setitem__(self, k: str, v: Any):
        if k in self.__dict__:
            self.__dict__.__setitem__(k, v)
        else:
            raise KeyError(f"invalid attribute name: {k}")

    def update(self, data: dict[str, Any]):
        for k, v in data.items():
            self.__setitem__(k, v)

    def set_border_status(self, left=True, right=True, top=True, bottom=True):
        """Set status of all cell borders at once."""
        self.left.status = left
        self.right.status = right
        self.top.status = top
        self.bottom.status = bottom

    def set_border_style(
        self, style: BorderStyle, left=True, right=True, top=True, bottom=True
    ):
        """
        Set border styles of all cell borders at once.
        """
        for border, status in (
            ("left", left),
            ("right", right),
            ("top", top),
            ("bottom", bottom),
        ):
            if status:
                self[border] = style

    @staticmethod
    def get_default_border_style() -> BorderStyle:
        return BorderStyle()


class BorderStyle:
    def __init__(
        self,
        status: bool = DEFAULT_BORDER_STATUS,
        color: int = DEFAULT_BORDER_COLOR,
        linetype: str = DEFAULT_BORDER_LINETYPE,
        priority: int = DEFAULT_BORDER_PRIORITY,
    ):
        # border status, True for visible, False for hidden
        self.status = status
        # ACI
        self.color = color
        # linetype name, BYLAYER if None
        self.linetype = linetype
        # drawing priority, higher values cover lower values
        self.priority = priority


class Grid:
    """Grid contains the graphical representation of the table."""

    def __init__(self, table: Table):
        self.table: Table = table
        # contains the x-axis coords of the grid lines between the data columns.
        self.col_pos: list[float] = self._calc_col_pos()
        # contains the y-axis coords of the grid lines between the data rows.
        self.row_pos: list[float] = self._calc_row_pos()

        # contains the horizontal border elements, list of border styles
        # get index with _border_index(row, col), which means the border element
        # above row, col, and row-indices are [0 .. nrows+1], nrows+1 for the
        # grid line below the last row; list contains only the border style with
        # the highest priority.
        self._hborders: list[BorderStyle] = []  # created in _init_borders
        # same as _hborders but for the vertical borders,
        # col-indices are [0 .. ncols+1], ncols+1 for the last grid line right
        # of the last column
        self._vborders: list[BorderStyle] = []  # created in _init_borders
        # border style to delete borders inside of merged cells
        self.noborder = BorderStyle(
            status=False, priority=999, linetype="BYLAYER", color=0
        )

    def _init_borders(self, hborder: BorderStyle, vborder: BorderStyle):
        """
        Init the _hborders with  <hborder> and _vborders with <vborder>.
        """
        # <border_count> has more elements than necessary, but it unifies the
        # index calculation for _vborders and _hborders.
        # exact values are:
        # hborder_count = ncols * (nrows+1), hindex = ncols * <row> + <col>
        # vborder_count = nrows * (ncols+1), vindex = (ncols+1) * <row> + <col>
        border_count: int = (self.table.nrows + 1) * (self.table.ncols + 1)
        self._hborders = [hborder] * border_count
        self._vborders = [vborder] * border_count

    def _border_index(self, row: int, col: int) -> int:
        """
        Calculate linear index for border arrays _hborders and _vborders.
        """
        return row * (self.table.ncols + 1) + col

    def set_hborder(self, row: int, col: int, border_style: BorderStyle):
        """
        Set <border_style> for the horizontal border element above <row>, <col>.
        """
        return self._set_border_style(self._hborders, row, col, border_style)

    def set_vborder(self, row: int, col: int, border_style: BorderStyle):
        """
        Set <border_style> for the vertical border element left of <row>, <col>.
        """
        return self._set_border_style(self._vborders, row, col, border_style)

    def _set_border_style(
        self,
        borders: list[BorderStyle],
        row: int,
        col: int,
        border_style: BorderStyle,
    ):
        """
        Set <border_style> for <row>, <col> in <borders>.
        """
        border_index = self._border_index(row, col)
        actual_borderstyle = borders[border_index]
        if border_style.priority >= actual_borderstyle.priority:
            borders[border_index] = border_style

    def get_hborder(self, row: int, col: int) -> BorderStyle:
        """
        Get the horizontal border element above <row>, <col>.
        Last grid line (below <nrows>) is the element above of <nrows+1>.
        """
        return self._get_border(self._hborders, row, col)

    def get_vborder(self, row: int, col: int) -> BorderStyle:
        """
        Get the vertical border element left of <row>, <col>.
        Last grid line (right of <ncols>) is the element left of <ncols+1>.
        """
        return self._get_border(self._vborders, row, col)

    def _get_border(
        self, borders: list[BorderStyle], row: int, col: int
    ) -> BorderStyle:
        """
        Get border element at <row>, <col> from <borders>.
        """
        return borders[self._border_index(row, col)]

    def _calc_col_pos(self) -> list[float]:
        """Calculate the x-axis coords of the grid lines between the columns."""
        col_pos: list[float] = []
        start_x: float = self.table.insert.x
        sum_fields(start_x, self.table.col_widths, col_pos.append)
        return col_pos

    def _calc_row_pos(self) -> list[float]:
        """Calculate the y-axis coords of the grid lines between the rows."""
        row_pos: list[float] = []
        start_y: float = self.table.insert.y
        sum_fields(start_y, self.table.row_heights, row_pos.append, -1.0)
        return row_pos

    def cell_coords(
        self, row: int, col: int, span: tuple[int, int]
    ) -> tuple[float, float, float, float]:
        """Get the coordinates of the cell <row>,<col> as absolute drawing units.

        :return: a tuple (left, right, top, bottom)
        """
        top = self.row_pos[row]
        bottom = self.row_pos[row + span[0]]
        left = self.col_pos[col]
        right = self.col_pos[col + span[1]]
        return left, right, top, bottom

    def render_cell_background(
        self, layout: GenericLayoutType, row: int, col: int, cell: Cell
    ):
        """
        Render the cell background for <row>, <col> as SOLID entity.
        """
        style = cell.style
        if style["bgcolor"] is None:
            return
        # get cell coords in absolute drawing units
        left, right, top, bottom = self.cell_coords(row, col, cell.span)
        ltop = (left, top)
        lbot = (left, bottom)
        rtop = (right, top)
        rbot = (right, bottom)
        layout.add_solid(
            points=(ltop, lbot, rtop, rbot),
            dxfattribs={
                "color": style["bgcolor"],
                "layer": self.table.bglayer,
            },
        )

    def render_cell_content(
        self, layout: GenericLayoutType, row: int, col: int, cell: Cell
    ):
        """
        Render the cell content for <row>,<col> into layout object.
        """
        # get cell coords in absolute drawing units
        coords = self.cell_coords(row, col, cell.span)
        cell.render(layout, coords, self.table.fglayer)

    def render_lines(self, layout: GenericLayoutType, vm: VisibilityMap):
        """
        Render all grid lines into layout object.
        """
        # Init borders with default_style top- and left border.
        default_style = self.table.get_cell_style("default")
        hborder = default_style.top
        vborder = default_style.left
        self._init_borders(hborder, vborder)
        self._set_frames(self.table.frames)
        self._set_borders(self.table.iter_visible_cells(vm))
        self._render_borders(layout, self.table)

    def _set_borders(self, visible_cells: Iterable[tuple[int, int, Cell]]):
        """
        Set borders of the visible cells.
        """
        for row, col, cell in visible_cells:
            bottom_row = row + cell.span[0]
            right_col = col + cell.span[1]
            self._set_rect_borders(row, bottom_row, col, right_col, cell.style)
            self._set_inner_borders(
                row, bottom_row, col, right_col, self.noborder
            )

    def _set_inner_borders(
        self,
        top_row: int,
        bottom_row: int,
        left_col: int,
        right_col: int,
        border_style: BorderStyle,
    ):
        """
        Set <border_style> to the inner borders of the rectangle <top_row...
        """
        if bottom_row - top_row > 1:
            for col in range(left_col, right_col):
                for row in range(top_row + 1, bottom_row):
                    self.set_hborder(row, col, border_style)
        if right_col - left_col > 1:
            for row in range(top_row, bottom_row):
                for col in range(left_col + 1, right_col):
                    self.set_vborder(row, col, border_style)

    def _set_rect_borders(
        self,
        top_row: int,
        bottom_row: int,
        left_col: int,
        right_col: int,
        style: CellStyle,
    ):
        """
        Set border <style> to the rectangle <top_row><bottom_row...

        The values describing the grid lines between the cells, see doc-strings for set_hborder and set_vborder and see
        comments for self._hborders and self._vborders.
        """
        for col in range(left_col, right_col):
            self.set_hborder(top_row, col, style["top"])
            self.set_hborder(bottom_row, col, style["bottom"])
        for row in range(top_row, bottom_row):
            self.set_vborder(row, left_col, style["left"])
            self.set_vborder(row, right_col, style["right"])

    def _set_frames(self, frames: Iterable[Frame]):
        """
        Set borders for all defined frames.
        """
        for frame in frames:
            top_row = frame.pos[0]
            left_col = frame.pos[1]
            bottom_row = top_row + frame.span[0]
            right_col = left_col + frame.span[1]
            self._set_rect_borders(
                top_row, bottom_row, left_col, right_col, frame.style
            )

    def _render_borders(self, layout: GenericLayoutType, table: Table):
        """Render the grid lines as LINE entities into layout object."""

        def render_line(start: Vec2, end: Vec2, style: BorderStyle):
            """
            Render the LINE entity into layout object.
            """
            if style.status:
                layout.add_line(
                    start=start,
                    end=end,
                    dxfattribs={
                        "layer": layer,
                        "color": style.color,
                        "linetype": style.linetype,
                    },
                )

        def render_hborders():
            """Draw the horizontal grid lines."""
            for row in range(table.nrows + 1):
                yrow = self.row_pos[row]
                for col in range(table.ncols):
                    xleft = self.col_pos[col]
                    xright = self.col_pos[col + 1]
                    style = self.get_hborder(row, col)
                    render_line(Vec2(xleft, yrow), Vec2(xright, yrow), style)

        def render_vborders():
            """Draw the vertical grid lines."""
            for col in range(table.ncols + 1):
                xcol = self.col_pos[col]
                for row in range(table.nrows):
                    ytop = self.row_pos[row]
                    ybottom = self.row_pos[row + 1]
                    style = self.get_vborder(row, col)
                    render_line(Vec2(xcol, ytop), Vec2(xcol, ybottom), style)

        layer = table.gridlayer
        render_hborders()
        render_vborders()


class Frame:
    """Represent a rectangle cell area enclosed by borderlines."""

    def __init__(
        self,
        table: Table,
        pos: tuple[int, int] = (0, 0),
        span: tuple[int, int] = (1, 1),
        style="default",
    ):
        """Constructor

        Args:
            table: the assigned data table
            pos: tuple (row, col), border goes left and top of pos
            span: count of cells that Frame covers, border goes right and below of this cells
            style: style name as string
        """
        self.table = table
        self.pos = pos
        self.span = span
        self.stylename = style

    @property
    def style(self) -> CellStyle:
        return self.table.get_cell_style(self.stylename)


class Cell:
    """
    Cell represents the table cell data.
    """

    def __init__(
        self, table: Table, style="default", span: tuple[int, int] = (1, 1)
    ):
        """Constructor

        Args:
            table: assigned data table
            style: style name as string
            span: tuple(spanrows, spancols), count of cells that cell covers

        Cell does not know its own position in the data table, because a cell can be used multiple times in the same or
        in different tables. Therefore the cell itself can not determine if the cell-range reaches beyond the table
        borders.
        """
        self.table = table
        self.stylename = style
        # span values has to be >= 1
        self.span = span

    @property
    def span(self) -> tuple[int, int]:
        return self._span

    @span.setter
    def span(self, value: tuple[int, int]):
        """
        Ensures that span values are >= 1 in each direction.
        """
        self._span = (max(1, value[0]), max(1, value[1]))

    @property
    def style(self) -> CellStyle:
        """
        Returns: Style() object of the associated table.
        """
        return self.table.get_cell_style(self.stylename)

    def render(
        self, layout: GenericLayoutType, coords: Sequence[float], layer: str
    ):
        pass

    def get_workspace_coords(self, coords: Sequence[float]) -> Sequence[float]:
        """
        Reduces the cell-coords about the hmargin and the vmargin values.
        """
        hmargin = self.style["hmargin"]
        vmargin = self.style["vmargin"]
        return (
            coords[0] + hmargin,  # left
            coords[1] - hmargin,  # right
            coords[2] - vmargin,  # top
            coords[3] + vmargin,
        )  # bottom


CustomCell = Cell


class TextCell(Cell):
    """Represents a multi line text. Text lines are separated by '\n'.

    Args:
        table: assigned data table
        text: multi line text, lines separated by '\n'
        style: cell style name as string
        span: tuple(rows, cols) area of cells to cover

    """

    def __init__(
        self,
        table: Table,
        text: str,
        style="default",
        span: tuple[int, int] = (1, 1),
    ):
        super(TextCell, self).__init__(table, style, span)
        self.text = text

    def render(
        self, layout: GenericLayoutType, coords: Sequence[float], layer: str
    ):
        """Text cell.

        Args:
            layout: target layout
            coords: tuple of border-coordinates: left, right, top, bottom
            layer: target layer name as string

        """
        if not len(self.text):
            return

        left, right, top, bottom = self.get_workspace_coords(coords)
        style = self.style
        halign = style.halign
        valign = style.valign
        rotated = self.style.rotation
        text = self.text
        if style.stacked:
            rotated = 0.0
            text = "\n".join((char for char in self.text.replace("\n", " ")))
        xpos = (left, float(left + right) / 2.0, right)[halign]
        ypos = (bottom, float(bottom + top) / 2.0, top)[valign - 1]
        mtext = MText(  # using dxfwrite MText() composite, because it works
            text,
            (xpos, ypos),
            linespacing=self.style.linespacing,
            style=self.style.textstyle,
            height=self.style.textheight,
            rotation=rotated,
            xscale=self.style.xscale,
            halign=halign,
            valign=valign,
            color=self.style.textcolor,
            layer=layer,
        )
        mtext.render(layout)


class BlockCell(Cell):
    """Block reference cells.

    Args:
        table: table object
        blockdef: :class:`ezdxf.layouts.BlockLayout` instance
        attribs: BLOCK attributes as (tag, value) dictionary
        style: cell style name as string
        span: tuple(rows, cols) area of cells to cover

    """

    def __init__(
        self,
        table: Table,
        blockdef: BlockLayout,
        style="default",
        attribs=None,
        span: tuple[int, int] = (1, 1),
    ):
        if attribs is None:
            attribs = {}
        super(BlockCell, self).__init__(table, style, span)
        self.block_name = blockdef.name  # dxf block name!
        self.attribs = attribs

    def render(
        self, layout: GenericLayoutType, coords: Sequence[float], layer: str
    ):
        """Create the cell content as INSERT-entity with trailing ATTRIB-Entities.

        Args:
            layout: target layout
            coords: tuple of border-coordinates : left, right, top, bottom
            layer: target layer name as string

        """
        left, right, top, bottom = self.get_workspace_coords(coords)
        style = self.style
        halign = style.halign
        valign = style.valign
        xpos = (left, float(left + right) / 2.0, right)[halign]
        ypos = (bottom, float(bottom + top) / 2.0, top)[valign - 1]
        layout.add_auto_blockref(
            name=self.block_name,
            insert=(xpos, ypos),
            values=self.attribs,
            dxfattribs={
                "xscale": style.xscale,
                "yscale": style.yscale,
                "rotation": style.rotation,
                "layer": layer,
            },
        )


def sum_fields(
    start_value: float,
    fields: list[float],
    append: Callable[[float], None],
    sign: float = 1.0,
):
    """Adds step-by-step the fields-values, starting with <start_value>,
    and appends the resulting values to another object with the
    append-method.
    """
    position = start_value
    append(position)
    for element in fields:
        position += element * sign
        append(position)
