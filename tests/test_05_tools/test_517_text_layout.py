#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, List
import pytest
from itertools import permutations
import ezdxf.tools.text_layout as tl


@pytest.mark.parametrize('margins,expected', [
    [None, (0, 0, 0, 0)],
    [(1,), (1, 1, 1, 1)],
    [(1, 2), (1, 2, 1, 2)],
    [(1, 2, 3), (1, 2, 3, 2)],
    [(1, 2, 3, 4), (1, 2, 3, 4)]
])
def test_resolve_margins(margins, expected):
    assert tl.resolve_margins(margins) == expected


@pytest.mark.parametrize('align,expected', [
    [tl.LayoutAlignment.TOP_LEFT, (0, 0)],
    [tl.LayoutAlignment.TOP_CENTER, (-2, 0)],
    [tl.LayoutAlignment.TOP_RIGHT, (-4, 0)],
    [tl.LayoutAlignment.MIDDLE_LEFT, (0, 3)],
    [tl.LayoutAlignment.MIDDLE_CENTER, (-2, 3)],
    [tl.LayoutAlignment.MIDDLE_RIGHT, (-4, 3)],
    [tl.LayoutAlignment.BOTTOM_LEFT, (0, 6)],
    [tl.LayoutAlignment.BOTTOM_CENTER, (-2, 6)],
    [tl.LayoutAlignment.BOTTOM_RIGHT, (-4, 6)],
])
def test_insert_location(align, expected):
    assert tl.insert_location(align, width=4, height=6) == expected


class Rect(tl.ContentRenderer):
    def __init__(self, name: str, result: List = None):
        if result is None:
            result = []
        self.result = result  # store test results
        self.name = name

    def render(self, left: float, bottom: float, right: float,
               top: float, m=None) -> None:
        self.result.append(
            f"{self.name}({left:.1f}, {bottom:.1f}, {right:.1f}, {top:.1f})")

    def line(self, x1: float, y1: float, x2: float, y2: float, m=None) -> None:
        self.result.append(f"LINE({x1:.1f}, {y1:.1f})TO({x2:.1f}, {y2:.1f})")


class TestTopLevelLayout:
    @pytest.fixture
    def layout1(self):
        return tl.Layout(width=10, height=None, margins=(1, 1),
                         renderer=Rect('Layout1'))

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
        layout1.append_column(height=height, renderer=Rect('Col1', result))

        assert layout1.total_width == width + 2
        assert layout1.total_height == height + 2

        layout1.place(align=tl.LayoutAlignment.BOTTOM_LEFT)
        layout1.render()
        assert len(result) == 2
        assert result[0] == "Layout1(0.0, 0.0, 12.0, 19.0)"
        assert result[1] == "Col1(1.0, 1.0, 11.0, 18.0)"

    def test_add_two_equal_columns(self, layout1):
        margins = (1,)
        layout1.append_column(width=5, height=10, gutter=2,
                              margins=margins, renderer=Rect('Col1'))
        layout1.append_column(width=7, height=20, margins=margins,
                              renderer=Rect('Col2'))
        # width1 + margins + gutter + width2 + margins
        assert layout1.content_width == (5 + 2 + 2 + 7 + 2)

        # max(height) + margins
        assert layout1.content_height == (20 + 2)


class TestColumn:
    @pytest.fixture
    def c1(self):
        return tl.Column(
            # margins = top, right, bottom, left - same order as for CSS
            width=5, height=7, margins=(1, 2, 3, 4), renderer=Rect('C1'))

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


def test_flow_text_available_line_content_space():
    flow = tl.FlowText(width=12, indent=(0.7, 0.5, 0.9))
    assert flow.line_width(first=True) == 12 - 0.7 - 0.9
    assert flow.line_width(first=False) == 12 - 0.5 - 0.9


