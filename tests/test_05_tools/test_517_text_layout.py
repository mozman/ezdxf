#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, List
import pytest
from itertools import permutations
import ezdxf.tools.text_layout as tl


@pytest.mark.parametrize(
    "margins,expected",
    [
        [None, (0, 0, 0, 0)],
        [(1,), (1, 1, 1, 1)],
        [(1, 2), (1, 2, 1, 2)],
        [(1, 2, 3), (1, 2, 3, 2)],
        [(1, 2, 3, 4), (1, 2, 3, 4)],
    ],
)
def test_resolve_margins(margins, expected):
    assert tl.resolve_margins(margins) == expected


@pytest.mark.parametrize(
    "align,expected",
    [
        [tl.LayoutAlignment.TOP_LEFT, (0, 0)],
        [tl.LayoutAlignment.TOP_CENTER, (-2, 0)],
        [tl.LayoutAlignment.TOP_RIGHT, (-4, 0)],
        [tl.LayoutAlignment.MIDDLE_LEFT, (0, 3)],
        [tl.LayoutAlignment.MIDDLE_CENTER, (-2, 3)],
        [tl.LayoutAlignment.MIDDLE_RIGHT, (-4, 3)],
        [tl.LayoutAlignment.BOTTOM_LEFT, (0, 6)],
        [tl.LayoutAlignment.BOTTOM_CENTER, (-2, 6)],
        [tl.LayoutAlignment.BOTTOM_RIGHT, (-4, 6)],
    ],
)
def test_insert_location(align, expected):
    assert tl.insert_location(align, width=4, height=6) == expected


class Rect(tl.ContentRenderer):
    def __init__(self, name: str, result: List = None):
        if result is None:
            result = []
        self.result = result  # store test results
        self.name = name

    def render(
        self, left: float, bottom: float, right: float, top: float, m=None
    ) -> None:
        self.result.append(
            f"{self.name}({left:.1f}, {bottom:.1f}, {right:.1f}, {top:.1f})"
        )

    def line(self, x1: float, y1: float, x2: float, y2: float, m=None) -> None:
        self.result.append(f"LINE({x1:.1f}, {y1:.1f})TO({x2:.1f}, {y2:.1f})")


class TestTopLevelLayout:
    @pytest.fixture
    def layout1(self):
        return tl.Layout(
            width=10, height=None, margins=(1, 1), renderer=Rect("Layout1")
        )

    def test_create_empty_layout_top_left(self, layout1):
        # layout1 has no height, only margins

        # 1. do layout placing
        layout1.place(align=tl.LayoutAlignment.TOP_LEFT)

        # 2. render content
        layout1.render()
        result = layout1.renderer.result
        assert len(result) == 1
        assert result[0] == "Layout1(0.0, -2.0, 12.0, 0.0)"

    def test_create_empty_layout_middle_center(self, layout1):
        # layout1 has no height, only margins

        # 1. do layout placing
        layout1.place(align=tl.LayoutAlignment.MIDDLE_CENTER)

        # 2. render content
        layout1.render()
        result = layout1.renderer.result
        assert len(result) == 1
        assert result[0] == "Layout1(-6.0, -1.0, 6.0, 1.0)"

    def test_add_one_column_by_reference_width(self, layout1):
        height = 17
        width = layout1.content_width  # reference column width
        result = layout1.renderer.result  # use same result container
        layout1.append_column(height=height, renderer=Rect("Col1", result))

        assert layout1.total_width == width + 2
        assert layout1.total_height == height + 2

        layout1.place(align=tl.LayoutAlignment.BOTTOM_LEFT)
        layout1.render()
        assert len(result) == 2
        assert result[0] == "Layout1(0.0, 0.0, 12.0, 19.0)"
        assert result[1] == "Col1(1.0, 1.0, 11.0, 18.0)"

    def test_add_two_equal_columns(self, layout1):
        margins = (1,)
        layout1.append_column(
            width=5, height=10, gutter=2, margins=margins, renderer=Rect("Col1")
        )
        layout1.append_column(
            width=7, height=20, margins=margins, renderer=Rect("Col2")
        )
        # width1 + margins + gutter + width2 + margins
        assert layout1.content_width == (5 + 2 + 2 + 7 + 2)

        # max(height) + margins
        assert layout1.content_height == (20 + 2)

    def test_bounding_box_for_not_placed_layout(self, layout1):
        # applies default alignment top/left, margins = (1, 1)
        layout1.append_column(10, 10)
        bbox = layout1.bbox()
        assert bbox.extmin == (0, -12)  # left/bottom
        assert bbox.extmax == (12, 0)  # right/top

    def test_bounding_box_for_placed_layout(self, layout1):
        # margins = (1, 1)
        layout1.append_column(10, 10)
        layout1.place(0, 0, tl.LayoutAlignment.MIDDLE_CENTER)
        bbox = layout1.bbox()
        assert bbox.extmin == (-6, -6)  # left/bottom
        assert bbox.extmax == (6, 6)  # right/top

    def test_next_existing_column(self, layout1):
        layout1.append_column(height=10)
        layout1.append_column(height=10)
        assert len(layout1) == 2
        assert layout1.current_column_index == 0
        layout1.next_column()
        assert layout1.current_column_index == 1

    def test_next_column_creates_a_new_column(self, layout1):
        layout1.append_column(height=10)
        assert len(layout1) == 1
        assert layout1.current_column_index == 0
        layout1.next_column()
        assert layout1.current_column_index == 1
        assert len(layout1) == 2, "a new column should be created"


