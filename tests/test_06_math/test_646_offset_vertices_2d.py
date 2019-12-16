# Copyright (c) 2019, Manfred Moitzi
# License: MIT License

from ezdxf.math import Vec2, offset_vertices_2d

PRECISION = 1e-3


def test_0_offset():
    vertices = [(1, 2, 3), (5, 2, 3)]
    result = list(offset_vertices_2d(vertices, 0))
    assert result[0] == (1, 2)
    assert result[1] == (5, 2)


def test_2_horiz_vertices_left_offset():
    vertices = [(1, 2), (5, 2)]
    result = list(offset_vertices_2d(vertices, 1))
    assert result[0] == (1, 3)
    assert result[1] == (5, 3)


def test_2_horiz_vertices_right_offset():
    vertices = [(1, 2), (5, 2)]
    result = list(offset_vertices_2d(vertices, -1))
    assert result[0] == (1, 1)
    assert result[1] == (5, 1)


def test_2_vert_vertices_left_offset():
    vertices = [(1, 2), (1, 5)]
    result = list(offset_vertices_2d(vertices, 1))
    assert result[0] == (0, 2)
    assert result[1] == (0, 5)


def test_2_vert_vertices_right_offset():
    vertices = [(1, 2), (1, 5)]
    result = list(offset_vertices_2d(vertices, -1))
    assert result[0] == (2, 2)
    assert result[1] == (2, 5)


def test_3_horiz_collinear_vertices():
    vertices = [(1, 2), (5, 2), (9, 2)]
    result = list(offset_vertices_2d(vertices, 1))
    assert result[0] == (1, 3)
    assert result[1] == (5, 3)
    assert result[2] == (9, 3)


def test_3_vert_collinear_vertices():
    vertices = [(1, 2), (1, 5), (1, 9)]
    result = list(offset_vertices_2d(vertices, 1))
    assert result[0] == (0, 2)
    assert result[1] == (0, 5)
    assert result[2] == (0, 9)


def test_3_vertices():
    vertices = [(0, 0), (300, 150), (450, 50)]
    result = list(offset_vertices_2d(vertices, 10))
    assert result[0].isclose(Vec2((-4.4721, 8.9443)), abs_tol=PRECISION)
    assert result[1].isclose(Vec2((300.7184, 161.5396)), abs_tol=PRECISION)
    assert result[2].isclose(Vec2((455.547, 58.3205)), abs_tol=PRECISION)


def test_closed_square_inside():
    vertices = [(0, 0), (5, 0), (5, 5), (0, 5)]
    result = list(offset_vertices_2d(vertices, 1, closed=True))
    assert result[0] == (1, 1)
    assert result[1] == (4, 1)
    assert result[2] == (4, 4)
    assert result[3] == (1, 4)


def test_closed_triangle_inside():
    vertices = [(0, 0), (5, 0), (2.5, 5)]
    result = list(offset_vertices_2d(vertices, 1, closed=True))
    assert result[0].isclose(Vec2((1.618, 1)), abs_tol=PRECISION)
    assert result[1].isclose(Vec2((3.382, 1)), abs_tol=PRECISION)
    assert result[2].isclose(Vec2((2.5, 2.7639)), abs_tol=PRECISION)


def test_closed_shape_with_collinear_last_segment():
    vertices = [(0, 0), (5, 0), (5, 5), (-5, 5), (-5, 0)]
    result = list(offset_vertices_2d(vertices, 1, closed=True))
    assert len(result) == len(vertices)
    assert result[0] == (0, 1)
    assert result[1] == (4, 1)
    assert result[2] == (4, 4)
    assert result[3] == (-4, 4)
    assert result[4] == (-4, 1)


def test_3_horiz_collinear_vertices_closed():
    vertices = [(1, 2), (5, 2), (9, 2)]
    result = list(offset_vertices_2d(vertices, 1, closed=True))
    assert len(result) == len(vertices)+2  # get 2 extra vertices
    # but the first vertex, would be expected as last vertex
    assert result[0] == (1, 1)
    assert result[1] == (1, 3)
    assert result[2] == (5, 3)
    # closing segment: (9, 2) -> (1, 2)
    assert result[3] == (9, 3)
    assert result[4] == (9, 1)
