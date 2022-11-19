# Created: 21.03.2010, adapted 2018 for ezdxf
# Copyright (C) 2010-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.document import Drawing
from ezdxf.addons.table import Table, CustomCell
from ezdxf.addons.table import Grid, CellStyle, DEFAULT_BORDER_COLOR


@pytest.fixture(scope="module")
def doc() -> Drawing:
    return ezdxf.new("R12")


class MockCell(CustomCell):
    counter = 0

    def render(self, layout, coords, layer):
        MockCell.counter += 1

    @staticmethod
    def reset():
        MockCell.counter = 0


def test_init():
    table = Table((0, 0), 10, 10, default_grid=False)
    assert bool(table) is True
    style = table.get_cell_style("default")
    for border in ["left", "right", "top", "bottom"]:
        assert style[border].status is False

    table = Table((0, 0), 10, 10, default_grid=True)
    style = table.get_cell_style("default")
    for border in ["left", "right", "top", "bottom"]:
        assert style[border].status is True


def test_setter_methods():
    table = Table((0, 0), 10, 10)
    table.set_col_width(0, 3.0)
    assert table.col_widths[0] == 3.0
    table.set_row_height(0, 4.0)
    assert table.row_heights[0] == 4.0


def test_cell_index():
    table = Table((0, 0), 10, 10)
    with pytest.raises(IndexError):
        table.get_cell(10, 10)
    with pytest.raises(IndexError):
        table.get_cell(-1, 10)


def test_default_text_cell():
    table = Table((0, 0), 10, 10)
    text_cell = table.text_cell(0, 0, "test")
    assert text_cell.text == "test"
    cell = table.get_cell(0, 0)
    assert cell.span == (1, 1)
    assert cell.stylename == "default"


def test_text_cell():
    table = Table((0, 0), 10, 10)
    text_cell = table.text_cell(8, 8, "test88", span=(2, 2), style="extrastyle")
    assert text_cell.text == "test88"
    cell = table.get_cell(8, 8)
    assert cell.span == (2, 2)
    assert cell.stylename == "extrastyle"


def test_block_cell(doc):
    block = doc.blocks.new("EMPTY_BLOCK")
    table = Table((0, 0), 10, 10)
    block_cell = table.block_cell(1, 1, block, span=(3, 3))
    assert block_cell.block_name == "EMPTY_BLOCK"

    cell = table.get_cell(1, 1)
    assert cell.span == (3, 3)
    assert cell.stylename == "default"


def test_frame():
    table = Table((0, 0), 10, 10)
    frame = table.frame(0, 0, width=10, height=2)
    assert frame.pos == (0, 0)
    assert frame.span == (2, 10)


def test_cell_style():
    table = Table((0, 0), 10, 10)
    table.new_cell_style("extra", textcolor=199)
    style = table.get_cell_style("extra")
    assert style.textcolor == 199
    with pytest.raises(KeyError):
        table.get_cell_style("extraextra")


def test_border_style():
    table = Table((0, 0), 10, 10)
    border_style = table.new_border_style(
        color=1, status=True, linetype="DOT", priority=99
    )
    assert border_style.color == 1
    assert border_style.status is True
    assert border_style.linetype == "DOT"
    assert border_style.priority == 99


def test_visibility_map():
    from ezdxf.addons.table import VisibilityMap

    table = Table((0, 0), 3, 3)
    text_cell = table.text_cell(0, 0, "text", span=(2, 2))
    vmap = VisibilityMap(table)
    empty = table.empty_cell
    expected = [
        (0, 0, text_cell),
        (0, 2, empty),  # cell (0, 1) is covered by (0,0)
        (1, 2, empty),  # cells (1, 0), (1, 2) are covered by cell (0, 0)
        (2, 0, empty),
        (2, 1, empty),
        (2, 2, empty),
    ]  # row 2
    for got, should in zip(table.iter_visible_cells(vmap), expected):
        assert got[0] == should[0]  # row
        assert got[1] == should[1]  # col
        assert got[2] == should[2]  # cell


def test_rendering(doc):
    MockCell.reset()
    layout = doc.blocks.new("test_rendering")
    table = Table((0, 0), 3, 3)
    indices = [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    ]
    cell = MockCell(table, "default", (1, 1))
    for row, col in indices:
        table.set_cell(row, col, cell)
    table.render(layout)
    assert cell.counter == 9  # count get_dxf_entity calls


def test_dxf_creation_span(doc):
    MockCell.reset()
    layout = doc.blocks.new("test_dxf_creation_span")
    table = Table((0, 0), 3, 3)
    indices = [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    ]
    cell = MockCell(table, "default", (1, 1))
    for row, col in indices:
        table.set_cell(row, col, cell)
    spancell = MockCell(table, "default", span=(2, 2))  # hides 3 cells
    table.set_cell(0, 0, spancell)
    table.render(layout)
    assert cell.counter == 6  # count get_dxf_entity calls


def test_span_beyond_table_borders(doc):
    layout = doc.blocks.new("test_span_beyond_table_borders")
    table = Table((0, 0), 3, 3)
    table.text_cell(0, 2, "ERROR", span=(1, 2))
    with pytest.raises(IndexError):
        table.render(layout)
    table.text_cell(2, 0, "ERROR", span=(2, 1))
    with pytest.raises(IndexError):
        table.render(layout)


@pytest.fixture
def table():
    table = Table((0, 0), 3, 3)
    for x in range(3):
        table.set_col_width(x, 3.0)
        table.set_row_height(x, 3.0)
    return table


def test_grid_coords(table):
    grid = Grid(table)
    left, right, top, bottom = grid.cell_coords(1, 1, span=(1, 1))
    assert left == 3.0  # , places=4)
    assert right == 6.0
    assert top == -3.0
    assert bottom == -6.0


def test_grid_coords_span(table):
    grid = Grid(table)
    left, right, top, bottom = grid.cell_coords(0, 0, span=(2, 2))
    assert left == 0.0
    assert right == 6.0
    assert top == 0.0
    assert bottom == -6.0


def test_draw_cell_background(doc, table):
    grid = Grid(table)
    layout = doc.blocks.new("test_draw_cell_background")
    table.new_cell_style("fill", bgcolor=17)
    cell = table.get_cell(0, 0)
    cell.stylename = "fill"
    grid.render_cell_background(layout, 0, 0, cell)
    solid = list(layout)[0]
    assert solid.dxftype() == "SOLID"


def test_set_border_status():
    style = CellStyle()
    style.set_border_status(False, True, False, True)
    assert style.left.status is False
    assert style.right.status is True
    assert style.top.status is False
    assert style.bottom.status is True


def test_set_border_style():
    style = CellStyle()
    border_style = CellStyle.get_default_border_style()
    border_style.color = 17

    style.set_border_style(border_style, False, True, False, True)
    assert style.left.color == DEFAULT_BORDER_COLOR
    assert style.right.color == 17
    assert style.top.color == DEFAULT_BORDER_COLOR
    assert style.bottom.color == 17


class TestStyle:
    def test_init_default_style(self):
        style = CellStyle()
        assert style.textstyle == "STANDARD"

    def test_init_custom_style(self):
        style = CellStyle({"textstyle": "Arial"})
        assert style.textstyle == "Arial"

    def test_get_attribute_index_operator(self):
        style = CellStyle()
        assert style["textstyle"] == style.textstyle

    def test_invalid_attribute_name_raises_key_error(self):
        style = CellStyle()
        with pytest.raises(KeyError):  # get
            _ = style["xxx"]

        with pytest.raises(KeyError):  # set
            style["xxx"] = "xxx"
