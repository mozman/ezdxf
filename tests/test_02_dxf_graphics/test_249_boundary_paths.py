#  Copyright (c) 2021-2024, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec3
from ezdxf.entities import (
    BoundaryPaths,
    BoundaryPathType,
    EdgeType,
)


def test_add_polyline_path():
    paths = BoundaryPaths()
    new_path = paths.add_polyline_path([(0, 0), (0, 1), (1, 1), (1, 0)])
    assert new_path.type == BoundaryPathType.POLYLINE, "expected polyline path"
    assert 4 == len(new_path.vertices), "invalid vertex count"

    # now check the created entity
    assert 1 == len(paths)
    path = paths[0]
    assert path.type == BoundaryPathType.POLYLINE, "invalid path type"
    assert 4 == len(path.vertices), "invalid vertex count"
    # vertex format: x, y, bulge_value
    assert (0, 0, 0) == path.vertices[0], "invalid first vertex"
    assert (1, 0, 0) == path.vertices[3], "invalid last vertex"
    assert path.is_closed == 1


def test_add_edge_path():
    paths = BoundaryPaths()
    path = paths.add_edge_path()
    assert path.type == BoundaryPathType.EDGE, "expected edge path type"
    assert paths.has_edge_paths is True

    path.add_line((0, 0), (10, 0))
    path.add_arc((10, 5), radius=5, start_angle=270, end_angle=450, ccw=True)
    path.add_ellipse(
        (5, 10), major_axis=(5, 0), ratio=0.2, start_angle=0, end_angle=180
    )
    path.add_line((10, 0), (0, 0))
    # exit with statement and create DXF tags

    path = paths[-1]
    edge = path.edges[0]
    assert edge.type == EdgeType.LINE, "invalid edge type for 1. edge"
    assert (0, 0) == edge.start
    assert (10, 0) == edge.end

    edge = path.edges[1]
    assert edge.type == EdgeType.ARC, "invalid edge type for 2. edge"
    assert (10, 5) == edge.center
    assert 5 == edge.radius
    assert 270 == edge.start_angle
    assert 450 == edge.end_angle
    assert edge.ccw is True

    edge = path.edges[2]
    assert edge.type == EdgeType.ELLIPSE, "invalid edge type for 3. edge"
    assert (5, 10) == edge.center
    assert (5, 0) == edge.major_axis
    assert 0.2 == edge.ratio
    assert 0 == edge.start_angle
    assert 180 == edge.end_angle
    assert edge.ccw is True

    edge = path.edges[3]
    assert edge.type == EdgeType.LINE, "invalid edge type for 4. edge"
    assert (10, 0) == edge.start
    assert (0, 0) == edge.end


def test_polyline_path_with_arcs_to_edge_path():
    paths = BoundaryPaths()
    # <-- 2 ----
    #  \        \
    #   3 cw     1 ccw
    #  /        /
    # --- 0 --->
    paths.add_polyline_path([(0, 0), (10, 0, 1), (10, 4), (0, 4, -1), (0, 0)])
    paths.polyline_to_edge_paths()
    path = paths[0]
    assert (
        path.type == BoundaryPathType.EDGE
    ), "polyline path not converted to edge path"

    line = path.edges[0]
    assert line.type == EdgeType.LINE
    assert line.start == (0, 0)
    assert line.end == (10, 0)

    # counter-clockwise arc edge
    arc = path.edges[1]
    assert arc.type == EdgeType.ARC
    assert arc.center.isclose((10, 2))
    assert arc.start_angle == pytest.approx(270)
    assert arc.end_angle == pytest.approx(90)
    assert arc.ccw is True

    line = path.edges[2]
    assert line.type == EdgeType.LINE
    assert line.start == (10, 4)
    assert line.end == (0, 4)

    # clockwise arc edge
    arc = path.edges[3]
    assert arc.type == EdgeType.ARC
    assert arc.center.isclose((0, 2))
    # angles are in counter-clockwise order
    assert arc.start_angle == pytest.approx(270)
    assert arc.end_angle == pytest.approx(90)
    # but ccw flag forces clockwise DXF export
    assert arc.ccw is False


