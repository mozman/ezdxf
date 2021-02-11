#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec2
from ezdxf.math.clipping import clip_polygon


@pytest.fixture
def rect():
    return [(-1, -1), (1, -1), (1, 1), (-1, 1)]


@pytest.fixture
def subject1():  # overlapping
    return [(0, 0), (2, 0), (2, 2), (0, 2)]


@pytest.fixture
def subject2():  # complete inside
    return [(0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5)]


@pytest.fixture
def subject3():  # complete outside
    return [(1, 1), (2, 1), (2, 2), (1, 2)]


def test_subject_do_overlap_clipping_rect(rect, subject1):
    result = clip_polygon(rect, subject1)
    assert len(result) == 4
    assert Vec2(0, 0) in result
    assert Vec2(1, 0) in result
    assert Vec2(1, 1) in result
    assert Vec2(0, 1) in result


def test_subject_is_inside_rect(rect, subject2):
    result = clip_polygon(rect, subject2)
    assert len(result) == 4
    for v in subject2:
        assert v in result


def test_subject_is_outside_rect(rect, subject3):
    result = clip_polygon(rect, subject3)
    assert len(result) == 0


if __name__ == '__main__':
    pytest.main([__file__])