class TestColumn:
    @pytest.fixture
    def c1(self):
        return tl.Column(
            # margins = top, right, bottom, left - same order as for CSS
            width=5,
            height=7,
            margins=(1, 2, 3, 4),
            renderer=Rect("C1"),
        )

    def test_size_calculation(self, c1):
        c1.place(0, 0)
        assert c1.content_width == 5
        assert c1.content_height == 7
        assert c1.total_width == 2 + 5 + 4
        assert c1.total_height == 1 + 7 + 3

    def test_render(self, c1):
        c1.place(0, 0)
        c1.render()
        result = c1.renderer.result
        assert result[0] == "C1(0.0, -11.0, 11.0, 0.0)"


def test_paragraph_available_line_content_space():
    par = tl.Paragraph(width=12, indent=(0.7, 0.5, 0.9))
    assert par.line_width(first=True) == 12 - 0.7 - 0.9
    assert par.line_width(first=False) == 12 - 0.5 - 0.9


class TestParagraphWithUnrestrictedHeight:
    # default values:
    # column width = 10
    # content width = 3
    # space width = 0.5

    @pytest.fixture
    def par(self):
        # Paragraph alignment is not important for content distribution,
        # because the required space is independent from alignment (left,
        # right, center or justified).
        # This may change by implementing regular tabulator support.
        return tl.Paragraph(width=10, renderer=Rect("PAR"))

    def test_empty_paragraph_dimensions(self, par):
        assert par.content_height == 0
        assert par.content_width == 10

    def test_render_empty_paragraph(self, par):
        par.place(0, 0)
        par.render()
        result = par.renderer.result

        assert len(result) == 1
        assert result[0] == "PAR(0.0, 0.0, 10.0, 0.0)"

    def test_distribute_invalid_content(self, par):
        par.append_content(str2cells("ttt"))
        with pytest.raises(ValueError):
            par.distribute_content(height=None)

    def test_distribute_common_case_without_nbsp(self, par):
        # column width = 10
        # content width = 3
        # space width = 0.5
        par.append_content(str2cells("t t t t t t t t t"))
        par.distribute_content(height=None)
        assert lines2str(par) == [
            "t t t",  # width = 3x3 + 2x0.5 = 10
            "t t t",  # remove line breaking spaces!
            "t t t",
        ]

    def test_distribute_with_nbsp(self, par):
        # column width = 10
        # content width = 3
        # space width = 0.5
        par.append_content(str2cells("t t t~t t t"))
        par.distribute_content(height=None)
        assert lines2str(par) == [
            "t t",  # t~t does not fit and goes to next line
            "t~t t",  # width = 3x3 + 2x0.5 = 10
            "t",
        ]

    def test_distribute_too_long_lines(self, par):
        # column width = 10
        par.append_content(str2cells("t t t", content=12))
        par.distribute_content(height=None)
        assert lines2str(par) == ["t", "t", "t"]

    def test_distribute_too_long_lines_including_nbsp(self, par):
        # column width = 10
        par.append_content(str2cells("t~t~t t~t t", content=5))
        par.distribute_content(height=None)
        assert lines2str(par) == [
            "t~t~t",  # width = 3x5 + 2x0.5 = 17
            "t~t",  # width = 2x5 + 0.5 = 10.5
            "t",
        ]


