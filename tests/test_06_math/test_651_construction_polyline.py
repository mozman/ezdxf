#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import List
import math
import pytest
from ezdxf.math import ConstructionPolyline, Vec3


@pytest.fixture(scope="module")
def poly1() -> ConstructionPolyline:
    return ConstructionPolyline([(0, 0), (1, 0), (1, 1), (0, 1)])


@pytest.fixture(scope="module")
def poly2() -> ConstructionPolyline:
    return ConstructionPolyline([(0, 0), (1, 0), (1, 1), (0, 1)], close=True)


class TestSequenceInterface:
    def test_empty_polyline(self):
        cp = ConstructionPolyline([])
        assert len(cp) == 0

    def test_len_open_polyline(self, poly1):
        assert len(poly1) == 4

    def test_len_closed_polyline(self, poly2):
        assert len(poly2) == 5

    def test_get_single_vertex(self, poly1):
        assert poly1[1] == (1, 0)

    def test_get_last_vertex(self, poly1):
        assert poly1[-1] == (0, 1)

    def test_get_vertex_slice(self, poly1):
        assert list(poly1[1:3]) == [(1, 0), (1, 1)]

    def test_vertex_slice_has_same_type(self, poly1):
        assert isinstance(poly1[1:3], ConstructionPolyline)

    def test_is_immutable(self, poly1):
        with pytest.raises(TypeError):
            poly1[1] = (1, 0)
        with pytest.raises(TypeError):
            del poly1[1]


class TestExtendedData:
    """The data() method returns the distance from the start vertex along the
    polyline, the distance from the previous vertex and the vertex itself for
    a give index.

    """

    def test_empty_polyline_raises_Value_error(self):
        with pytest.raises(ValueError):
            ConstructionPolyline([]).data(0)

    def test_data_0(self, poly1):
        assert poly1.data(0) == (0, 0, (0, 0))

    def test_data_1(self, poly1):
        assert poly1.data(1) == (1, 1, (1, 0))

    def test_data_2(self, poly1):
        assert poly1.data(2) == (2, 1, (1, 1))

    def test_data_3(self, poly1):
        assert poly1.data(3) == (3, 1, (0, 1))

    def test_data_for_negative_index(self, poly1):
        assert poly1.data(-1) == (3, 1, (0, 1))
        assert poly1.data(-2) == (2, 1, (1, 1))

    def test_vertices_at_the_same_location(self):
        cp = ConstructionPolyline([(0, 0), (0, 0), (0, 0)])
        assert cp.data(0) == (0, 0, (0, 0))
        assert cp.data(1) == (0, 0, (0, 0))
        assert cp.data(2) == (0, 0, (0, 0))

    def test_raises_index_error(self, poly1):
        with pytest.raises(IndexError):
            poly1.data(4)


class TestLength:
    def test_empty_polyline(self):
        assert ConstructionPolyline([]).length == 0.0

    def test_open_polyline(self, poly1):
        assert poly1.length == 3.0

    def test_closed_polyline(self, poly2):
        assert poly2.length == 4.0

    def test_vertices_at_the_same_location(self):
        cp = ConstructionPolyline([(0, 0), (0, 0), (0, 0)])
        assert cp.length == 0.0


class TestIsClosed:
    def test_empty_polyline_is_not_closed(self):
        assert ConstructionPolyline([]).is_closed is False

    def test_polyline_with_too_few_vertices_is_not_closed(self):
        assert ConstructionPolyline([(0, 0)]).is_closed is False
        assert ConstructionPolyline([(0, 0), (0, 0)]).is_closed is False

    def test_poly1_is_not_closed(self, poly1):
        assert poly1.is_closed is False

    def test_poly2_is_closed(self, poly2):
        assert poly2.is_closed is True


