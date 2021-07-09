# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import pytest
import math

from ezdxf.entities import Hatch
from ezdxf.render.forms import box
from ezdxf.math import Vec2, Vec3, Matrix44, arc_angle_span_deg
from ezdxf.path import make_path, have_close_control_vertices


@pytest.fixture()
def m44():
    return Matrix44.chain(
        Matrix44.z_rotate(math.pi / 2),
        Matrix44.translate(1, 2, 0),
    )


def test_polyline_path_transform_interface(m44):
    hatch = Hatch.new()
    vertices = list(box(1.0, 2.0))
    path = hatch.paths.add_polyline_path(vertices)

    hatch.transform(m44)
    chk = m44.transform_vertices(vertices)
    for v, c in zip(path.vertices, chk):
        assert c.isclose(v)


def test_edge_path_transform_interface(m44):
    hatch = Hatch.new()
    path = hatch.paths.add_edge_path()
    path.add_line((0, 0), (10, 0))
    path.add_arc((10, 5), radius=5, start_angle=270, end_angle=450, ccw=1)
    path.add_ellipse(
        (5, 10), major_axis=(5, 0), ratio=0.2, start_angle=0, end_angle=180
    )
    spline = path.add_spline(
        [(1, 1), (2, 2), (3, 3), (4, 4)], degree=3, periodic=1
    )
    # the following values do not represent a mathematically valid spline
    spline.control_points = [(1, 1), (2, 2), (3, 3), (4, 4)]
    spline.knot_values = [1, 2, 3, 4, 5, 6]
    spline.weights = [4, 3, 2, 1]
    spline.start_tangent = (10, 1)
    spline.end_tangent = (2, 20)

    chk = list(
        m44.transform_vertices(
            [
                Vec3(0, 0),
                Vec3(10, 0),
                Vec3(10, 5),
                Vec3(5, 10),
                Vec3(1, 1),
                Vec3(2, 2),
                Vec3(3, 3),
                Vec3(4, 4),
            ]
        )
    )

    hatch.transform(m44)
    line = path.edges[0]
    assert chk[0].isclose(line.start)
    assert chk[1].isclose(line.end)
    arc = path.edges[1]
    assert chk[2].isclose(arc.center)
    ellipse = path.edges[2]
    assert chk[3].isclose(ellipse.center)
    spline = path.edges[3]
    for c, v in zip(chk[4:], spline.control_points):
        assert c.isclose(v)
    for c, v in zip(chk[4:], spline.fit_points):
        assert c.isclose(v)
    assert m44.transform_direction((10, 1, 0)).isclose(spline.start_tangent)
    assert m44.transform_direction((2, 20, 0)).isclose(spline.end_tangent)


@pytest.fixture(params=["arc", "ellipse"])
def closed_edge_hatch(request):
    _hatch = Hatch.new()
    _path = _hatch.paths.add_edge_path()
    if request.param == "arc":
        _path.add_arc((0, 0), radius=1, start_angle=0, end_angle=360, ccw=1)
    elif request.param == "ellipse":
        _path.add_ellipse(
            (0, 0), major_axis=(5, 0), ratio=0.2, start_angle=0, end_angle=360
        )
    return _hatch


def test_full_circle_ellipse_edge_rotation(closed_edge_hatch):
    edge = closed_edge_hatch.paths[0].edges[0]
    assert arc_angle_span_deg(
        edge.start_angle, edge.end_angle
    ) == pytest.approx(360)

    closed_edge_hatch.transform(Matrix44.z_rotate(math.radians(30)))
    edge2 = closed_edge_hatch.paths[0].edges[0]
    assert arc_angle_span_deg(
        edge2.start_angle, edge2.end_angle
    ) == pytest.approx(360)


def test_full_circle_edge_scaling():
    _hatch = Hatch.new()
    _path = _hatch.paths.add_edge_path()
    _arc = _path.add_arc((0, 0), radius=1, start_angle=0, end_angle=360, ccw=1)
    _hatch.transform(Matrix44.scale(0.5, 0.5, 0.5))
    assert _arc.radius == pytest.approx(0.5)


def transformed_copy(entity, matrix):
    _copy = entity.copy()
    _copy.transform(matrix)
    return _copy