class TestParagraphWithRestrictedHeight:
    # default values:
    # column width = 10
    # content width = 3
    # space width = 0.5
    # cap height = 1,
    # line spacing 3-on-5 by 100% = 1.667
    THREE_LINE_SPACE = tl.leading(1, 1) * 2 + 1

    @pytest.fixture
    def par(self):
        # Paragraph alignment is not important for content distribution.
        return tl.Paragraph(width=10, renderer=Rect("PAR"))

    def test_distribute_with_exact_height_match(self, par):
        par.append_content(str2cells("t t t t t t t t t"))
        par.distribute_content(height=self.THREE_LINE_SPACE)
        assert lines2str(par) == [
            "t t t",  # width = 3x3 + 2x0.5 = 10
            "t t t",
            "t t t",
        ]

    def test_distribute_with_one_line_left_over(self, par):
        par.append_content(str2cells("t t t t t t t t t"))
        # Paragraph has only space for 2 lines by reducing the available space
        # by a small amount:
        height = self.THREE_LINE_SPACE - 0.01
        leftover = par.distribute_content(height=height)
        assert lines2str(par) == [
            "t t t",
            "t t t",
        ]
        leftover.distribute_content(height=1)
        assert lines2str(leftover) == ["t t t"]

    def test_distribute_with_all_lines_left_over(self, par):
        par.append_content(str2cells("t t t~t t t t t t"))
        # Paragraph has no space at all:
        leftover = par.distribute_content(height=0)
        assert lines2str(par) == []

        # None = unrestricted height
        leftover.distribute_content(height=None)
        assert lines2str(leftover) == [
            "t t",
            "t~t t",
            "t t t",
            "t",
        ]


def set_paragraph_content(flow):
    flow.append_content(str2cells("t t t t t t t t t"))
    flow.distribute_content()


class TestParagraphLeftAlignment:
    # default values:
    # content width = 3
    # space width = 0.5

    def test_without_indentation(self):
        par = tl.Paragraph(width=12, align=tl.ParagraphAlignment.LEFT)
        set_paragraph_content(par)
        par.place(0, 0)
        for line in par:
            assert line.total_width == 10
            assert line.final_location()[0] == 0

    def test_left_indentation(self):
        par = tl.Paragraph(
            width=12, indent=(0.7, 0.5, 0), align=tl.ParagraphAlignment.LEFT
        )
        set_paragraph_content(par)
        par.place(0, 0)
        lines = list(par)
        # first line:
        assert par.line_width(True) == 12 - 0.7  # available content space
        assert lines[0].final_location()[0] == 0.7
        assert lines[0].total_width == 10
        # remaining lines:
        for line in lines[1:]:
            assert par.line_width(False) == 12 - 0.5  # available content space
            assert line.total_width == 10
            assert line.final_location()[0] == 0.5

    def test_move_tab_to_next_line_if_following_content_does_not_fit(self):
        result = []
        par = tl.Paragraph(width=10, tab_stops=[tl.TabStop(4)])
        par.append_content(str2cells("t#t", content=6, result=result))
        # The tab (#) should move the following text to the tab stop
        # in the next line at position 4.
        par.distribute_content()
        par.place(0, 0)
        par.render()
        assert result[0] == "Text(0.0, -1.0, 6.0, 0.0)"
        assert result[1] == "Text(4.0, -2.7, 10.0, -1.7)", "x1 has to be 4.0"


class TestParagraphAlignment:
    # default values:
    # content width = 3
    # space width = 0.5

    def test_without_indentation(self):
        par = tl.Paragraph(width=12, align=tl.ParagraphAlignment.RIGHT)
        set_paragraph_content(par)
        par.place(0, 0)
        for line in par:
            assert line.total_width == 10
            assert line.final_location()[0] == 2

    def test_right_indentation(self):
        par = tl.Paragraph(
            width=12, indent=(0.5, 0.5, 0.5), align=tl.ParagraphAlignment.RIGHT
        )
        set_paragraph_content(par)
        par.place(0, 0)
        for line in par:
            assert line.total_width == 10
            assert line.final_location()[0] == 1.5  # 12 - 0.5 - 10


