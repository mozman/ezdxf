import pytest
from ezdxf.render.shape import Shape, Vector


@pytest.fixture()
def square():
    return Shape([(0, 0), (1, 0), (1, 1), (0, 1)])


def test_init(square):

    # shape is list like
    assert len(square) == 4

    # elements are Vectors?
    assert square[0].x == 0
    assert square[0].y == 0
    assert square[2].x == 1
    assert square[2].y == 1

    e = list(square)
    assert len(e) == 4

    square.append((3, 3))
    assert square[-1] == (3, 3)


def test_translate(square):
    square.translate((1, 0))
    assert square[0] == (1, 0)
    assert square[2] == (2, 1)


def test_scale(square):
    square.scale(sx=2, sy=3)
    assert square[0] == (0, 0)
    assert square[2] == (2, 3)


def test_scale_uniform(square):
    square.scale_uniform(1.5)
    assert square[0] == (0, 0)
    assert square[2] == (1.5, 1.5)


def test_rotate(square):
    square.rotate(90)
    assert square[0] == (0, 0)
    assert square[2] == (-1, 1)
    square.rotate(90)
    assert square[0] == (0, 0)
    assert square[2] == (-1, -1)


def test_rotate_center(square):
    square.translate((2, 2))
    square.rotate(90, center=Vector(2, 2))
    assert square[0] == (2, 2)
    assert square[2] == (1, 3)

