#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
import math

from ezdxf.explode import virtual_boundary_path_entities
from ezdxf.entities import Spline
from ezdxf.math import Vec3, Matrix44, OCSTransform


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


class TestSpatialTransformation:
    # fixture "all_edge_types_hatch" from conftest.py
    @pytest.fixture(scope="class")
    def matrix(self):
        return Matrix44.y_rotate(math.radians(-90))

    @pytest.fixture
    def paths(self, all_edge_types_hatch, matrix):
        all_edge_types_hatch.transform(matrix)
        return virtual_boundary_path_entities(all_edge_types_hatch)

    @pytest.fixture
    def spline(self, paths) -> Spline:
        return cast(Spline, paths[0][5])

    def test_wcs_line(self, paths, matrix):
        line = paths[0][2]
        assert line.dxf.start.isclose(matrix.transform((0, 0)))
        assert line.dxf.end.isclose(matrix.transform((10, 0)))

    def test_wcs_spline(self, spline, matrix):
        expected_control_points = matrix.transform_vertices(
            [
                Vec3(10.0, 16.0),
                Vec3(9.028174684192452, 16.0),
                Vec3(6.824943218065775, 12.14285714285714),
                Vec3(3.175056781934232, 19.85714285714287),
                Vec3(0.9718253158075516, 16.0),
                Vec3(0, 16.0),
            ]
        )
        assert (
            all(
                expected_cp.isclose(cp)
                for cp, expected_cp in zip(
                    spline.control_points, expected_control_points
                )
            )
            is True
        )

    def test_ocs_clockwise_arc(self, paths, matrix):
        arc = paths[0][0]
        ocs_transform = OCSTransform(Vec3(0, 0, 1), matrix)

        wcs_center = ocs_transform.new_ocs.to_wcs(arc.dxf.center)
        assert wcs_center.isclose(matrix.transform((0, 13)))

        expected_start_angle = ocs_transform.transform_deg_angle(-90)
        assert arc.dxf.start_angle == pytest.approx(expected_start_angle)

        expected_end_angle = ocs_transform.transform_deg_angle(90)
        assert arc.dxf.end_angle == pytest.approx(expected_end_angle)

    def test_ocs_counter_clockwise_arc(self, paths, matrix):
        arc = paths[0][4]
        ocs_transform = OCSTransform(Vec3(0, 0, 1), matrix)

        wcs_center = ocs_transform.new_ocs.to_wcs(arc.dxf.center)
        assert wcs_center.isclose(matrix.transform((10, 13)))

        expected_start_angle = ocs_transform.transform_deg_angle(270)
        assert arc.dxf.start_angle == pytest.approx(expected_start_angle)

        expected_end_angle = ocs_transform.transform_deg_angle(450)
        assert arc.dxf.end_angle == pytest.approx(expected_end_angle)

    def test_wcs_clockwise_ellipse(self, paths, matrix):
        ellipse = paths[0][1]
        assert ellipse.dxf.center.isclose(matrix.transform((0, 5)))
        assert ellipse.dxf.major_axis.isclose(
            matrix.transform_direction((0, 5))
        )
        # ellipse normal vector
        assert ellipse.dxf.extrusion.isclose(
            matrix.transform_direction((0, 0, 1))
        )
        # only the center and the major axis are transformed:
        assert ellipse.dxf.start_param == pytest.approx(math.radians(180))
        assert ellipse.dxf.end_param == pytest.approx(math.radians(360))

    def test_wcs_counter_clockwise_ellipse(self, paths, matrix):
        ellipse = paths[0][3]
        assert ellipse.dxf.center.isclose(matrix.transform((10, 5)))
        assert ellipse.dxf.major_axis.isclose(
            matrix.transform_direction((0, -5))
        )
        # ellipse normal vector
        assert ellipse.dxf.extrusion.isclose(
            matrix.transform_direction((0, 0, 1))
        )
        # only the center and the major axis are transformed:
        assert ellipse.dxf.start_param == pytest.approx(math.radians(0))
        assert ellipse.dxf.end_param == pytest.approx(math.radians(180))


if __name__ == "__main__":
    pytest.main([__file__])