class TestParagraphCenterAlignment:
    # default values:
    # content width = 3
    # space width = 0.5

    def test_without_indentation(self):
        par = tl.Paragraph(width=12, align=tl.ParagraphAlignment.CENTER)
        set_paragraph_content(par)
        par.place(0, 0)
        for line in par:
            assert line.total_width == 10
            assert line.final_location()[0] == 1

    def test_left_indentation(self):
        par = tl.Paragraph(
            width=12, indent=(0.5, 0.5, 0), align=tl.ParagraphAlignment.CENTER
        )
        set_paragraph_content(par)
        par.place(0, 0)
        for line in par:
            assert line.total_width == 10
            assert line.final_location()[0] == 1.25  # 0.5 + (11.5 - 10) / 2

    def test_right_indentation(self):
        par = tl.Paragraph(
            width=12, indent=(0, 0, 0.5), align=tl.ParagraphAlignment.CENTER
        )
        set_paragraph_content(par)
        par.place(0, 0)
        for line in par:
            assert line.total_width == 10
            assert line.final_location()[0] == 0.75  # (11.5 - 10) / 2


class TestParagraphJustifiedAlignment:
    # default values:
    # content width = 3
    # space width = 0.5

    def test_without_indentation(self):
        par = tl.Paragraph(width=12, align=tl.ParagraphAlignment.JUSTIFIED)
        set_paragraph_content(par)
        par.place(0, 0)
        lines = list(par)
        for line in lines[:-1]:
            assert line.total_width == 12  # expand across paragraph width
            assert line.final_location()[0] == 0

        # last line is not expanded
        last_line = lines[-1]
        assert last_line.total_width == 10
        assert last_line.final_location()[0] == 0

    def test_with_indentation(self):
        par = tl.Paragraph(
            width=12,
            indent=(0.7, 0.5, 0.5),
            align=tl.ParagraphAlignment.JUSTIFIED,
        )
        set_paragraph_content(par)
        par.place(0, 0)
        lines = list(par)
        # first line:
        assert lines[0].total_width == 10.8  # 12 - (0.7 + 0.5)
        assert lines[0].final_location()[0] == 0.7

        # remaining lines:
        for line in lines[1:-1]:
            assert line.total_width == 11  # 12 - (0.5 + 0.5)
            assert line.final_location()[0] == 0.5

        # last line is not expanded:
        assert lines[-1].total_width == 10
        assert lines[-1].final_location()[0] == 0.5


class TestVerticalCellAlignment:
    @staticmethod
    def build_line(align):
        line = tl.LeftLine(width=7)
        big0 = tl.Text(width=3, height=3)
        small = tl.Text(width=1, height=1, valign=align, renderer=Rect("CELL"))
        big1 = tl.Text(width=3, height=3)
        line.append(big0)
        line.append(small)
        line.append(big1)
        line.place(0, 0)
        return line

    def test_line_properties(self):
        line = self.build_line(tl.CellAlignment.BOTTOM)
        assert len(list(line)) == 3
        assert line.total_width == 7
        assert line.total_height == 3

    def test_bottom_alignment(self):
        line = self.build_line(tl.CellAlignment.BOTTOM)
        big0, small, big1 = line
        # final location is always the top/left corner of the cell:
        assert big0.final_location() == (0, 0)
        assert small.final_location() == (3, -2)
        assert big1.final_location() == (4, 0)

        small.render()
        result = small.renderer.result
        # left, bottom, right, top
        assert result[0] == "CELL(3.0, -3.0, 4.0, -2.0)"

    def test_center_alignment(self):
        line = self.build_line(tl.CellAlignment.CENTER)
        big0, small, big1 = line
        # final location is always the top/left corner of the cell:
        assert big0.final_location() == (0, 0)
        assert small.final_location() == (3, -1)
        assert big1.final_location() == (4, 0)

        small.render()
        result = small.renderer.result
        # left, bottom, right, top
        assert result[0] == "CELL(3.0, -2.0, 4.0, -1.0)"

    def test_top_alignment(self):
        line = self.build_line(tl.CellAlignment.TOP)
        big0, small, big1 = line
        # final location is always the top/left corner of the cell:
        assert big0.final_location() == (0, 0)
        assert small.final_location() == (3, 0)
        assert big1.final_location() == (4, 0)

        small.render()
        result = small.renderer.result
        # left, bottom, right, top
        assert result[0] == "CELL(3.0, -1.0, 4.0, 0.0)"

    def test_mixed_alignment(self):
        big0 = tl.Text(width=3, height=3)
        bottom = tl.Text(width=1, height=1, valign=tl.CellAlignment.BOTTOM)
        center = tl.Text(width=1, height=1, valign=tl.CellAlignment.CENTER)
        top = tl.Text(width=1, height=1, valign=tl.CellAlignment.TOP)
        big1 = tl.Text(width=3, height=3)
        line = tl.LeftLine(width=9)
        for cell in [big0, top, center, bottom, big1]:
            line.append(cell)
        line.place(0, 0)
        assert bottom.final_location() == (5, -2)
        assert center.final_location() == (4, -1)
        assert top.final_location() == (3, 0)


