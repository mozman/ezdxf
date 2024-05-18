# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

import math
from ezdxf import loopfinder
from ezdxf.entities import Circle, Arc, Ellipse, LWPolyline, Spline
from ezdxf.math import fit_points_to_cad_cv, Vec2


def test_circle_is_a_closed_entity():
    circle = Circle()
    circle.dxf.radius = 1

    assert loopfinder.is_closed_entity(circle) is True


def test_circle_of_radius_0_is_not_a_closed_entity():
    circle = Circle()
    circle.dxf.radius = 0

    assert loopfinder.is_closed_entity(circle) is False


@pytest.mark.parametrize("start,end", [(0, 180), (0, 0), (180, 180), (360, 360)])
def test_open_arc_is_not_a_closed_entity(start, end):
    arc = Arc()
    arc.dxf.radius = 1
    arc.dxf.start_angle = start
    arc.dxf.end_angle = end

    assert loopfinder.is_closed_entity(arc) is False


@pytest.mark.parametrize("start,end", [(0, 360), (360, 0), (180, -180)])
def test_closed_arc_is_a_closed_entity(start, end):
    arc = Arc()
    arc.dxf.radius = 1
    arc.dxf.start_angle = start
    arc.dxf.end_angle = end

    assert loopfinder.is_closed_entity(arc) is True


@pytest.mark.parametrize(
    "start,end", [(0, math.pi), (0, 0), (math.pi, math.pi), (math.tau, math.tau)]
)
def test_open_ellipse_is_not_a_closed_entity(start, end):
    ellipse = Ellipse()
    ellipse.dxf.major_axis = (1, 0)
    ellipse.dxf.ratio = 1
    ellipse.dxf.start_param = start
    ellipse.dxf.end_param = end

    assert loopfinder.is_closed_entity(ellipse) is False


@pytest.mark.parametrize(
    "start,end", [(0, math.tau), (math.tau, 0), (math.pi, -math.pi)]
)
def test_closed_ellipse_is_a_closed_entity(start, end):
    ellipse = Ellipse()
    ellipse.dxf.major_axis = (1, 0)
    ellipse.dxf.ratio = 1
    ellipse.dxf.start_param = start
    ellipse.dxf.end_param = end

    assert loopfinder.is_closed_entity(ellipse) is True


# Note: Ellipses with major_axis == (0, 0, 0) are not valid.
# They cannot be created by ezdxf and loading such ellipses raises an DXFStructureError.


def test_closed_lwpolyline_is_a_closed_entity():
    polyline = LWPolyline()
    polyline.closed = True
    polyline.append_points([(0, 0), (10, 0), (10, 10)])

    assert loopfinder.is_closed_entity(polyline) is True


def test_open_lwpolyline_is_not_a_closed_entity():
    polyline = LWPolyline()
    polyline.closed = False
    polyline.append_points([(0, 0), (10, 0), (10, 10)])

    assert loopfinder.is_closed_entity(polyline) is False


def test_explicit_closed_lwpolyline_is_a_closed_entity():
    polyline = LWPolyline()
    polyline.closed = False
    polyline.append_points([(0, 0), (10, 0), (10, 10), (0, 0)])

    assert loopfinder.is_closed_entity(polyline) is True


def test_closed_spline():
    ct = fit_points_to_cad_cv([(0, 0), (10, 0), (10, 10), (0, 0)])
    spline = Spline()
    spline.apply_construction_tool(ct)

    assert loopfinder.is_closed_entity(spline) is True


def test_open_spline():
    ct = fit_points_to_cad_cv([(0, 0), (10, 0), (10, 10), (0, 10)])
    spline = Spline()
    spline.apply_construction_tool(ct)

    assert loopfinder.is_closed_entity(spline) is False


def test_empty_spline():
    spline = Spline()

    assert loopfinder.is_closed_entity(spline) is False


class TestEdge:
    def test_init(self):
        edge = loopfinder.Edge(Vec2(0, 0), Vec2(1, 0), 1.0)
        assert edge.start == Vec2(0, 0)
        assert edge.end == Vec2(1, 0)
        assert edge.length == 1.0
        assert edge.reverse is False
        assert edge.payload is None

    def test_identity(self):
        edge0 = loopfinder.Edge(Vec2(0, 0), Vec2(1, 0), 1.0)
        edge1 = loopfinder.Edge(Vec2(0, 0), Vec2(1, 0), 1.0)
        assert edge0 == edge0
        assert edge0 != edge1, "each edge should have an unique identity"
        assert edge0 == edge0.copy(), "copies represent the same edge"
        assert edge0 == edge0.reversed(), "reversed copies represent the same edge"

    def test_copy(self):
        edge = loopfinder.Edge(Vec2(0, 0), Vec2(1, 0), 1.0)
        clone = edge.copy()
        assert edge == clone
        assert edge.id == clone.id
        assert edge.start == clone.start
        assert edge.end == clone.end
        assert edge.length == clone.length
        assert edge.reverse is clone.reverse
        assert edge.payload is clone.payload

    def test_reversed_copy(self):
        edge = loopfinder.Edge(Vec2(0, 0), Vec2(1, 0), 1.0)
        clone = edge.reversed()
        assert edge == clone
        assert edge.id == clone.id
        assert edge.start == clone.end
        assert edge.end == clone.start
        assert edge.length == clone.length
        assert edge.reverse is (not clone.reverse)
        assert edge.payload is clone.payload


if __name__ == "__main__":
    pytest.main([__file__])
