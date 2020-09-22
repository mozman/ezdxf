# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest

from ezdxf.math import has_clockwise_orientation


@pytest.fixture
def v1():
    return [(0, 0), (1, 0), (1, 1), (0, 1)]


@pytest.mark.parametrize('vertices', [
    [(0, 0), (1, 0), (1, 1)],
    [(0, 0), (1, 0), (1, 1), (0, 1)],
])
def test_has_clockwise_orientation(vertices):
    assert has_clockwise_orientation(vertices) is False


@pytest.mark.parametrize('vertices', [
    [(1, 1), (1, 0), (0, 0)],
    [(0, 1), (1, 1), (1, 0), (0, 0)],
])
def test_has_counter_clockwise_orientation(vertices):
    assert has_clockwise_orientation(vertices) is True


if __name__ == '__main__':
    pytest.main([__file__])
