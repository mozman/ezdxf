# Copyright (c) , Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pytest

import math
from ezdxf import loopgen
from ezdxf.entities import Circle, Arc, Ellipse, LWPolyline, Spline
from ezdxf.math import fit_points_to_cad_cv


def test_circle_is_a_closed_entity():
    circle = Circle()
    circle.dxf.radius = 1

    assert loopgen.is_closed_entity(circle) is True


def test_circle_of_radius_0_is_not_a_closed_entity():
    circle = Circle()
    circle.dxf.radius = 0

    assert loopgen.is_closed_entity(circle) is False


@pytest.mark.parametrize("start,end", [(0, 180), (0, 0), (180, 180), (360, 360)])
def test_open_arc_is_not_a_closed_entity(start, end):
    arc = Arc()
    arc.dxf.radius = 1
    arc.dxf.start_angle = start
    arc.dxf.end_angle = end

    assert loopgen.is_closed_entity(arc) is False


@pytest.mark.parametrize("start,end", [(0, 360), (360, 0), (180, -180)])
def test_closed_arc_is_a_closed_entity(start, end):
    arc = Arc()
    arc.dxf.radius = 1
    arc.dxf.start_angle = start
    arc.dxf.end_angle = end

    assert loopgen.is_closed_entity(arc) is True


@pytest.mark.parametrize(
    "start,end", [(0, math.pi), (0, 0), (math.pi, math.pi), (math.tau, math.tau)]
)
def test_open_ellipse_is_not_a_closed_entity(start, end):
    ellipse = Ellipse()
    ellipse.dxf.major_axis = (1, 0)
    ellipse.dxf.ratio = 1
    ellipse.dxf.start_param = start
    ellipse.dxf.end_param = end

    assert loopgen.is_closed_entity(ellipse) is False


@pytest.mark.parametrize(
    "start,end", [(0, math.tau), (math.tau, 0), (math.pi, -math.pi)]
)
def test_closed_ellipse_is_a_closed_entity(start, end):
    ellipse = Ellipse()
    ellipse.dxf.major_axis = (1, 0)
    ellipse.dxf.ratio = 1
    ellipse.dxf.start_param = start
    ellipse.dxf.end_param = end

    assert loopgen.is_closed_entity(ellipse) is True


# Note: Ellipses with major_axis == (0, 0, 0) are not valid.
# They cannot be created by ezdxf and loading such ellipses raises an DXFStructureError.


def test_closed_lwpolyline_is_a_closed_entity():
    polyline = LWPolyline()
    polyline.closed = True
    polyline.append_points([(0, 0), (10, 0), (10, 10)])

    assert loopgen.is_closed_entity(polyline) is True


def test_open_lwpolyline_is_not_a_closed_entity():
    polyline = LWPolyline()
    polyline.closed = False
    polyline.append_points([(0, 0), (10, 0), (10, 10)])

    assert loopgen.is_closed_entity(polyline) is False


def test_explicit_closed_lwpolyline_is_a_closed_entity():
    polyline = LWPolyline()
    polyline.closed = False
    polyline.append_points([(0, 0), (10, 0), (10, 10), (0, 0)])

    assert loopgen.is_closed_entity(polyline) is True


def test_closed_spline():
    ct = fit_points_to_cad_cv([(0, 0), (10, 0), (10, 10), (0, 0)])
    spline = Spline()
    spline.apply_construction_tool(ct)

    assert loopgen.is_closed_entity(spline) is True


def test_open_spline():
    ct = fit_points_to_cad_cv([(0, 0), (10, 0), (10, 10), (0, 10)])
    spline = Spline()
    spline.apply_construction_tool(ct)

    assert loopgen.is_closed_entity(spline) is False


def test_empty_spline():
    spline = Spline()

    assert loopgen.is_closed_entity(spline) is False


if __name__ == "__main__":
    pytest.main([__file__])
