# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest
from ezdxf.render.path import Path, Command
from ezdxf.math import Vector, Matrix44


def test_init():
    path = Path()
    assert path.start == (0, 0)
    assert len(path) == 0
    assert path.end == (0, 0)


def test_set_start():
    path = Path(start=(1, 2))
    assert path.start == (1, 2)
    path.start = (3, 4, 5)
    assert path.start == (3, 4, 5)
    assert path.end == (3, 4, 5)


def test_line_to():
    path = Path()
    path.line_to((1, 2, 3))
    assert path[0] == (Command.LINE, Vector(1, 2, 3))
    assert path.end == (1, 2, 3)


def test_cubic_to():
    path = Path()
    path.cubic_to((1, 2, 3), (0, 1, 0), (0, 2, 0))
    assert path[0] == (Command.CUBIC, (1, 2, 3), (0, 1, 0), (0, 2, 0))
    assert path.end == (1, 2, 3)


def test_approximate_lines():
    path = Path()
    path.line_to((1, 1))
    path.line_to((2, 0))
    vertices = list(path.approximate())
    assert len(vertices) == 3
    assert vertices[0] == path.start == (0, 0)
    assert vertices[2] == path.end == (2, 0)


def test_approximate_cubic():
    path = Path()
    path.cubic_to((2, 0), (0, 1), (2, 1))
    vertices = list(path.approximate(10))
    assert len(vertices) == 11
    assert vertices[0] == (0, 0)
    assert vertices[-1] == (2, 0)


def test_approximate_line_cubic():
    path = Path()
    path.line_to((2, 0))
    path.cubic_to((4, 0), (2, 1), (4, 1))
    vertices = list(path.approximate(10))
    assert len(vertices) == 12
    assert vertices[0] == (0, 0)
    assert vertices[1] == (2, 0)
    assert vertices[-1] == (4, 0)


def test_transform():
    path = Path()
    path.line_to((2, 0))
    path.cubic_to((4, 0), (2, 1), (4, 1))
    p2 = path.transform(Matrix44.translate(1, 1, 0))
    assert p2.start == (1, 1)
    assert p2[0][1] == (3, 1)  # line to location
    assert p2[1][1] == (5, 1)  # cubic to location
    assert p2[1][2] == (3, 2)  # cubic ctrl1
    assert p2[1][3] == (5, 2)  # cubic ctrl2
    assert p2.end == (5, 1)


if __name__ == '__main__':
    pytest.main([__file__])
