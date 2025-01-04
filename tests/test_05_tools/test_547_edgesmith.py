# Copyright (c) , Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Sequence
import pytest

import math
from ezdxf import edgesmith as es
from ezdxf import edgeminer as em
from ezdxf.entities import Circle, Arc, Ellipse, LWPolyline, Spline
from ezdxf.math import fit_points_to_cad_cv, Vec3
from ezdxf.layouts import VirtualLayout


def test_circle_is_a_closed_entity():
    circle = Circle()
    circle.dxf.radius = 1

    assert es.is_closed_entity(circle) is True


def test_circle_of_radius_0_is_not_a_closed_entity():
    circle = Circle()
    circle.dxf.radius = 0

    assert es.is_closed_entity(circle) is False


@pytest.mark.parametrize("start,end", [(0, 180), (0, 0), (180, 180), (360, 360)])
def test_open_arc_is_not_a_closed_entity(start, end):
    arc = Arc()
    arc.dxf.radius = 1
    arc.dxf.start_angle = start
    arc.dxf.end_angle = end

    assert es.is_closed_entity(arc) is False


@pytest.mark.parametrize("start,end", [(0, 360), (360, 0), (180, -180)])
def test_closed_arc_is_a_closed_entity(start, end):
    arc = Arc()
    arc.dxf.radius = 1
    arc.dxf.start_angle = start
    arc.dxf.end_angle = end

    assert es.is_closed_entity(arc) is True


@pytest.mark.parametrize(
    "start,end", [(0, math.pi), (0, 0), (math.pi, math.pi), (math.tau, math.tau)]
)
def test_open_ellipse_is_not_a_closed_entity(start, end):
    ellipse = Ellipse()
    ellipse.dxf.major_axis = (1, 0)
    ellipse.dxf.ratio = 1
    ellipse.dxf.start_param = start
    ellipse.dxf.end_param = end

    assert es.is_closed_entity(ellipse) is False


@pytest.mark.parametrize(
    "start,end", [(0, math.tau), (math.tau, 0), (math.pi, -math.pi)]
)
def test_closed_ellipse_is_a_closed_entity(start, end):
    ellipse = Ellipse()
    ellipse.dxf.major_axis = (1, 0)
    ellipse.dxf.ratio = 1
    ellipse.dxf.start_param = start
    ellipse.dxf.end_param = end

    assert es.is_closed_entity(ellipse) is True


# Note: Ellipses with major_axis == (0, 0, 0) are not valid.
# They cannot be created by ezdxf and loading such ellipses raises an DXFStructureError.


def test_closed_lwpolyline_is_a_closed_entity():
    polyline = LWPolyline()
    polyline.closed = True
    polyline.append_points([(0, 0), (10, 0), (10, 10)])

    assert es.is_closed_entity(polyline) is True


def test_open_lwpolyline_is_not_a_closed_entity():
    polyline = LWPolyline()
    polyline.closed = False
    polyline.append_points([(0, 0), (10, 0), (10, 10)])

    assert es.is_closed_entity(polyline) is False


def test_explicit_closed_lwpolyline_is_a_closed_entity():
    polyline = LWPolyline()
    polyline.closed = False
    polyline.append_points([(0, 0), (10, 0), (10, 10), (0, 0)])

    assert es.is_closed_entity(polyline) is True


def test_closed_spline():
    ct = fit_points_to_cad_cv([(0, 0), (10, 0), (10, 10), (0, 0)])
    spline = Spline()
    spline.apply_construction_tool(ct)

    assert es.is_closed_entity(spline) is True


def test_open_spline():
    ct = fit_points_to_cad_cv([(0, 0), (10, 0), (10, 10), (0, 10)])
    spline = Spline()
    spline.apply_construction_tool(ct)

    assert es.is_closed_entity(spline) is False


def test_empty_spline():
    spline = Spline()

    assert es.is_closed_entity(spline) is False