class TestFlowTextWithUnrestrictedHeight:
    # default values:
    # column width = 10
    # content width = 3
    # space width = 0.5

    @pytest.fixture
    def flow(self):
        # Paragraph alignment is not important for content distribution,
        # because the required space is independent from alignment (left,
        # right, center or justified).
        # This may change by implementing regular tabulator support.
        return tl.FlowText(width=10, renderer=Rect('PAR'))

    def test_empty_paragraph_dimensions(self, flow):
        assert flow.content_height == 0
        assert flow.content_width == 10

    def test_render_empty_paragraph(self, flow):
        flow.place(0, 0)
        flow.render()
        result = flow.renderer.result

        assert len(result) == 1
        assert result[0] == "PAR(0.0, 0.0, 10.0, 0.0)"

    def test_distribute_invalid_content(self, flow):
        flow.append_content(str2cells('ttt'))
        with pytest.raises(ValueError):
            flow.distribute_content(height=None)

    def test_distribute_common_case_without_nbsp(self, flow):
        # column width = 10
        # content width = 3
        # space width = 0.5
        flow.append_content(str2cells('t t t t t t t t t'))
        flow.distribute_content(height=None)
        assert lines2str(flow) == [
            't t t',  # width = 3x3 + 2x0.5 = 10
            't t t',  # remove line breaking spaces!
            't t t'
        ]

    def test_distribute_with_nbsp(self, flow):
        # column width = 10
        # content width = 3
        # space width = 0.5
        flow.append_content(str2cells('t t t~t t t'))
        flow.distribute_content(height=None)
        assert lines2str(flow) == [
            't t',  # t~t does not fit and goes to next line
            't~t t',  # width = 3x3 + 2x0.5 = 10
            't'
        ]

    def test_distribute_too_long_lines(self, flow):
        # column width = 10
        flow.append_content(str2cells('t t t', content=12))
        flow.distribute_content(height=None)
        assert lines2str(flow) == [
            't',
            't',
            't'
        ]

    def test_distribute_too_long_lines_including_nbsp(self, flow):
        # column width = 10
        flow.append_content(str2cells('t~t~t t~t t', content=5))
        flow.distribute_content(height=None)
        assert lines2str(flow) == [
            't~t~t',  # width = 3x5 + 2x0.5 = 17
            't~t',  # width = 2x5 + 0.5 = 10.5
            't'
        ]


class TestFlowTextWithRestrictedHeight:
    # default values:
    # column width = 10
    # content width = 3
    # space width = 0.5
    # cap height = 1,
    # line spacing 3-on-5 by 100% = 1.667
    THREE_LINE_SPACE = tl.leading(1, 1) * 2 + 1

    @pytest.fixture
    def flow(self):
        # Paragraph alignment is not important for content distribution.
        return tl.FlowText(width=10, renderer=Rect('PAR'))

    def test_distribute_with_exact_height_match(self, flow):
        flow.append_content(str2cells('t t t t t t t t t'))
        flow.distribute_content(height=self.THREE_LINE_SPACE)
        assert lines2str(flow) == [
            't t t',  # width = 3x3 + 2x0.5 = 10
            't t t',
            't t t'
        ]

    def test_distribute_with_one_line_left_over(self, flow):
        flow.append_content(str2cells('t t t t t t t t t'))
        # Paragraph has only space for 2 lines by reducing the available space
        # by a small amount:
        height = self.THREE_LINE_SPACE - 0.01
        leftover = flow.distribute_content(height=height)
        assert lines2str(flow) == [
            't t t',
            't t t',
        ]
        leftover.distribute_content(height=1)
        assert lines2str(leftover) == ['t t t']

    def test_distribute_with_all_lines_left_over(self, flow):
        flow.append_content(str2cells('t t t~t t t t t t'))
        # Paragraph has no space at all:
        leftover = flow.distribute_content(height=0)
        assert lines2str(flow) == []

        # None = unrestricted height
        leftover.distribute_content(height=None)
        assert lines2str(leftover) == [
            't t',
            't~t t',
            't t t',
            't',
        ]


def set_flow_content(flow):
    flow.append_content(str2cells('t t t t t t t t t'))
    flow.distribute_content()