class StrokeRender(Rect):
    def line(self, x1: float, y1: float, x2: float, y2: float, m=None) -> None:
        length = x2 - x1
        if y1 < -1:
            location = "UNDERLINE"
        elif y1 > 0:
            location = "OVERLINE"
        else:
            location = "STRIKE_THROUGH"
        self.result.append(f"{self.name}({location}, {length:.1f})")


class TestTextStrokeRendering:
    @staticmethod
    def render_text(stroke, result):
        text = tl.Text(
            width=3,
            height=1,
            stroke=stroke,
            renderer=StrokeRender("STROKE", result),
        )
        text.place(0, 0)
        tl.render_text_strokes([text])

    @pytest.mark.parametrize(
        "stroke,expected",
        [
            (tl.Stroke.UNDERLINE, "STROKE(UNDERLINE, 3.0)"),
            (tl.Stroke.OVERLINE, "STROKE(OVERLINE, 3.0)"),
            (tl.Stroke.STRIKE_THROUGH, "STROKE(STRIKE_THROUGH, 3.0)"),
        ],
    )
    def test_simple_stroke(self, stroke, expected):
        result = []
        self.render_text(stroke, result)
        assert result[0] == expected


class TestTextContinueStroke:
    @staticmethod
    def make_text(stroke, result):
        text = tl.Text(
            width=3,
            height=1,
            stroke=stroke,
            renderer=StrokeRender("STROKE", result),
        )
        text.place(0, 0)
        return text

    def test_continue_stroke_across_one_space(self):
        result = []
        word = self.make_text(tl.Stroke.UNDERLINE + tl.Stroke.CONTINUE, result)
        space = tl.Space(width=0.5)
        tl.render_text_strokes([word, space, word])
        assert len(result) == 2
        assert result[0] == "STROKE(UNDERLINE, 3.5)", "space should be included"
        assert result[1] == "STROKE(UNDERLINE, 3.0)", "no following space"

    def test_continue_stroke_across_multiple_spaces(self):
        result = []
        word = self.make_text(tl.Stroke.UNDERLINE + tl.Stroke.CONTINUE, result)
        space = tl.Space(width=0.5)
        nbsp = tl.NonBreakingSpace(width=0.5)
        tl.render_text_strokes([word, space, nbsp, space, word])
        assert len(result) == 2
        assert (
            result[0] == "STROKE(UNDERLINE, 4.5)"
        ), "3 spaces should be included"
        assert result[1] == "STROKE(UNDERLINE, 3.0)", "no following spaces"

    def test_do_not_continue_stroke_automatically(self):
        result = []
        word = self.make_text(tl.Stroke.UNDERLINE, result)
        space = tl.Space(width=0.5)
        tl.render_text_strokes([word, space, word])
        assert len(result) == 2
        assert result[0] == "STROKE(UNDERLINE, 3.0)", "do not continue stroke"


