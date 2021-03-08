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


@pytest.fixture
def layout1():
    return tl.Layout(width=10, height=None, margins=(1, 1),
                     render=Rect('Layout1'))


def test_create_empty_layout_top_left(layout1):
    layout1.align = 1
    # has no height, only margins
    result = list(layout1.render())
    assert len(result) == 1
    assert result[0] == "Layout1(0.0, -2.0, 12.0, 0.0)"


def test_create_empty_layout_middle_center(layout1):
    layout1.align = 5
    # has no height, only margins
    result = list(layout1.render())
    assert len(result) == 1
    assert result[0] == "Layout1(-6.0, -1.0, 6.0, 1.0)"


if __name__ == '__main__':
    pytest.main([__file__])
