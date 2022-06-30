#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.render import forms
from ezdxf.math import Vec2, is_convex_polygon_2d


def test_open_triangle():
    polygon = Vec2.list([(0, 0), (1, 0), (1, 1)])
    assert is_convex_polygon_2d(polygon) is True
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is True


def test_closed_triangle():
    polygon = Vec2.list([(0, 0), (1, 0), (1, 1), (0, 0)])
    assert is_convex_polygon_2d(polygon) is True
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is True


def test_open_square():
    polygon = Vec2.list([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert is_convex_polygon_2d(polygon) is True
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is True


def test_closed_square():
    polygon = Vec2.list([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    assert is_convex_polygon_2d(polygon) is True
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is True


@pytest.mark.parametrize(
    "polygon",
    [
        Vec2.list([(0, 0)]),
        Vec2.list([(0, 0), (1, 0)]),
        Vec2.list([(0, 0), (1, 0), (0, 0)]),
    ],
)
def test_irregular_polygons(polygon):
    assert is_convex_polygon_2d(polygon) is False
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is False


def test_two_colinear_edges():
    polygon = Vec2.list([(0, 0), (1, 0), (2, 0), (0, 1)])
    assert is_convex_polygon_2d(polygon) is True
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is True


def test_all_colinear_edges():
    polygon = Vec2.list([(0, 0), (1, 0), (2, 0), (3, 0)])
    assert is_convex_polygon_2d(polygon) is False
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is False


def test_some_coincident_vertices():
    polygon = Vec2.list([(0, 0), (1, 0), (1, 0), (0, 1)])
    assert is_convex_polygon_2d(polygon) is True
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is True


def test_all_coincident_vertices():
    polygon = Vec2.list([(0, 0), (0, 0), (0, 0), (0, 0)])
    assert is_convex_polygon_2d(polygon) is False
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is False


@pytest.mark.parametrize("n", [3, 4, 11])
def test_regular_convex_ngons(n):
    polygon = Vec2.list(forms.ngon(n, radius=1.0))
    assert is_convex_polygon_2d(polygon) is True
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is True


@pytest.mark.parametrize("n", [4, 5, 11])
def test_star_is_concave(n):
    polygon = Vec2.list(forms.star(n, r1=1.0, r2=2.0))
    assert is_convex_polygon_2d(polygon) is False
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is False


def test_concave_quadrilateral():
    polygon = Vec2.list([(0, 0), (1, 1), (2, 0), (1, 2)])
    assert is_convex_polygon_2d(polygon) is False
    polygon.reverse()
    assert is_convex_polygon_2d(polygon) is False


if __name__ == "__main__":
    pytest.main([__file__])
