# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.math import triangulation, Vec3, area, BoundingBox2d
from ezdxf.render import forms


def total_area(triangles):
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


def test_polygon_data0(polygon_data0):
    data = polygon_data0
    triangles = list(triangulation.ear_clipping_2d(data.vertices))
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


def test_open_polygons_are_the_regular_case():
    result = list(
        triangulation.ear_clipping_2d(
            [(0, 0), (1, 0), (1, 1), (1, 2), (0, 2), (0, 1)]
        )
    )
    assert len(result) == 4


def test_closed_polygons_work_also_as_expected():
    result = list(
        triangulation.ear_clipping_2d(
            [(0, 0), (1, 0), (1, 1), (1, 2), (0, 2), (0, 1), (0, 0)]
        )
    )
    assert len(result) == 4


def test_empty_input_returns_empty_result():
    result = list(triangulation.ear_clipping_2d([]))
    assert len(result) == 0


def test_single_vertex_returns_empty_result():
    result = list(triangulation.ear_clipping_2d([(0, 0)]))
    assert len(result) == 0


class TestEarClipping3D:
    def test_simple_case(self):
        cube = forms.cube()
        for face in list(cube.faces_as_vertices()):
            result = list(triangulation.ear_clipping_3d(face))
            assert len(result) == 2

    def test_polygon(self):
        polygon = Vec3.list(
            [
                (0, 0, 0),
                (1, 0, 0),
                (1, 0, 1),
                (2, 0, 1),
                (2, 0, 2),
                (0, 0, 2),
            ]
        )
        result = list(triangulation.ear_clipping_3d(polygon))
        assert len(result) == 4
        for triangle in result:
            assert all(abs(v.y) < 1e-9 for v in triangle)

    def test_input_type_is_Vec3(self):
        with pytest.raises(TypeError):
            list(triangulation.ear_clipping_3d([(0, 0, 0)]))  # type: ignore

    def test_empty_input_returns_empty_result(self):
        assert len(list(triangulation.ear_clipping_3d([]))) == 0

    def test_invalid_polygon_raise_zero_division_error(self):
        with pytest.raises(ZeroDivisionError):
            list(
                triangulation.ear_clipping_3d(
                    Vec3.list([(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)])
                )
            )


def test_simple_polygon_triangulation():
    open_square = forms.square()
    r = triangulation.simple_polygon_triangulation(open_square)
    assert len(r) == 4
    center = r[0][2]
    assert center == (0.5, 0.5, 0)

    closed_square = list(forms.circle(4, elevation=2, close=True))
    assert len(closed_square) == 5
    r = triangulation.simple_polygon_triangulation(closed_square)
    assert len(r) == 4
    center = r[0][2]
    assert center.isclose((0, 0, 2))

    # also subdivide triangles
    r = triangulation.simple_polygon_triangulation(
        Vec3.list([(0, 0), (1, 0), (1, 1)])
    )
    assert len(r) == 3


if __name__ == "__main__":
    pytest.main([__file__])