def test_arc_to_ellipse_edges():
    paths = BoundaryPaths()
    paths.add_polyline_path(
        [(0, 0, 1), (10, 0), (10, 10, -0.5), (0, 10)], is_closed=True
    )

    paths.polyline_to_edge_paths()
    path = paths[0]
    assert (
        path.type == BoundaryPathType.EDGE
    ), "polyline path not converted to edge path"

    paths.arc_edges_to_ellipse_edges()

    edge = path.edges[0]
    assert edge.type == EdgeType.ELLIPSE
    assert edge.center == (5, 0)
    assert edge.major_axis == (5, 0)
    assert edge.ratio == 1.0

    edge = path.edges[1]
    assert edge.type == EdgeType.LINE
    assert edge.start == (10, 0)
    assert edge.end == (10, 10)

    edge = path.edges[2]
    assert edge.type == EdgeType.ELLIPSE
    assert edge.ratio == 1.0

    edge = path.edges[3]
    assert edge.type == EdgeType.LINE
    assert edge.start == (0, 10)
    assert edge.end == (0, 0)


def test_ellipse_edges_to_spline_edges():
    paths = BoundaryPaths()
    paths.add_polyline_path(
        [(0, 0, 1), (10, 0), (10, 10, -0.5), (0, 10)], is_closed=True
    )
    paths.all_to_spline_edges(num=32)
    path = paths[0]

    edge = path.edges[0]
    assert edge.type == EdgeType.SPLINE
    assert edge.control_points[0].isclose((0, 0))
    assert edge.control_points[-1].isclose((10, 0))

    edge = path.edges[2]
    assert edge.type == EdgeType.SPLINE
    assert Vec3(10, 10).isclose(edge.control_points[0])
    assert Vec3(0, 10).isclose(edge.control_points[-1])


def add_edge_path(paths: BoundaryPaths):
    path = paths.add_edge_path()
    path.add_line((0, 0), (1, 0))
    path.add_line((1, 0), (1, 1))
    path.add_line((1, 1), (0, 1))
    path.add_line((0, 1), (0, 0))


def test_edge_to_polyline_paths():
    paths = BoundaryPaths()
    add_edge_path(paths)
    paths.edge_to_polyline_paths(distance=0.1)
    path = paths[0]
    assert path.type == BoundaryPathType.POLYLINE
    assert path.has_bulge() is False
    assert len(path.vertices) == 5


class TestValidatingBoundaryPaths:
    def test_spline_edge_has_valid_knot_count(self):
        paths = BoundaryPaths()
        edge_path = paths.add_edge_path()
        spline = edge_path.add_spline(
            control_points=[(0, 0), (1, 1), (2, 0), (3, 1)],
            knot_values=[1, 2, 3, 4, 5, 6, 7, 8],
        )
        assert spline.is_valid() is True, "expected degree + count + 1 values"

        spline.knot_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        assert spline.is_valid() is False, "too many knot value"
        spline.knot_values = [0, 0, 0, 0]
        assert spline.is_valid() is False, "too few knot value"

        assert paths.is_valid() is False, "invalid state should be propagated"

    def test_spline_edge_has_enough_control_points(self):
        paths = BoundaryPaths()
        edge_path = paths.add_edge_path()
        spline = edge_path.add_spline(
            control_points=[(0, 0), (1, 1), (2, 0)],
            knot_values=[1, 2, 3, 4, 5, 6, 7],  # correct degree + count + 1!
        )
        assert spline.is_valid() is False, "too few control points"

    def test_spline_edge_has_enough_fir_points(self):
        paths = BoundaryPaths()
        edge_path = paths.add_edge_path()
        spline = edge_path.add_spline(
            fit_points=[(0, 0), (1, 1), (2, 0)],
        )
        assert spline.is_valid() is True, "expected 2 or more points"
        spline.fit_points = [(0, 0)]
        assert spline.is_valid() is False, "too few fit points"


def test_real_start_point_of_arc_edge():
    paths = BoundaryPaths()
    edge_path = paths.add_edge_path()
    arc_edge = edge_path.add_arc(
        (1, 0), radius=1, start_angle=0, end_angle=180, ccw=True
    )
    assert arc_edge.real_start_point.isclose((2, 0))
    arc_edge = edge_path.add_arc(
        (1, 0), radius=1, start_angle=0, end_angle=180, ccw=False
    )
    assert arc_edge.real_start_point.isclose((0, 0))


