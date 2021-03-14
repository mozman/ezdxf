#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable
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
    [1, (0, 0)], [2, (-2, 0)], [3, (-4, 0)],
    [4, (0, 3)], [5, (-2, 3)], [6, (-4, 3)],
    [7, (0, 6)], [8, (-2, 6)], [9, (-4, 6)],
])
def test_insert_location(align, expected):
    assert tl.insert_location(align, width=4, height=6) == expected


class Rect(tl.ContentRenderer):
    def __init__(self, name: str):
        self.name = name

    def render(self, left: float, bottom: float, right: float,
               top: float, m=None):
        return f"{self.name}({left:.1f}, {bottom:.1f}, {right:.1f}, {top:.1f})"

    def line(self, x1: float, y1: float, x2: float, y2: float, m=None):
        return f"LINE({x1:.1f}, {y1:.1f})TO({x2:.1f}, {y2:.1f})"


class TestTopLevelLayout:
    @pytest.fixture
    def layout1(self):
        return tl.Layout(width=10, height=None, margins=(1, 1),
                         render=Rect('Layout1'))

    def test_create_empty_layout_top_left(self, layout1):
        # layout1 has no height, only margins

        # 1. do layout placing
        layout1.place(align=1)

        # 2. render content
        result = list(layout1.render())
        assert len(result) == 1
        assert result[0] == "Layout1(0.0, -2.0, 12.0, 0.0)"

    def test_create_empty_layout_middle_center(self, layout1):
        # layout1 has no height, only margins

        # 1. do layout placing
        layout1.place(align=5)

        # 2. render content
        result = list(layout1.render())
        assert len(result) == 1
        assert result[0] == "Layout1(-6.0, -1.0, 6.0, 1.0)"

    def test_add_one_column_by_reference_width(self, layout1):
        height = 17
        width = layout1.content_width  # reference column width
        layout1.add_column(height=height, render=Rect('Col1'))

        assert layout1.total_width == width + 2
        assert layout1.total_height == height + 2

        layout1.place(align=7)  # left/bottom
        result = list(layout1.render())
        assert len(result) == 2
        assert result[0] == "Layout1(0.0, 0.0, 12.0, 19.0)"
        assert result[1] == "Col1(1.0, 1.0, 11.0, 18.0)"

    def test_add_two_equal_columns(self, layout1):
        margins = (1,)
        layout1.add_column(width=5, height=10, gutter=2,
                           margins=margins, render=Rect('Col1'))
        layout1.add_column(width=7, height=20, margins=margins,
                           render=Rect('Col2'))
        # width1 + margins + gutter + width2 + margins
        assert layout1.content_width == (5 + 2 + 2 + 7 + 2)

        # max(height) + margins
        assert layout1.content_height == (20 + 2)


class TestColumn:
    @pytest.fixture
    def c1(self):
        return tl.Column(
            width=5, height=7, margins=(1, 2, 3, 4), render=Rect('C1'))

    def test_size_calculation(self, c1):
        # margins = top, right, bottom, left
        c1.place(0, 0)
        assert c1.content_width == 5
        assert c1.content_height == 7
        assert c1.total_width == 2 + 5 + 4
        assert c1.total_height == 1 + 7 + 3

    def test_render(self, c1):
        c1.place(0, 0)
        assert list(c1.render())[0] == "C1(0.0, -11.0, 11.0, 0.0)"


class TestFlowText:
    @pytest.fixture
    def left(self):
        return tl.FlowText(width=10, align=1, render=Rect('LEFT'))

    def test_empty_paragraph_dimensions(self, left):
        assert left.content_height == 0
        assert left.content_width == 10

    def test_render_empty_paragraph(self, left):
        left.place(0, 0)
        result = list(left.render())
        assert len(result) == 1
        assert result[0] == "LEFT(0.0, 0.0, 10.0, 0.0)"

    def test_distribute_invalid_content(self, left):
        left.append_content(str2cells('ttt'))
        with pytest.raises(ValueError):
            left.distribute_content(height=None)

    def test_distribute_left_adjustment(self, left):
        left.append_content(str2cells('t t t t t t t t t'))
        left.distribute_content(height=None)
        lines = list(left)
        assert len(lines) == 3


def str2cells(s: str, content=3, space=0.5, min_space=0.2):
    # t ... text cell
    # f ... fraction cell
    # space is space
    # ~ ... non breaking space (nbsp)
    # ^ ... tab
    for c in s.lower():
        if c == 't':
            yield tl.Text(width=content, height=1, renderer=Rect('Text'))
        elif c == 'f':
            yield tl.Fraction(width=content, height=2,
                              renderer=Rect('Fraction'))
        elif c == ' ':
            yield tl.Space(width=space, min_width=min_space)
        elif c == '~':
            yield tl.NonBreakingSpace(width=space, min_width=min_space)
        elif c == '^':
            yield tl.Tab()
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
        elif t is tl.Tab:
            s.append('^')
        else:
            raise ValueError(f'unknown cell type {str(t)}')
    return "".join(s)


def test_cell_converter():
    assert cells2str(str2cells('tf ~^')) == 'tf ~^'
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

    @pytest.mark.parametrize('content', ['t~~t', 't~~~t', 't~ t', 't ~t'])
    def test_preserve_multiple_non_breaking_spaces(self, content):
        cells = tl.normalize_cells(str2cells(content))
        assert cells2str(cells) == content

    @pytest.mark.parametrize('content', ['t t', 't  t', 't   t'])
    def test_preserve_multiple_spaces(self, content):
        cells = tl.normalize_cells(str2cells(content))
        assert cells2str(cells) == content

    def test_remove_pending_glue(self):
        for glue in permutations([' ', '~', '^', ' ']):
            content = 't' + "".join(glue)
            cells = list(tl.normalize_cells(str2cells(content)))
            assert cells2str(cells) == 't'

    def test_preserve_prepending_glue(self):
        for glue in permutations([' ', '~', '^', ' ']):
            content = "".join(glue) + 't'
            cells = list(tl.normalize_cells(str2cells(content)))
            assert cells2str(cells) == content


if __name__ == '__main__':
    pytest.main([__file__])
