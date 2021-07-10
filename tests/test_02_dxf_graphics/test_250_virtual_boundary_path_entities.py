#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
import math

from ezdxf.explode import virtual_boundary_path_entities
from ezdxf.entities import Spline
from ezdxf.math import Vec3


class TestVirtualEntitiesFromEdgePath:
    # fixture "all_edge_types_hatch" from conftest.py
    @pytest.fixture
    def paths(self, all_edge_types_hatch):
        return virtual_boundary_path_entities(all_edge_types_hatch)

    @pytest.fixture
    def spline(self, paths) -> Spline:
        return cast(Spline, paths[0][5])

    def test_returns_one_path(self, paths):
        assert len(paths) == 1

    def test_path_has_six_entities(self, paths):
        assert len(paths[0]) == 6

    def test_expected_entity_types(self, paths):
        types = [e.dxftype() for e in paths[0]]
        assert types == ["ARC", "ELLIPSE", "LINE", "ELLIPSE", "ARC", "SPLINE"]

    def test_arc_0_parameters(self, paths):
        # source edge is a clockwise oriented ArcEdge
        arc_0 = paths[0][0]
        assert arc_0.dxf.center.isclose((0, 13))
        assert arc_0.dxf.radius == pytest.approx(3)
        # ARC entity is always counter-clockwise oriented
        assert arc_0.dxf.start_angle == pytest.approx(-90)
        assert arc_0.dxf.end_angle == pytest.approx(90)

    def test_ellipse_1_parameters(self, paths):
        # source edge is a clockwise oriented EllipseEdge
        ellipse_1 = paths[0][1]
        assert ellipse_1.dxf.center.isclose((0, 5))
        assert ellipse_1.dxf.major_axis.isclose((0, 5))
        assert ellipse_1.dxf.ratio == pytest.approx(0.6)
        # EllipseEdge angles in degrees - ELLIPSE entity params in radians!
        # ELLIPSE entity is always counter-clockwise oriented
        assert ellipse_1.dxf.start_param == pytest.approx(math.radians(180))
        assert ellipse_1.dxf.end_param == pytest.approx(math.radians(360))

    def test_line_parameters(self, paths):
        # source edge is a LineEdge
        line = paths[0][2]
        assert line.dxf.start.isclose((0, 0))
        assert line.dxf.end.isclose((10, 0))

    def test_ellipse_3_parameters(self, paths):
        # source edge is a counter-clockwise oriented EllipseEdge
        ellipse_3 = paths[0][3]
        assert ellipse_3.dxf.center.isclose((10, 5))
        assert ellipse_3.dxf.major_axis.isclose((0, -5))
        assert ellipse_3.dxf.ratio == pytest.approx(0.6)
        # EllipseEdge angles in degrees - ELLIPSE entity params in radians!
        # ELLIPSE entity is always counter-clockwise oriented
        assert ellipse_3.dxf.start_param == pytest.approx(0)
        assert ellipse_3.dxf.end_param == pytest.approx(math.radians(180))

    def test_arc_4_parameters(self, paths):
        # source edge is a counter-clockwise oriented ArcEdge
        arc_4 = paths[0][4]
        assert arc_4.dxf.center.isclose((10, 13))
        assert arc_4.dxf.radius == pytest.approx(3)
        # ARC entity is always counter-clockwise oriented
        assert arc_4.dxf.start_angle == pytest.approx(270)
        assert arc_4.dxf.end_angle == pytest.approx(450)

    def test_spline_parameters(self, spline):
        # source edge is a SplineEdge
        assert spline.dxf.degree == 3
        assert len(spline.control_points) == 6
        assert len(spline.knots) == 10
        assert len(spline.weights) == 0

    def test_spline_control_points(self, spline):
        expected_control_points = [
            Vec3(10.0, 16.0),
            Vec3(9.028174684192452, 16.0),
            Vec3(6.824943218065775, 12.14285714285714),
            Vec3(3.175056781934232, 19.85714285714287),
            Vec3(0.9718253158075516, 16.0),
            Vec3(0, 16.0),
        ]
        assert (
            all(
                expected_cp.isclose(cp)
                for cp, expected_cp in zip(
                    spline.control_points, expected_control_points
                )
            )
            is True
        )

    def test_spline_knots(self, spline):
        expected_knot_values = [
            0.0,
            0.0,
            0.0,
            0.0,
            2.91547594742265,
            8.746427842267952,
            11.6619037896906,
            11.6619037896906,
            11.6619037896906,
            11.6619037896906,
        ]
        assert spline.knots == pytest.approx(expected_knot_values)


if __name__ == "__main__":
    pytest.main([__file__])