class TestFlowTextLeftAlignment:
    # default values:
    # content width = 3
    # space width = 0.5

    def test_without_indentation(self):
        flow = tl.FlowText(width=12, align=tl.FlowTextAlignment.LEFT)
        set_flow_content(flow)
        flow.place(0, 0)
        for line in flow:
            assert line.total_width == 10
            assert line.final_location()[0] == 0

    def test_left_indentation(self):
        flow = tl.FlowText(width=12, indent=(0.7, 0.5, 0),
                           align=tl.FlowTextAlignment.LEFT)
        set_flow_content(flow)
        flow.place(0, 0)
        lines = list(flow)
        # first line:
        assert flow.line_width(True) == 12 - 0.7  # available content space
        assert lines[0].final_location()[0] == 0.7
        assert lines[0].total_width == 10
        # remaining lines:
        for line in lines[1:]:
            assert flow.line_width(False) == 12 - 0.5  # available content space
            assert line.total_width == 10
            assert line.final_location()[0] == 0.5


class TestFlowTextRightAlignment:
    # default values:
    # content width = 3
    # space width = 0.5

    def test_without_indentation(self):
        flow = tl.FlowText(width=12, align=tl.FlowTextAlignment.RIGHT)
        set_flow_content(flow)
        flow.place(0, 0)
        for line in flow:
            assert line.total_width == 10
            assert line.final_location()[0] == 2

    def test_right_indentation(self):
        flow = tl.FlowText(width=12, indent=(0.5, 0.5, 0.5),
                           align=tl.FlowTextAlignment.RIGHT)
        set_flow_content(flow)
        flow.place(0, 0)
        for line in flow:
            assert line.total_width == 10
            assert line.final_location()[0] == 1.5  # 12 - 0.5 - 10


class TestFlowTextCenterAlignment:
    # default values:
    # content width = 3
    # space width = 0.5

    def test_without_indentation(self):
        flow = tl.FlowText(width=12, align=tl.FlowTextAlignment.CENTER)
        set_flow_content(flow)
        flow.place(0, 0)
        for line in flow:
            assert line.total_width == 10
            assert line.final_location()[0] == 1

    def test_left_indentation(self):
        flow = tl.FlowText(width=12, indent=(0.5, 0.5, 0),
                           align=tl.FlowTextAlignment.CENTER)
        set_flow_content(flow)
        flow.place(0, 0)
        for line in flow:
            assert line.total_width == 10
            assert line.final_location()[0] == 1.25  # 0.5 + (11.5 - 10) / 2

    def test_right_indentation(self):
        flow = tl.FlowText(width=12, indent=(0, 0, 0.5),
                           align=tl.FlowTextAlignment.CENTER)
        set_flow_content(flow)
        flow.place(0, 0)
        for line in flow:
            assert line.total_width == 10
            assert line.final_location()[0] == 0.75  # (11.5 - 10) / 2


class TestFlowTextJustifiedAlignment:
    # default values:
    # content width = 3
    # space width = 0.5

    def test_without_indentation(self):
        flow = tl.FlowText(width=12, align=tl.FlowTextAlignment.JUSTIFIED)
        set_flow_content(flow)
        flow.place(0, 0)
        for line in flow:
            assert line.total_width == 12  # expand across paragraph width
            assert line.final_location()[0] == 0

    def test_with_indentation(self):
        flow = tl.FlowText(width=12, indent=(0.7, 0.5, 0.5),
                           align=tl.FlowTextAlignment.JUSTIFIED)
        set_flow_content(flow)
        flow.place(0, 0)
        lines = list(flow)
        # first line:
        assert lines[0].total_width == 10.8  # 12 - (0.7 + 0.5)
        assert lines[0].final_location()[0] == 0.7
        # remaining lines:
        for line in lines[1:]:
            assert line.total_width == 11  # 12 - (0.5 + 0.5)
            assert line.final_location()[0] == 0.5