class TestLineAndArcToPolyline:
    @pytest.fixture(scope="class")
    def edges(self) -> Sequence[em.Edge]:
        layout = VirtualLayout()
        layout.add_line((0, 0), (6, 0))
        layout.add_arc((6, 3), radius=3, start_angle=270, end_angle=90)
        layout.add_line((6, 6), (0, 6))
        layout.add_line((0, 6), (0, 0))
        return list(es.edges_from_entities_2d(layout))

    def test_create_lwpolyline(self, edges: Sequence[em.Edge]):
        def int_pnt(point):
            return tuple(round(v) for v in point)

        pl = es.lwpolyline_from_chain(edges)
        assert len(pl.lwpoints) == 5
        assert int_pnt(pl.lwpoints[1]) == (6, 0, 0, 0, 1)
        assert int_pnt(pl.lwpoints[2]) == (6, 6, 0, 0, 0)

    def test_create_polyline2d(self, edges: Sequence[em.Edge]):
        def int_pnt(vertex):
            dxf = vertex.dxf
            return round(dxf.location.x), round(dxf.location.y), round(dxf.bulge)

        pl = es.polyline2d_from_chain(edges)
        assert len(pl.vertices) == 5

        assert int_pnt(pl.vertices[1]) == (6, 0, 1)
        assert int_pnt(pl.vertices[2]) == (6, 6, 0)

    def test_create_polyline_path(self, edges: Sequence[em.Edge]):
        # HATCH boundary path: ezdxf.entities.PolylinePath
        def int_pnt(point):
            return tuple(round(v) for v in point)

        pl_path = es.polyline_path_from_chain(edges)
        assert len(pl_path.vertices) == 5
        assert int_pnt(pl_path.vertices[1]) == (6, 0, 1)
        assert int_pnt(pl_path.vertices[2]) == (6, 6, 0)

    def test_create_edge_path(self, edges: Sequence[em.Edge]):
        # HATCH boundary path: ezdxf.entities.EdgePath
        pass

    def test_create_path(self, edges: Sequence[em.Edge]):
        # ezdxf.path.Path
        path = es.path2d_from_chain(edges)
        commands = path.commands()
        assert len(commands) == 5
        assert path.start.isclose((0, 0))
        assert path.is_closed is True
        assert path.has_curves is True
        assert path.has_lines is True


class TestBoundingBox:
    def test_empty_sequence(self):
        bbox = es.bounding_box_2d([])
        assert bbox.has_data is False

    def test_one_edge(self):
        edge = em.make_edge((0, 0), (1, 1))
        bbox = es.bounding_box_2d([edge])
        assert bbox.extmin.isclose((0, 0))
        assert bbox.extmax.isclose((1, 1))

    def test_more_edges(self):
        edge1 = em.make_edge((0, 0), (3, 4))
        edge2 = em.make_edge((-1, -2), (0, 0))
        bbox = es.bounding_box_2d([edge1, edge2])
        assert bbox.extmin.isclose((-1, -2))
        assert bbox.extmax.isclose((3, 4))


class TestIsInsidePolygon:
    @pytest.fixture
    def edges(self):
        return [
            em.make_edge((0, 0), (1, 0)),
            em.make_edge((1, 0), (1, 1)),
            em.make_edge((1, 1), (0, 1)),
            em.make_edge((0, 1), (0, 0)),
        ]

    def test_is_inside_polygon(self, edges):
        assert es.is_inside_polygon_2d(edges, (0.5, 0.5)) is True

    def test_on_border_is_inside_polygon(self, edges):
        assert es.is_inside_polygon_2d(edges, (0.5, 1.0)) is True

    def test_is_outside_polygon(self, edges):
        assert es.is_inside_polygon_2d(edges, (0.5, 1.5)) is False

    def test_raise_exception_if_not_a_loop(self, edges):
        with pytest.raises(ValueError):
            es.is_inside_polygon_2d(edges[:-1], (0.5, 0.5))


class TestIntersectingEdges:
    @pytest.fixture
    def edges(self):
        return [
            em.make_edge((0, -1), (0, 1)),
            em.make_edge((1, -1), (1, 1)),
            em.make_edge((2, -1), (2, 1)),
            em.make_edge((3, -1), (3, 1)),
        ]

    def test_empty_sequence(self, edges):
        assert len(es.intersecting_edges_2d([], (-1, 0.5))) == 0

    def test_no_intersection(self, edges):
        assert len(es.intersecting_edges_2d(edges, (-2, 0), (-1, 0))) == 0

    def test_first_intersection(self, edges):
        result = es.intersecting_edges_2d(edges, (-2, 0), (0.5, 0))
        assert result[0].edge.id == edges[0].id
        assert math.isclose(result[0].distance, 2) is True

    def test_all_intersections(self, edges):
        result = es.intersecting_edges_2d(edges, (-2, 0), (4, 0))
        assert len(result) == len(edges)

    def test_arbitrary_p2_v1(self, edges):
        result = es.intersecting_edges_2d(edges, (-2, 0))
        assert len(result) == len(edges)

    def test_arbitrary_p2_v2(self, edges):
        result = es.intersecting_edges_2d(edges, (4, 0))
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__])