class TestFractionCell:
    @staticmethod
    def fraction(stacking, x, y):
        result = []
        a = tl.Text(1, 1, renderer=Rect("A", result))
        b = tl.Text(1, 1, renderer=Rect("B", result))
        fr = tl.Fraction(a, b, stacking, renderer=Rect("Fraction", result))
        fr.place(x, y)
        fr.render()
        return result

    def test_a_over_b(self):
        # y = total height = (a.total_height + b.total_height) * HEIGHT_SCALE
        result = self.fraction(
            tl.Stacking.OVER, x=0, y=2 * tl.Fraction.HEIGHT_SCALE
        )
        assert len(result) == 2
        assert result[0] == "A(0.0, 1.4, 1.0, 2.4)"  # L, B, R, T
        assert result[1] == "B(0.0, 0.0, 1.0, 1.0)"  # L, B, R, T

    def test_a_over_line_b(self):
        # y = total height = (a.total_height + a.total_height) * HEIGHT_SCALE
        result = self.fraction(
            tl.Stacking.LINE, x=0, y=2 * tl.Fraction.HEIGHT_SCALE
        )
        assert len(result) == 3
        assert result[0] == "A(0.0, 1.4, 1.0, 2.4)"  # L, B, R, T
        assert result[1] == "B(0.0, 0.0, 1.0, 1.0)"  # L, B, R, T
        assert result[2] == "LINE(0.0, 1.2)TO(1.0, 1.2)"

    def test_a_slanted_b(self):
        # y = total height = (a.total_height + a.total_height)
        result = self.fraction(tl.Stacking.SLANTED, x=0, y=2)
        assert len(result) == 3
        assert result[0] == "A(0.0, 1.0, 1.0, 2.0)"  # L, B, R, T
        assert result[1] == "B(1.0, 0.0, 2.0, 1.0)"  # L, B, R, T
        assert result[2] == "LINE(0.0, 0.0)TO(2.0, 2.0)"


def str2cells(s: str, content=3, space=0.5, result=None):
    # t ... text cell
    # f ... fraction cell
    # space is space
    # ~ ... non breaking space (nbsp)
    # # ... tabulator
    if result is None:
        result = []
    for c in s.lower():
        if c == "t":
            yield tl.Text(
                width=content, height=1, renderer=Rect("Text", result=result)
            )
        elif c == "f":
            cell = tl.Text(content / 2, 1)
            yield tl.Fraction(
                top=cell,
                bottom=cell,
                stacking=tl.Stacking.SLANTED,
                renderer=Rect("Fraction", result=result),
            )
        elif c == " ":
            yield tl.Space(width=space)
        elif c == "~":
            yield tl.NonBreakingSpace(width=space)
        elif c == "#":
            yield tl.Tabulator(width=0)  # Tabulators do not need a width
        else:
            raise ValueError(f'unknown cell type "{c}"')


CELL2STR = {
    tl.Text: "t",
    tl.Fraction: "f",
    tl.Space: " ",
    tl.NonBreakingSpace: "~",
    tl.Tabulator: "#",
}


def cells2str(cells: Iterable[tl.Cell]) -> str:
    return "".join(CELL2STR[type(cell)] for cell in cells)


def lines2str(lines):
    return [cells2str(line) for line in lines]


def test_cell_converter():
    assert cells2str(str2cells("tf ~#")) == "tf ~#"
    with pytest.raises(ValueError):
        list(str2cells("x"))
    with pytest.raises(KeyError):
        cells2str([0])


class TestNormalizeCells:
    @pytest.mark.parametrize("content", ["tt", "tf", "ft", "ff"])
    def test_no_glue_between_content_raises_value_error(self, content):
        cells = str2cells(content)
        with pytest.raises(ValueError):
            list(tl.normalize_cells(cells))

    @pytest.mark.parametrize("content", ["t~f", "f~f", "f~t"])
    def test_ignore_non_breaking_space_between_text_and_fraction(self, content):
        cells = str2cells(content)
        result = tl.normalize_cells(cells)
        assert len(result) == 3

    def test_ignore_pending_non_breaking_space(self):
        cells = str2cells("t~t~")
        result = tl.normalize_cells(cells)
        assert len(result) == 3

    @pytest.mark.parametrize("content", ["t~t", "t~~t", "t~~~t"])
    def test_preserve_multiple_nbsp(self, content):
        cells = tl.normalize_cells(str2cells(content))
        assert cells2str(cells) == content

    @pytest.mark.parametrize(
        "content",
        [
            "t~ t",
            "t ~t",
            "t~~ t",
            "t ~~t",
            "~t",
            "~~t",
            "t#~t",
            "t~#t",
            "t~#~t",
        ],
    )
    def test_replace_useless_nbsp_by_spaces(self, content):
        cells = tl.normalize_cells(str2cells(content))
        assert cells2str(cells) == content.replace("~", " ")

    @pytest.mark.parametrize("content", ["t t", "t  t", "t   t"])
    def test_preserve_multiple_spaces(self, content):
        cells = tl.normalize_cells(str2cells(content))
        assert cells2str(cells) == content

    def test_remove_pending_glue(self):
        for glue in permutations([" ", "~", " ", "#"]):
            content = "t" + "".join(glue)
            cells = list(tl.normalize_cells(str2cells(content)))
            assert cells2str(cells) == "t"

    @pytest.mark.parametrize("content", [" t", "  t", "   t"])
    def test_preserve_prepending_space(self, content):
        cells = list(tl.normalize_cells(str2cells(content)))
        assert cells2str(cells) == content


