#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Sequence, List
import pytest
import math
from functools import partial
from ezdxf.math import Vec2, BoundingBox2d, area, UVec
from ezdxf.render import forms
from ezdxf.math._mapbox_earcut import earcut as _py_earcut

CYTHON = "Cython"
try:
    from ezdxf.acc.mapbox_earcut import earcut as _cy_earcut
except ImportError:
    CYTHON = "CPython"
    _cy_earcut = _py_earcut


def earcut_driver(
    exterior: Iterable[UVec],
    holes: Iterable[Iterable[UVec]] = None,
    func=_py_earcut,
) -> List[Sequence[Vec2]]:
    points: List[Vec2] = Vec2.list(exterior)
    if len(points) == 0:
        return []
    holes_: List[List[Vec2]] = []
    if holes:
        holes_ = [Vec2.list(hole) for hole in holes]
    return func(points, holes_)


py_earcut = partial(earcut_driver, func=_py_earcut)
cy_earcut = partial(earcut_driver, func=_cy_earcut)
functions = [py_earcut, cy_earcut]
names = ("CPython", CYTHON)


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


@pytest.mark.parametrize("earcut", functions, ids=names)
def test_triangulate_ccw_square(earcut):
    square = forms.square(2)
    triangles = earcut(square)
    assert len(triangles) == 2
    assert total_area(triangles) == pytest.approx(4.0)


@pytest.mark.parametrize("earcut", functions, ids=names)
def test_triangulate_cw_square(earcut):
    square = list(reversed(forms.square(2)))
    triangles = earcut(square)
    assert len(triangles) == 2
    assert total_area(triangles) == pytest.approx(4.0)


@pytest.mark.parametrize("earcut", functions, ids=names)
def test_triangulate_concave_gear_shape(earcut):
    square = list(
        forms.gear(32, top_width=1, bottom_width=3, height=2, outside_radius=10)
    )
    triangles = earcut(square)
    assert len(triangles) == 126
    assert total_area(triangles) == pytest.approx(265.17899685816224)


@pytest.mark.parametrize("earcut", functions, ids=names)
def test_triangulate_square_with_square_hole(earcut):
    square = forms.square(4, center=True)
    hole = forms.square(2, center=True)
    triangles = earcut(square, holes=[hole])
    assert len(triangles) == 8
    assert total_area(triangles) == pytest.approx(16.0 - 4.0)


@pytest.mark.parametrize("earcut", functions, ids=names)
def test_triangulate_square_with_two_holes(earcut):
    square = list(forms.square(4, center=True))
    hole0 = list(forms.translate(forms.square(1, center=True), (-1, -1)))
    hole1 = list(forms.translate(forms.square(1, center=True), (1, 1)))
    holes = [hole0, hole1]
    triangles = earcut(square, holes=holes)
    assert len(triangles) == 14
    assert total_area(triangles) == pytest.approx(16.0 - 2.0)


@pytest.mark.parametrize("earcut", functions, ids=names)
def test_triangulate_square_with_steiner_point(earcut):
    square = forms.square(4, center=True)
    steiner_point = [(0, 0)]  # defined as a hole with a single point
    triangles = earcut(square, holes=[steiner_point])
    assert len(triangles) == 4
    assert total_area(triangles) == pytest.approx(16.0)


@pytest.mark.parametrize("earcut", functions, ids=names)
def test_empty_exterior(earcut):
    triangles = list(earcut([]))
    assert len(triangles) == 0


@pytest.mark.parametrize("earcut", functions, ids=names)
def test_empty_holes(earcut):
    square = forms.square(2)
    assert len(earcut(square, [[]])) == 2


@pytest.mark.parametrize("earcut", functions, ids=names)
def test_polygon_data0(polygon_data0, earcut):
    data = polygon_data0
    triangles = list(earcut(data.vertices))
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
