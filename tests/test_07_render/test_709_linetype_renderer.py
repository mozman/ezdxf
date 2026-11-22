#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.render.linetypes import LineTypeRenderer
from ezdxf.render._linetypes import _LineTypeRenderer
from ezdxf.acc import USE_C_EXT

renderer_classes = [_LineTypeRenderer]

if USE_C_EXT:
    from ezdxf.acc.linetypes import _LineTypeRenderer as CLineTypeRenderer

    renderer_classes.append(CLineTypeRenderer)


@pytest.fixture(params=renderer_classes)
def ltr_class(request):
    return request.param


def test_line_type_solid():
    ltr = LineTypeRenderer(dashes=tuple())
    assert ltr.is_solid is True
    assert list(ltr.line_segment((0, 0), (5, 0))) == [((0, 0), (5, 0))]


def test_line_start_is_end():
    ltr = LineTypeRenderer(dashes=tuple())
    assert list(ltr.line_segment((0, 0), (0, 0))) == [((0, 0), (0, 0))]


def test_dashed_line_2():
    ltr = LineTypeRenderer(dashes=(1, 1))
    result = list(ltr.line_segment((0, 0), (2, 0)))
    assert len(result) == 1
    assert result[0] == ((0, 0), (1, 0))


def test_dashed_line_4():
    ltr = LineTypeRenderer(dashes=(1, 1))
    result = list(ltr.line_segment((0, 0), (4, 0)))
    assert len(result) == 2
    assert result[0] == ((0, 0), (1, 0))
    # 1,0 -> 2,0 is a gap
    assert result[1] == ((2, 0), (3, 0))


def test_dash_dot_2x_render_issue():
    # DASHDOTX2 (0, 0) -> (20, 0)
    ltr = LineTypeRenderer(dashes=(2.0, 0.2, 0.1, 0.2))
    result = list(ltr.line_segment((0, 0), (20, 0)))
    last_segment = result[-1]
    # Last segment is very, very short:
    assert last_segment[0].isclose(last_segment[1])


def test_dash_of_length_zero_is_a_point(ltr_class):
    # DOT: point, gap, point, gap, ...
    ltr = ltr_class(dashes=(0.0, 1.0))
    result = list(ltr.line_segment((0, 0), (3, 0)))
    assert result == [((0, 0), (0, 0)), ((1, 0), (1, 0)), ((2, 0), (2, 0))]


def test_dash_dot_pattern_keeps_the_points(ltr_class):
    ltr = ltr_class(dashes=(2.0, 1.0, 0.0, 1.0))
    result = list(ltr.line_segment((0, 0), (10, 0)))
    assert result == [
        ((0, 0), (2, 0)),
        ((3, 0), (3, 0)),
        ((4, 0), (6, 0)),
        ((7, 0), (7, 0)),
        ((8, 0), (10, 0)),
    ]


def test_dashed_line_with_both_renderers(ltr_class):
    ltr = ltr_class(dashes=(1.0, 1.0))
    result = list(ltr.line_segment((0, 0), (4, 0)))
    assert result == [((0, 0), (1, 0)), ((2, 0), (3, 0))]


if __name__ == "__main__":
    pytest.main([__file__])