class TestSpace:
    def test_shrink_space(self):
        space = tl.Space(1, min_width=0.1)
        space.resize(0.5)
        assert space.total_width == 0.5
        space.resize(0)
        assert space.total_width == 0.1

    def test_default_min_width(self):
        space = tl.Space(1)
        space.resize(0.5)
        assert space.total_width == 1.0

    def test_expand_restricted_space(self):
        space = tl.Space(1, max_width=2)
        space.resize(1.5)
        assert space.total_width == 1.5
        space.resize(3)
        assert space.total_width == 2

    def test_expand_unrestricted_space(self):
        space = tl.Space(1)
        space.resize(1.5)
        assert space.total_width == 1.5
        space.resize(30)
        assert space.total_width == 30

    def test_total_height_is_zero(self):
        assert tl.Space(1).total_height == 0

    def test_non_breaking_space_to_space(self):
        space = tl.NonBreakingSpace(1).to_space()
        assert type(space) == tl.Space

    def test_can_shrink(self):
        assert tl.Space(1).can_shrink is False
        assert tl.Space(1, min_width=0.5).can_shrink is True

    def test_can_grow(self):
        assert tl.Space(1).can_grow is True
        assert tl.Space(1, max_width=1.0).can_grow is False


class TestRigidConnection:
    def test_rigid_connection(self):
        cells = tl.normalize_cells(str2cells("t~t t t"))
        result = tl.group_non_breakable_cells(cells)
        assert isinstance(result[0], tl.RigidConnection)
        assert isinstance(result[1], tl.Space)
        assert isinstance(result[2], tl.Text)
        assert isinstance(result[3], tl.Space)
        assert isinstance(result[4], tl.Text)

    @pytest.mark.parametrize("content", ["t~t", "t~t~t"])
    def test_create_one_connection(self, content):
        cells = tl.normalize_cells(str2cells(content))
        result = tl.group_non_breakable_cells(cells)
        assert len(result) == 1

    @pytest.mark.parametrize("content", ["t~t t~t", "t~t~t t~t~t"])
    def test_create_two_connections(self, content):
        cells = tl.normalize_cells(str2cells(content))
        result = tl.group_non_breakable_cells(cells)
        assert len(result) == 3
        assert isinstance(result[1], tl.Space)

    def test_ignore_pending_non_breaking_space(self):
        cells = tl.normalize_cells(str2cells("t~t~"))
        result = tl.group_non_breakable_cells(cells)
        assert len(result) == 1


