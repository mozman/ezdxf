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


@pytest.mark.parametrize(
    "sx, sy",
    [(-1, 1), (1, -1), (-1, -1)],
    ids=["mirror-x", "mirror-y", "mirror-xy"],
)
def test_wcs_mirror_transformations_for_all_edge_types(
    sx, sy, all_edge_types_hatch
):
    hatch = all_edge_types_hatch
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


def test_pattern_scale_and_angle_transform_preserves_geometry():
    """Transform a hatch with pattern fill and verify that base_point and offset
    are only rotated+scaled (not translated) and that scale/angle DXF attrs
    are correctly updated.
    """
    hatch = Hatch.new()
    hatch.set_pattern_fill("ANSI31", angle=0, scale=1.0)
    # The predefined ANSI31 definition loaded above contains a single pattern
    # line. Capture the original pattern state.
    line = hatch.pattern.lines[0]
    # ANSI31 pattern line has base_angle=45°; capture before transform.
    orig_line_angle = line.angle

    # Apply a rotation of 45° around the z-axis (no translation).
    m = Matrix44.z_rotate(math.radians(45))
    hatch.transform(m)

    # DXF angle should reflect the OCS rotation.
    assert hatch.dxf.pattern_angle == pytest.approx(45.0)

    # pattern_scale should be multiplied by the x-axis length scale factor.
    # For pure rotation there is no scale change (factor == 1).
    assert hatch.dxf.pattern_scale == pytest.approx(1.0)

    # The line's stored angle should be the original plus the OCS rotation.
    assert line.angle == pytest.approx((orig_line_angle + 45.0) % 360.0)

    # After the rotation the offset should still be a pure direction (no
    # translation applied). With no additional scale the magnitude must be
    # unchanged.
    assert Vec2(line.offset).magnitude == pytest.approx(
        Vec2(line.offset).magnitude, abs=1e-9
    )
    # The offset should also be rotated by 45° relative to its previous
    # direction (up to sign ambiguity when the rotation axis flips).
    prev = Vec2(line.offset)
    # Re-apply the inverse to verify round-trip consistency.
    inv = Matrix44.z_rotate(math.radians(-45))
    recovered = Vec2(inv.transform_direction((line.offset[0], line.offset[1], 0)))
    assert recovered.isclose(Vec2(-2.2450640303, 2.2450640303), abs_tol=1e-6)


def test_pattern_transform_with_translation_does_not_shift_base_point():
    """Translation component of the matrix must not affect the magnitude of
    base_point or offset — they are direction vectors, not positions.
    """
    hatch = Hatch.new()
    hatch.set_pattern_fill("ANSI31", angle=0, scale=1.0)
    line = hatch.pattern.lines[0]
    orig_base_mag = Vec2(line.base_point).magnitude
    orig_offset_mag = Vec2(line.offset).magnitude

    # Matrix includes a large translation; direction vectors should be unchanged
    # in magnitude, only the angle should change.
    m = Matrix44.chain(
        Matrix44.z_rotate(math.radians(90)),
        Matrix44.translate(1000, 2000, 0),
    )
    hatch.transform(m)

    # base_point/offset magnitude must not drift by the translation.
    assert Vec2(line.base_point).magnitude == pytest.approx(orig_base_mag, abs=1e-9)
    assert Vec2(line.offset).magnitude == pytest.approx(orig_offset_mag, abs=1e-9)

    # The DXF pattern_angle should be 90.
    assert hatch.dxf.pattern_angle == pytest.approx(90.0)


def test_pattern_transform_with_scale_updates_scale_and_geometry():
    """With non-unit scale, pattern_scale DXF attr should be multiplied by the
    x-axis length scale and the base_point/offset magnitudes should follow.
    """
    hatch = Hatch.new()
    hatch.set_pattern_fill("ANSI31", angle=0, scale=1.0)
    line = hatch.pattern.lines[0]
    orig_base_len = Vec2(line.base_point).magnitude
    orig_offset_len = Vec2(line.offset).magnitude

    m = Matrix44.scale(2, 2, 1)
    hatch.transform(m)

    assert hatch.dxf.pattern_scale == pytest.approx(2.0)

    new_base_len = Vec2(line.base_point).magnitude
    new_offset_len = Vec2(line.offset).magnitude
    # Allow a loose tolerance because the ANSI31 base_point/offset are
    # non-zero and can drift due to OCS↔WCS round-trip.
    assert new_base_len == pytest.approx(orig_base_len * 2, abs=1e-9)
    assert new_offset_len == pytest.approx(orig_offset_len * 2, abs=1e-9)


def test_pattern_transform_combined_rotation_and_scale():
    hatch = Hatch.new()
    hatch.set_pattern_fill("ANSI31", angle=0, scale=1.0)
    line = hatch.pattern.lines[0]
    orig_line_angle = line.angle  # ANSI31 default is 45°

    m = Matrix44.chain(
        Matrix44.z_rotate(math.radians(30)),
        Matrix44.scale(2, 2, 1),
    )
    hatch.transform(m)

    assert hatch.dxf.pattern_angle == pytest.approx(30.0)
    assert hatch.dxf.pattern_scale == pytest.approx(2.0)
    assert line.angle == pytest.approx((orig_line_angle + 30.0) % 360.0)
