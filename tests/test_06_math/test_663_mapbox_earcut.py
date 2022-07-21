#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Sequence
import pytest
import math
from ezdxf.math.triangulation import mapbox_earcut_2d
from ezdxf.math import Vec2, BoundingBox2d, area
from ezdxf.render import forms


def total_area(triangles: Iterable[Sequence[Vec2]]):
    area = 0.0
    sides = []
    for triangle in triangles:
        sides.clear()
        for i in range(3):
            pt = triangle[i]
            pt2 = triangle[(i + 1) % 3]
            sides.append(pt.distance(pt2))
        a, b, c = sides
        area += 0.25 * math.sqrt(
            (a + b + c) * (-a + b + c) * (a - b + c) * (a + b - c)
        )
    return area


def test_triangulate_ccw_square():
    square = forms.square(2)
    triangles = mapbox_earcut_2d(square)
    assert len(triangles) == 2
    assert total_area(triangles) == pytest.approx(4.0)


def test_triangulate_cw_square():
    square = list(reversed(forms.square(2)))
    triangles = mapbox_earcut_2d(square)
    assert len(triangles) == 2
    assert total_area(triangles) == pytest.approx(4.0)


def test_triangulate_concave_gear_shape():
    square = list(
        forms.gear(32, top_width=1, bottom_width=3, height=2, outside_radius=10)
    )
    triangles = mapbox_earcut_2d(square)
    assert len(triangles) == 126
    assert total_area(triangles) == pytest.approx(265.17899685816224)


def test_triangulate_square_with_square_hole():
    square = forms.square(4, center=True)
    hole = forms.square(2, center=True)
    triangles = mapbox_earcut_2d(square, holes=[hole])
    assert len(triangles) == 8
    assert total_area(triangles) == pytest.approx(16.0 - 4.0)


def test_triangulate_square_with_two_holes():
    square = list(forms.square(4, center=True))
    hole0 = list(forms.translate(forms.square(1, center=True), (-1, -1)))
    hole1 = list(forms.translate(forms.square(1, center=True), (1, 1)))
    holes = [hole0, hole1]
    triangles = mapbox_earcut_2d(square, holes=holes)
    assert len(triangles) == 14
    assert total_area(triangles) == pytest.approx(16.0 - 2.0)


def test_triangulate_square_with_steiner_point():
    square = forms.square(4, center=True)
    steiner_point = [(0, 0)]  # defined as a hole with a single point
    triangles = mapbox_earcut_2d(square, holes=[steiner_point])
    assert len(triangles) == 4
    assert total_area(triangles) == pytest.approx(16.0)


def test_empty_exterior():
    triangles = list(mapbox_earcut_2d([]))
    assert len(triangles) == 0


def test_empty_holes():
    square = forms.square(2)
    assert len(mapbox_earcut_2d(square, [[]])) == 2


def test_polygon_data0(polygon_data0):
    data = polygon_data0
    triangles = list(mapbox_earcut_2d(data.vertices))
    area0 = area(data.vertices)
    area1 = total_area(triangles)
    absolute_error = abs(area0 - area1)

    assert math.isclose(
        area0, area1
    ), "{}: area absolute error ({:.3f} - {:.3f} = {:.6f})".format(
        data.name,
        area0,
        area1,
        absolute_error,
    )
    bbox0 = BoundingBox2d(data.vertices)
    bbox1 = BoundingBox2d()
    for t in triangles:
        bbox1.extend(t)
    assert bbox0.extmin.isclose(bbox1.extmin)
    assert bbox0.extmax.isclose(bbox1.extmax)


if __name__ == "__main__":
    pytest.main([__file__])