class TestLeftLine:
    def test_setup(self):
        line = tl.LeftLine(10)
        assert line.line_width == 10
        assert line.total_width == 0

    def test_line_height_is_defined_by_max_content_height(self):
        line = tl.LeftLine(10)
        line.append(tl.Text(1, 1))
        assert line.total_height == 1
        line.append(tl.Text(1, 2))
        assert line.total_height == 2
        line.append(tl.Text(1, 3))
        assert line.total_height == 3

    def test_line_total_width_is_defined_by_content(self):
        line = tl.LeftLine(10)
        line.append(tl.Text(1, 1))
        assert line.total_width == 1
        line.append(tl.Text(1, 1))
        assert line.total_width == 2
        line.append(tl.Text(1, 1))
        assert line.total_width == 3

    def test_fill_until_line_is_full(self):
        line = tl.LeftLine(10)
        assert line.append(tl.Text(5, 1)) == tl.AppendType.SUCCESS
        assert line.append(tl.Text(5, 1)) == tl.AppendType.SUCCESS
        assert line.append(tl.Text(5, 1)) == tl.AppendType.FAIL
        assert line.total_width <= line.line_width

    def test_left_tab(self):
        def append_left_tab(size):
            line.append(tl.Tabulator(width=0.5))
            line.append(tl.Text(size, 1, renderer=Rect("LTAB", result)))

        result = []
        line = tl.LeftLine(
            20,
            tab_stops=[
                tl.TabStop(6, tl.TabStopType.LEFT),
                tl.TabStop(12, tl.TabStopType.LEFT),
            ],
        )
        line.append(tl.Text(2, 1, renderer=Rect("TEXT", result)))
        append_left_tab(2)
        append_left_tab(2)
        line.append(tl.Space(0.5))
        line.append(tl.Text(2, 1, renderer=Rect("TEXT", result)))
        line.place(0, 0)
        line.render()
        assert result[0] == "TEXT(0.0, -1.0, 2.0, 0.0)"
        assert result[1] == "LTAB(6.0, -1.0, 8.0, 0.0)"
        assert result[2] == "LTAB(12.0, -1.0, 14.0, 0.0)"
        assert result[3] == "TEXT(14.5, -1.0, 16.5, 0.0)"

    def test_left_tab_without_tab_stops(self):
        result = []
        line = tl.LeftLine(20)
        line.append(tl.Text(2, 1, renderer=Rect("TEXT", result)))
        line.append(tl.Tabulator(width=0.5))
        line.append(tl.Text(2, 1, renderer=Rect("LTAB", result)))
        line.place(0, 0)
        line.render()
        assert result[0] == "TEXT(0.0, -1.0, 2.0, 0.0)"
        # replace tab by a space width= 0.5
        assert result[1] == "LTAB(2.5, -1.0, 4.5, 0.0)"

    def test_center_tab(self):
        def append_center_tab(size):
            line.append(tl.Tabulator(width=0.5))
            line.append(tl.Text(size, 1, renderer=Rect("CTAB", result)))

        result = []
        line = tl.LeftLine(
            20,
            tab_stops=[
                tl.TabStop(6, tl.TabStopType.CENTER),
                tl.TabStop(12, tl.TabStopType.CENTER),
            ],
        )
        line.append(tl.Text(2, 1, renderer=Rect("TEXT", result)))
        append_center_tab(2)
        append_center_tab(2)
        line.append(tl.Space(0.5))
        line.append(tl.Text(2, 1, renderer=Rect("TEXT", result)))
        line.place(0, 0)
        line.render()
        assert result[0] == "TEXT(0.0, -1.0, 2.0, 0.0)"
        assert result[1] == "CTAB(5.0, -1.0, 7.0, 0.0)"
        assert result[2] == "CTAB(11.0, -1.0, 13.0, 0.0)"
        assert result[3] == "TEXT(13.5, -1.0, 15.5, 0.0)"

    def test_right_tab(self):
        def append_right_tab(size):
            line.append(tl.Tabulator(width=0.5))
            line.append(tl.Text(size, 1, renderer=Rect("RTAB", result)))

        result = []
        line = tl.LeftLine(
            20,
            tab_stops=[
                tl.TabStop(6, tl.TabStopType.RIGHT),
                tl.TabStop(12, tl.TabStopType.RIGHT),
            ],
        )
        line.append(tl.Text(2, 1, renderer=Rect("TEXT", result)))
        append_right_tab(2)
        append_right_tab(2)
        line.append(tl.Space(0.5))
        line.append(tl.Text(2, 1, renderer=Rect("TEXT", result)))
        line.place(0, 0)
        line.render()
        assert result[0] == "TEXT(0.0, -1.0, 2.0, 0.0)"
        assert result[1] == "RTAB(4.0, -1.0, 6.0, 0.0)"
        assert result[2] == "RTAB(10.0, -1.0, 12.0, 0.0)"
        assert result[3] == "TEXT(12.5, -1.0, 14.5, 0.0)"


if __name__ == "__main__":
    pytest.main([__file__])
