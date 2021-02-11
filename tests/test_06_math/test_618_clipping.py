#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec2
from ezdxf.math.clipping import clip_polygon_2d


@pytest.fixture
def rect():
    return [(-1, -1), (1, -1), (1, 1), (-1, 1)]


@pytest.fixture
def overlapping():  # overlapping
    return [(0, 0), (2, 0), (2, 2), (0, 2)]


@pytest.fixture
def inside():  # complete inside
    return [(0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5)]


@pytest.fixture
def outside():  # complete outside
    return [(1, 1), (2, 1), (2, 2), (1, 2)]


def test_subject_do_overlap_clipping_rect(rect, overlapping):
    result = clip_polygon_2d(rect, overlapping)
    assert len(result) == 4
    assert Vec2(0, 0) in result
    assert Vec2(1, 0) in result
    assert Vec2(1, 1) in result
    assert Vec2(0, 1) in result


def test_subject_is_inside_rect(rect, inside):
    result = clip_polygon_2d(rect, inside)
    assert len(result) == 4
    for v in inside:
        assert v in result


def test_clockwise_oriented_clipping_rect(rect, inside):
    rect.reverse()
    result = clip_polygon_2d(rect, inside)
    assert len(result) == 4
    for v in inside:
        assert v in result


def test_subject_is_outside_rect(rect, outside):
    result = clip_polygon_2d(rect, outside)
    assert len(result) == 0


if __name__ == '__main__':
    pytest.main([__file__])
