# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
import pytest

import math
from ezdxf.math import (
    ConstructionEllipse, cubic_bezier_interpolation, cubic_bezier_from_arc,
    cubic_bezier_from_ellipse,
)
from ezdxf.math.bezier4p import cubic_bezier_arc_parameters


def test_cubic_bezier_arc_parameters_computation():
    parts = list(cubic_bezier_arc_parameters(0, math.tau))
    assert len(parts) == 4

    chk = 4.0 * (math.sqrt(2) - 1.0) / 3.0
    sp, cp1, cp2, ep = parts[0]
    assert sp.isclose((1, 0))
    assert cp1.isclose((1, chk))
    assert cp2.isclose((chk, 1))
    assert ep.isclose((0, 1))

    sp, cp1, cp2, ep = parts[1]
    assert sp.isclose((0, 1))
    assert cp1.isclose((-chk, 1))
    assert cp2.isclose((-1, chk))
    assert ep.isclose((-1, 0))

    sp, cp1, cp2, ep = parts[2]
    assert sp.isclose((-1, 0))
    assert cp1.isclose((-1, -chk))
    assert cp2.isclose((-chk, -1))
    assert ep.isclose((0, -1))

    sp, cp1, cp2, ep = parts[3]
    assert sp.isclose((0, -1))
    assert cp1.isclose((chk, -1))
    assert cp2.isclose((1, -chk))
    assert ep.isclose((1, 0))


def test_vertex_interpolation():
    points = [(0, 0), (3, 1), (5, 3), (0, 8)]
    result = list(cubic_bezier_interpolation(points))
    assert len(result) == 3
    c1, c2, c3 = result
    p = c1.control_points
    assert p[0].isclose((0, 0))
    assert p[1].isclose((0.9333333333333331, 0.3111111111111111))
    assert p[2].isclose((1.8666666666666663, 0.6222222222222222))
    assert p[3].isclose((3, 1))

    p = c2.control_points
    assert p[0].isclose((3, 1))
    assert p[1].isclose((4.133333333333334, 1.3777777777777778))
    assert p[2].isclose((5.466666666666667, 1.822222222222222))
    assert p[3].isclose((5, 3))

    p = c3.control_points
    assert p[0].isclose((5, 3))
    assert p[1].isclose((4.533333333333333, 4.177777777777778))
    assert p[2].isclose((2.2666666666666666, 6.088888888888889))
    assert p[3].isclose((0, 8))


def test_from_circular_arc():
    curves = list(cubic_bezier_from_arc(end_angle=90))
    assert len(curves) == 1

    bezier4p = curves[0]
    cpoints = bezier4p.control_points
    assert len(cpoints) == 4
    assert cpoints[0].isclose((1, 0, 0))
    assert cpoints[1].isclose((1.0, 0.5522847498307933, 0.0))
    assert cpoints[2].isclose((0.5522847498307935, 1.0, 0.0))
    assert cpoints[3].isclose((0, 1, 0))


def test_rational_spline_from_simple_elliptic_arc():
    ellipse = ConstructionEllipse(
        center=(1, 1),
        major_axis=(2, 0),
        ratio=0.5,
        start_param=0,
        end_param=math.pi / 2,
    )
    curves = list(cubic_bezier_from_ellipse(ellipse))
    assert len(curves) == 1

    p1, p2, p3, p4 = curves[0].control_points
    assert p1.isclose((3, 1, 0))
    assert p2.isclose((3.0, 1.5522847498307932, 0))
    assert p3.isclose((2.104569499661587, 2.0, 0))
    assert p4.isclose((1, 2, 0))


def test_rational_spline_from_complex_elliptic_arc():
    ellipse = ConstructionEllipse(
        center=(49.64089977339618, 36.43095770602131, 0.0),
        major_axis=(16.69099826506408, 6.96203799241026, 0.0),
        ratio=0.173450304570581,
        start_param=5.427509144462117,
        end_param=7.927025930557775,
    )
    curves = list(cubic_bezier_from_ellipse(ellipse))

    assert curves[0].control_points[0].isclose(ellipse.start_point)
    assert curves[1].control_points[-1].isclose(ellipse.end_point)
