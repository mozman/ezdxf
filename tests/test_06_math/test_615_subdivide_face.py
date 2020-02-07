# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import subdivide_face, Vector, Vec2
from ezdxf.render.forms import square


def test_subdivide_square_in_quads():
    b = square(2)
    result = list(subdivide_face(b, quads=True))
    assert len(result) == 4
    assert result[0] == ((0, 0), (1, 0), (1, 1), (0, 1))


def test_subdivide_square_in_triangles():
    b = square(2)
    result = list(subdivide_face(b, quads=False))
    assert len(result) == 8
    assert result[0] == ((0, 1), (0, 0), (1, 1))
    assert result[1] == ((0, 0), (1, 0), (1, 1))


def test_subdivide_triangle():
    t = Vector.list([(0, 0), (2, 0), (1, 2)])
    assert len(list(subdivide_face(t, quads=True))) == 3
    assert len(list(subdivide_face(t, quads=False))) == 6


def test_subdivide_vec2_square_in_quads():
    b = Vec2.list(square(2))
    result = list(subdivide_face(b, quads=True))
    assert len(result) == 4
    assert result[0] == ((0, 0), (1, 0), (1, 1), (0, 1))


if __name__ == '__main__':
    pytest.main([__file__])