class TestVertexAt:
    def test_empty_polyline_raises_error(self):
        with pytest.raises(ValueError):
            ConstructionPolyline([]).vertex_at(0.0)

    def test_too_few_vertices_raises_error(self):
        with pytest.raises(ValueError):
            ConstructionPolyline([(0, 0)]).vertex_at(0.0)

    def test_out_of_range_raises_error(self, poly1):
        with pytest.raises(ValueError):
            poly1.vertex_at(-1)
        with pytest.raises(ValueError):
            poly1.vertex_at(poly1.length + 0.01)

    def test_interpolation_at_vertex_location(self, poly1):
        assert poly1.vertex_at(0.) == (0, 0)
        assert poly1.vertex_at(1.) == (1, 0)
        assert poly1.vertex_at(2.) == (1, 1)
        assert poly1.vertex_at(3.) == (0, 1)

    def test_interpolate_last_vertex_of_closed_polyline(self, poly2):
        assert poly2.vertex_at(0.) == (0, 0)
        assert poly2.vertex_at(poly2.length) == (0, 0)

    def test_interpolate_at_first_edge(self, poly1):
        """Interpolate edge  (0, 0) -> (1, 0)"""
        assert poly1.vertex_at(0.1).isclose((0.1, 0))
        assert poly1.vertex_at(0.5).isclose((0.5, 0))
        assert poly1.vertex_at(0.9).isclose((0.9, 0))

    def test_interpolate_at_second_edge(self, poly1):
        """Interpolate edge  (1, 0) -> (1, 1)"""
        assert poly1.vertex_at(1.1).isclose((1.0, 0.1))
        assert poly1.vertex_at(1.5).isclose((1.0, 0.5))
        assert poly1.vertex_at(1.9).isclose((1.0, 0.9))

    def test_interpolation_for_coincident_vertices_in_front(self):
        cp = ConstructionPolyline([(0, 0), (0, 0), (0, 0), (1, 0)])
        assert cp.vertex_at(0.0).isclose((0.0, 0.0))
        assert cp.vertex_at(0.1).isclose((0.1, 0.0))
        assert cp.vertex_at(0.5).isclose((0.5, 0.0))
        assert cp.vertex_at(0.9).isclose((0.9, 0.0))
        assert cp.vertex_at(1.0).isclose((1.0, 0.0))

    def test_interpolation_for_coincident_vertices_after(self):
        cp = ConstructionPolyline([(0, 0), (1, 0), (1, 0), (1, 0)])
        assert cp.vertex_at(0.0).isclose((0.0, 0.0))
        assert cp.vertex_at(0.1).isclose((0.1, 0.0))
        assert cp.vertex_at(0.5).isclose((0.5, 0.0))
        assert cp.vertex_at(0.9).isclose((0.9, 0.0))
        assert cp.vertex_at(1.0).isclose((1.0, 0.0))

    def test_interpolation_for_coincident_vertices_between(self):
        cp = ConstructionPolyline([(0, 0), (0.5, 0), (0.5, 0), (0.5, 0), (1, 0)])
        assert cp.vertex_at(0.0).isclose((0.0, 0.0))
        assert cp.vertex_at(0.1).isclose((0.1, 0.0))
        assert cp.vertex_at(0.5).isclose((0.5, 0.0))
        assert cp.vertex_at(0.9).isclose((0.9, 0.0))
        assert cp.vertex_at(1.0).isclose((1.0, 0.0))


class TestDivide:
    @pytest.mark.parametrize("count", [-1, 0, 1])
    def test_raises_error_invalid_count(self, count, poly1):
        with pytest.raises(ValueError):
            list(poly1.divide(count))

    def test_divide_by_3(self, poly1):
        vertices: List[Vec3] = list(poly1.divide(3))
        assert vertices[0].isclose(poly1[0])
        assert vertices[1].isclose((1, 0.5))
        assert vertices[2].isclose(poly1[-1])

    def test_divide_by_length(self, poly1):
        vertices: List[Vec3] = list(poly1.divide_by_length(0.7))
        assert len(vertices) == 5
        assert vertices[-1].isclose(poly1.vertex_at(2.8))

    def test_divide_by_length_force_last_vertex(self, poly1):
        vertices: List[Vec3] = list(poly1.divide_by_length(0.7, force_last=True))
        assert len(vertices) == 6
        assert vertices[-1].isclose(poly1[-1])


class TestApproximationAccuracy:
    def test_unit_circle(self):
        from ezdxf.entities import Circle
        # create unit circle
        circle: Circle = Circle.new(dxfattribs={"center": (0, 0), "radius": 1.})
        cp = ConstructionPolyline(circle.flattening(0.01))
        assert cp.is_closed is True
        assert len(cp) > 20
        assert abs(cp.length - math.tau) < 0.02

    def test_unit_circle_by_path(self):
        from ezdxf import path
        p = path.unit_circle()
        cp = ConstructionPolyline(p.flattening(0.01))
        assert cp.is_closed is True
        assert len(cp) > 60
        assert abs(cp.length - math.tau) < 0.002


if __name__ == "__main__":
    pytest.main([__file__])