@pytest.mark.parametrize(
    "sx, sy, extrusion",
    [
        (-1, 1, (0, 0, -1)),
        (1, -1, (0, 0, -1)),
        (-1, -1, (0, 0, 1)),
    ],
    ids=["mirror-x", "mirror-y", "mirror-xy"],
)
@pytest.mark.parametrize("kind", ["arc", "ellipse"])
def test_ocs_mirror_transformations_of_clockwise_oriented_curves(
    sx,
    sy,
    extrusion,
    kind,
):
    hatch = Hatch()
    edge_path = hatch.paths.add_edge_path()
    if kind == "arc":
        edge_path.add_arc((7, 0), 5, start_angle=0, end_angle=180, ccw=False)
    elif kind == "ellipse":
        edge_path.add_ellipse(
            (7, 0), (5, 0), ratio=0.7, start_angle=0, end_angle=180, ccw=False
        )
    else:
        pytest.fail(f"unknown kind: {kind}")

    transformed_hatch = transformed_copy(hatch, Matrix44.scale(sx, sy, 1))

    # This tests the current implementation of OCS transformations!
    assert transformed_hatch.dxf.extrusion.isclose(extrusion)
    assert (
        transformed_hatch.paths[0].edges[0].ccw is False
    ), "ccw flag should not change"


@pytest.mark.parametrize(
    "sx, sy",
    [(-1, 1), (1, -1), (-1, -1)],
    ids=["mirror-x", "mirror-y", "mirror-xy"],
)
@pytest.mark.parametrize("kind", ["arc", "ellipse"])
def test_wcs_mirror_transformations_of_clockwise_oriented_curves(sx, sy, kind):
    hatch = Hatch()
    edge_path = hatch.paths.add_edge_path()
    # A closed loop is required to get a path!
    edge_path.add_line((15, 5), (5, 5))
    if kind == "arc":
        edge_path.add_arc((10, 5), 5, start_angle=0, end_angle=180, ccw=False)
    elif kind == "ellipse":
        edge_path.add_ellipse(
            (10, 5), (5, 0), ratio=0.7, start_angle=0, end_angle=180, ccw=False
        )
    else:
        pytest.fail(f"unknown kind: {kind}")
    src_path = make_path(hatch)
    assert len(src_path) > 1, "expected non empty path"

    m = Matrix44.scale(sx, sy, 1)
    transformed_hatch = transformed_copy(hatch, m)

    expected_path = src_path.transform(m)
    path_of_transformed_hatch = make_path(transformed_hatch)
    assert (
        have_close_control_vertices(path_of_transformed_hatch, expected_path)
        is True
    )


def all_edge_types_hatch():
    hatch = Hatch.new(
        dxfattribs={
            "layer": "0",
            "color": "2",
            "elevation": (0.0, 0.0, 0.0),
            "extrusion": (0.0, 0.0, 1.0),
            "pattern_name": "SOLID",
            "solid_fill": 1,
            "associative": 0,
            "hatch_style": 0,
            "pattern_type": 1,
        },
    )
    # edge-path contains all supported edge types:
    ep = hatch.paths.add_edge_path(flags=1)
    ep.add_arc(  # clockwise oriented ARC
        center=(0.0, 13.0),
        radius=3.0,
        start_angle=-90.0,
        end_angle=90.0,
        ccw=False,
    )
    ep.add_ellipse(  # clockwise oriented ELLIPSE
        center=(0.0, 5.0),
        major_axis=(0.0, 5.0),
        ratio=0.6,
        start_angle=180.0,
        end_angle=360.0,
        ccw=False,
    )
    ep.add_line((0.0, 0.0), (10.0, 0.0))  # LINE
    ep.add_ellipse(  # counter-clockwise oriented ELLIPSE
        center=(10.0, 5.0),
        major_axis=(0.0, -5.0),
        ratio=0.6,
        start_angle=0.0,
        end_angle=180.0,
        ccw=True,
    )
    ep.add_arc(  # counter-clockwise oriented ARC
        center=(10.0, 13.0),
        radius=3.0,
        start_angle=270.0,
        end_angle=450.0,
        ccw=True,
    )
    ep.add_spline(  # SPLINE
        control_points=[
            Vec2(10.0, 16.0),
            Vec2(9.028174684192452, 16.0),
            Vec2(6.824943218065775, 12.14285714285714),
            Vec2(3.175056781934232, 19.85714285714287),
            Vec2(0.9718253158075516, 16.0),
            Vec2(0, 16.0),
        ],
        knot_values=[
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
        ],
        degree=3,
        periodic=0,
    )
    return hatch


@pytest.mark.parametrize(
    "sx, sy",
    [(-1, 1), (1, -1), (-1, -1)],
    ids=["mirror-x", "mirror-y", "mirror-xy"],
)
def test_wcs_mirror_transformations_for_all_edge_types(sx, sy):
    hatch = all_edge_types_hatch()
    src_path = make_path(hatch)
    assert len(src_path) > 1, "expected non empty path"

    m = Matrix44.scale(sx, sy, 1)
    transformed_hatch = transformed_copy(hatch, m)

    expected_path = src_path.transform(m)
    path_of_transformed_hatch = make_path(transformed_hatch)
    assert (
        have_close_control_vertices(path_of_transformed_hatch, expected_path)
        is True
    )