class TestVerticalCellAlignment:
    @staticmethod
    def build_line(align):
        big0 = tl.Text(width=3, height=3)
        small = tl.Text(width=1, height=1, valign=align, renderer=Rect('CELL'))
        big1 = tl.Text(width=3, height=3)
        line = tl.HCellGroup([big0, small, big1])
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
        line = tl.HCellGroup([big0, top, center, bottom, big1])
        line.place(0, 0)
        # final location is always the top/left corner of the cell:
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
        text = tl.Text(width=3, height=1, stroke=stroke,
                       renderer=StrokeRender("STROKE", result))
        text.place(0, 0)
        tl.render_text_strokes([text])

    @pytest.mark.parametrize("stroke,expected",[
        (tl.Stroke.UNDERLINE, "STROKE(UNDERLINE, 3.0)"),
        (tl.Stroke.OVERLINE, "STROKE(OVERLINE, 3.0)"),
        (tl.Stroke.STRIKE_THROUGH, "STROKE(STRIKE_THROUGH, 3.0)"),
    ])
    def test_simple_stroke(self, stroke, expected):
        result = []
        self.render_text(stroke, result)
        assert result[0] == expected


class TestTextContinueStroke:
    @staticmethod
    def make_text(stroke, result):
        text = tl.Text(width=3, height=1, stroke=stroke,
                       renderer=StrokeRender("STROKE", result))
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
        assert result[0] == "STROKE(UNDERLINE, 4.5)", "3 spaces should be included"
        assert result[1] == "STROKE(UNDERLINE, 3.0)", "no following spaces"

    def test_do_not_continue_stroke_automatically(self):
        result = []
        word = self.make_text(tl.Stroke.UNDERLINE, result)
        space = tl.Space(width=0.5)
        tl.render_text_strokes([word, space, word])
        assert len(result) == 2
        assert result[0] == "STROKE(UNDERLINE, 3.0)", "do not continue stroke"


def str2cells(s: str, content=3, space=0.5):
    # t ... text cell
    # f ... fraction cell
    # space is space
    # ~ ... non breaking space (nbsp)
    for c in s.lower():
        if c == 't':
            yield tl.Text(width=content, height=1, renderer=Rect('Text'))
        elif c == 'f':
            yield tl.Fraction(width=content, height=2,
                              renderer=Rect('Fraction'))
        elif c == ' ':
            yield tl.Space(width=space)
        elif c == '~':
            yield tl.NonBreakingSpace(width=space)
        else:
            raise ValueError(f'unknown cell type "{c}"')


def cells2str(cells: Iterable[tl.Cell]) -> str:
    s = []
    for cell in cells:
        t = type(cell)
        if t is tl.Text:
            s.append('t')
        elif t is tl.Fraction:
            s.append('f')
        elif t is tl.Space:
            s.append(' ')
        elif t is tl.NonBreakingSpace:
            s.append('~')
        else:
            raise ValueError(f'unknown cell type {str(t)}')
    return "".join(s)


def lines2str(lines):
    return [cells2str(line) for line in lines]


def test_cell_converter():
    assert cells2str(str2cells('tf ~')) == 'tf ~'
    with pytest.raises(ValueError):
        list(str2cells('x'))
    with pytest.raises(ValueError):
        cells2str([0])


class TestNormalizeCells:
    @pytest.mark.parametrize('content', ['tt', 'tf', 'ft', 'ff'])
    def test_no_glue_between_content_raises_value_error(self, content):
        cells = str2cells(content)
        with pytest.raises(ValueError):
            list(tl.normalize_cells(cells))

    @pytest.mark.parametrize('content', ['t~t', 't~~t', 't~~~t'])
    def test_preserve_multiple_nbsp(self, content):
        cells = tl.normalize_cells(str2cells(content))
        assert cells2str(cells) == content

    @pytest.mark.parametrize(
        'content', ['t~ t', 't ~t', 't~~ t', 't ~~t', '~t', '~~t'])
    def test_replace_useless_nbsp_by_spaces(self, content):
        cells = tl.normalize_cells(str2cells(content))
        assert cells2str(cells) == content.replace('~', ' ')

    @pytest.mark.parametrize('content', ['t t', 't  t', 't   t'])
    def test_preserve_multiple_spaces(self, content):
        cells = tl.normalize_cells(str2cells(content))
        assert cells2str(cells) == content

    def test_remove_pending_glue(self):
        for glue in permutations([' ', '~', ' ']):
            content = 't' + "".join(glue)
            cells = list(tl.normalize_cells(str2cells(content)))
            assert cells2str(cells) == 't'

    @pytest.mark.parametrize('content', [' t', '  t', '   t'])
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


if __name__ == '__main__':
    pytest.main([__file__])
