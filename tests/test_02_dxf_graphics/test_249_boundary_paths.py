#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec3
from ezdxf.entities import BoundaryPaths, BoundaryPathType, EdgeType


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


if __name__ == "__main__":
    pytest.main([__file__])
