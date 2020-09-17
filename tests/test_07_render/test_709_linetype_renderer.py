#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.render.linetypes import LineTypeRenderer


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


if __name__ == '__main__':
    pytest.main([__file__])
