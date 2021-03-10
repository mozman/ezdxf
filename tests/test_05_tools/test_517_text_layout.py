#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest
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


if __name__ == '__main__':
    pytest.main([__file__])