def test_real_start_point_of_ellipse_edge():
    paths = BoundaryPaths()
    edge_path = paths.add_edge_path()
    arc_edge = edge_path.add_ellipse(
        (1, 0), major_axis=(1, 0), ratio=1, start_angle=0, end_angle=180, ccw=True
    )
    assert arc_edge.real_start_point.isclose((2, 0))
    arc_edge = edge_path.add_ellipse(
        (1, 0), major_axis=(1, 0), ratio=1, start_angle=0, end_angle=180, ccw=False
    )
    assert arc_edge.real_start_point.isclose((0, 0))


def test_real_end_point_of_arc_edge():
    paths = BoundaryPaths()
    edge_path = paths.add_edge_path()
    arc_edge = edge_path.add_arc(
        (1, 0), radius=1, start_angle=0, end_angle=180, ccw=True
    )
    assert arc_edge.real_end_point.isclose((0, 0))
    arc_edge = edge_path.add_arc(
        (1, 0), radius=1, start_angle=0, end_angle=180, ccw=False
    )
    assert arc_edge.real_end_point.isclose((2, 0))


def test_real_end_point_of_ellipse_edge():
    paths = BoundaryPaths()
    edge_path = paths.add_edge_path()
    arc_edge = edge_path.add_ellipse(
        (1, 0), major_axis=(1, 0), ratio=1, start_angle=0, end_angle=180, ccw=True
    )
    assert arc_edge.real_end_point.isclose((0, 0))
    arc_edge = edge_path.add_ellipse(
        (1, 0), major_axis=(1, 0), ratio=1, start_angle=0, end_angle=180, ccw=False
    )
    assert arc_edge.real_end_point.isclose((2, 0))


class TestCloseGapsOfEdgePaths:
    def test_gap_between_line_edges(self):
        paths = BoundaryPaths()
        edge_path = paths.add_edge_path()
        edge_path.add_line((0, 0), (1, 0))
        edge_path.add_line((1.1, 0), (1, 1))
        edge_path.add_line((1, 1), (0, 0))
        edge_path.close_gaps(0.01)
        assert len(edge_path.edges) == 4

    def test_gap_between_last_and_first_line(self):
        paths = BoundaryPaths()
        edge_path = paths.add_edge_path()
        edge_path.add_line((0, 0), (1, 0))
        edge_path.add_line((1, 0), (1, 1))
        edge_path.add_line((1, 1), (0, 0.1))
        edge_path.close_gaps(0.01)
        assert len(edge_path.edges) == 4

    def test_gap_between_arc_and_line_ccw(self):
        paths = BoundaryPaths()
        edge_path = paths.add_edge_path()
        edge_path.add_arc((1, 0), radius=1, start_angle=0, end_angle=180)
        edge_path.add_line((0, 0), (1.9, 0))
        edge_path.close_gaps(0.01)
        assert len(edge_path.edges) == 3

    def test_gap_between_arc_and_line_cw(self):
        paths = BoundaryPaths()
        edge_path = paths.add_edge_path()
        edge_path.add_arc((1, 0), radius=1, start_angle=0, end_angle=180, ccw=False)
        edge_path.add_line((1.9, 0), (0, 0))
        edge_path.close_gaps(0.01)
        assert len(edge_path.edges) == 3

    def test_gap_between_ellipse_and_line_ccw(self):
        paths = BoundaryPaths()
        edge_path = paths.add_edge_path()
        edge_path.add_ellipse(
            (1, 0), major_axis=(1, 0), ratio=1, start_angle=0, end_angle=180
        )
        edge_path.add_line((0, 0), (1.9, 0))
        edge_path.close_gaps(0.01)
        assert len(edge_path.edges) == 3

    def test_gap_between_ellipse_and_line_cw(self):
        paths = BoundaryPaths()
        edge_path = paths.add_edge_path()
        edge_path.add_ellipse(
            (1, 0), major_axis=(1, 0), ratio=1, start_angle=0, end_angle=180, ccw=False
        )
        edge_path.add_line((1.9, 0), (0, 0))
        edge_path.close_gaps(0.01)
        assert len(edge_path.edges) == 3


if __name__ == "__main__":
    pytest.main([__file__])
