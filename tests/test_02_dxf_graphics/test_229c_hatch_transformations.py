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
    spline = path.add_spline([(1, 1), (2, 2), (3, 3), (4, 4)], degree=3, periodic=1)
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
    assert arc_angle_span_deg(edge.start_angle, edge.end_angle) == pytest.approx(360)

    closed_edge_hatch.transform(Matrix44.z_rotate(math.radians(30)))
    edge2 = closed_edge_hatch.paths[0].edges[0]
    assert arc_angle_span_deg(edge2.start_angle, edge2.end_angle) == pytest.approx(360)


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
    assert have_close_control_vertices(path_of_transformed_hatch, expected_path) is True


@pytest.mark.parametrize(
    "sx, sy",
    [(-1, 1), (1, -1), (-1, -1)],
    ids=["mirror-x", "mirror-y", "mirror-xy"],
)
def test_wcs_mirror_transformations_for_all_edge_types(sx, sy, all_edge_types_hatch):
    hatch = all_edge_types_hatch
    src_path = make_path(hatch)
    assert len(src_path) > 1, "expected non empty path"

    m = Matrix44.scale(sx, sy, 1)
    transformed_hatch = transformed_copy(hatch, m)

    expected_path = src_path.transform(m)
    path_of_transformed_hatch = make_path(transformed_hatch)
    assert have_close_control_vertices(path_of_transformed_hatch, expected_path) is True


def test_hatch_pattern_angle_after_hatch_rotation_has_new_absolute_angle():
    hatch = Hatch()
    hatch.paths.add_polyline_path([(0, 0), (10, 0), (10, 10), (0, 10)])
    hatch.set_pattern_fill("ANSI31", scale=1.0, angle=30.0)

    assert hatch.dxf.pattern_angle == 30
    hatch.transform(Matrix44.z_rotate(math.radians(15)))
    assert hatch.dxf.pattern_angle == pytest.approx(45)


def test_translation_does_not_change_hatch_pattern_angle():
    hatch = Hatch()
    hatch.paths.add_polyline_path([(0, 0), (10, 0), (10, 10), (0, 10)])
    hatch.set_pattern_fill("ANSI31", scale=1.0, angle=30.0)

    assert hatch.dxf.pattern_angle == 30
    hatch.transform(Matrix44.translate(100, 0, 0))
    assert hatch.dxf.pattern_angle == pytest.approx(30)


def test_pattern_line_angle_after_rotation_has_new_absolute_angle():
    hatch = Hatch()
    hatch.paths.add_polyline_path([(0, 0), (10, 0), (10, 10), (0, 10)])
    hatch.set_pattern_fill("ANSI31", scale=1.0, angle=30.0)
    pattern_line_angle = hatch.pattern.lines[0].angle
    # ANSI31 has 45° pattern lines in base configuration at 0° rotation
    assert pattern_line_angle == 30 + 45

    # rotation 15 degree counter-clockwise
    hatch.transform(Matrix44.z_rotate(math.radians(15)))
    assert hatch.pattern.lines[0].angle == pytest.approx(30 + 45 + 15)


def test_translation_does_not_change_pattern_line_angle():
    hatch = Hatch()
    hatch.paths.add_polyline_path([(0, 0), (10, 0), (10, 10), (0, 10)])
    hatch.set_pattern_fill("ANSI31", scale=1.0, angle=30.0)
    pattern_line_angle = hatch.pattern.lines[0].angle
    # ANSI31 has 45° pattern lines in base configuration at 0° rotation
    assert pattern_line_angle == 30 + 45

    hatch.transform(Matrix44.translate(100, 0, 0))
    assert hatch.pattern.lines[0].angle == pytest.approx(pattern_line_angle)


def test_translation_moves_pattern_base_point_like_a_boundary_vertex():
    # Regression test for issue #1402: DXFPolygon.transform() translated the
    # boundary paths but left the hatch pattern line base points untouched, so
    # the pattern phase drifted relative to the boundary under any translation.
    hatch = Hatch()
    path = hatch.paths.add_polyline_path([(0, 0), (10, 0), (10, 10), (0, 10)])
    hatch.set_pattern_fill("ANSI31", scale=1.0)
    # anchor the first pattern line base point at the boundary origin (0, 0)
    hatch.pattern.lines[0].base_point = Vec2(0, 0)

    offset = Vec2(37.5, 11.0)
    hatch.transform(Matrix44.translate(offset.x, offset.y, 0))

    # the boundary vertex (0, 0) maps to the translation offset ...
    vx, vy, _ = path.vertices[0]
    assert Vec2(vx, vy).isclose(offset)
    # ... and the pattern base point must move by the same translation
    assert hatch.pattern.lines[0].base_point.isclose(offset)


def test_translation_moves_every_pattern_base_point_by_the_same_offset():
    # Regression test for issue #1402: every non-zero base point must move by
    # the same translation as the boundary, keeping the pattern phase locked.
    hatch = Hatch()
    hatch.paths.add_polyline_path([(0, 0), (10, 0), (10, 10), (0, 10)])
    hatch.set_pattern_fill("ANSI31", scale=1.0)
    # give each pattern line a distinct non-zero base point
    for index, line in enumerate(hatch.pattern.lines):
        line.base_point = Vec2(index + 1, 2 * (index + 1))
    original_base_points = [line.base_point for line in hatch.pattern.lines]

    offset = Vec2(100, 25)
    hatch.transform(Matrix44.translate(offset.x, offset.y, 0))

    for line, base_point in zip(hatch.pattern.lines, original_base_points):
        assert line.base_point.isclose(base_point + offset)


def test_pattern_base_point_maps_like_boundary_vertex_under_full_transform():
    # Regression test for issue #1402: a base point coincident with a boundary
    # vertex must land on the exact same transformed point under a combined
    # rotation + translation. This guards against double-applying the linear
    # part that Pattern.scale() already handles.
    vertices = [(2, 3), (10, 0), (10, 10), (0, 10)]
    hatch = Hatch()
    path = hatch.paths.add_polyline_path(vertices)
    hatch.set_pattern_fill("ANSI31", scale=1.0)
    hatch.pattern.lines[0].base_point = Vec2(2, 3)  # coincident with vertices[0]

    m = Matrix44.chain(
        Matrix44.z_rotate(math.radians(37)),
        Matrix44.translate(37.5, 11.0, 0),
    )
    hatch.transform(m)

    vx, vy, _ = path.vertices[0]
    assert hatch.pattern.lines[0].base_point.isclose(Vec2(vx, vy))


class TestNonUniformPatternScaling:
    # The hatch pattern has to be stretched like the boundary paths, e.g. for a
    # HATCH in a block reference with different x- and y-scaling factors.

    @staticmethod
    def pattern_hatch(definition) -> Hatch:
        hatch = Hatch()
        hatch.paths.add_polyline_path([(3, 2), (103, 2), (103, 102), (60, 70), (3, 102)])
        hatch.set_pattern_fill("TEST", definition=definition)
        return hatch

    def test_horizontal_dashed_pattern_line(self):
        hatch = self.pattern_hatch([[0, (1, 2), (0.5, 1), [2, -1]]])
        hatch.transform(Matrix44.scale(3, 100, 1))

        line = hatch.pattern.lines[0]
        assert line.angle == pytest.approx(0)
        assert line.base_point.isclose((3, 200))
        assert line.offset.isclose((1.5, 100))  # line distance: y-scaling
        assert line.dash_length_items == pytest.approx([6, -3])  # x-scaling

    def test_vertical_dashed_pattern_line(self):
        hatch = self.pattern_hatch([[90, (1, 2), (-1, 0.5), [2, -1]]])
        hatch.transform(Matrix44.scale(3, 100, 1))

        line = hatch.pattern.lines[0]
        assert line.angle == pytest.approx(90)
        assert line.base_point.isclose((3, 200))
        assert line.offset.isclose((-3, 50))  # line distance: x-scaling
        assert line.dash_length_items == pytest.approx([200, -100])  # y-scaling

    def test_diagonal_pattern_line_changes_angle(self):
        hatch = self.pattern_hatch([[45, (0, 0), (-1, 1), []]])
        hatch.transform(Matrix44.scale(1, 2, 1))

        line = hatch.pattern.lines[0]
        assert line.angle == pytest.approx(math.degrees(math.atan2(2, 1)))
        assert line.offset.isclose((-1, 2))

    def test_uniform_scaling_scales_all_pattern_values(self):
        hatch = self.pattern_hatch([[45, (1, 2), (-1, 1), [2, -1]]])
        hatch.transform(Matrix44.scale(3, 3, 3))

        line = hatch.pattern.lines[0]
        assert line.angle == pytest.approx(45)
        assert line.base_point.isclose((3, 6))
        assert line.offset.isclose((-3, 3))
        assert line.dash_length_items == pytest.approx([6, -3])
        assert hatch.dxf.pattern_scale == pytest.approx(3)

    @pytest.mark.parametrize(
        "m",
        [
            Matrix44.scale(1, 250, 1),
            Matrix44.scale(0.001, 1, 1),
            Matrix44.scale(7, 0.3, 1) @ Matrix44.z_rotate(math.radians(33)),
            Matrix44.scale(-2, 5, 1) @ Matrix44.translate(40, -9, 0),
        ],
        ids=["stretch-y", "shrink-x", "non-uniform-rotated", "non-uniform-mirrored"],
    )
    @pytest.mark.parametrize(
        "definition",
        [
            [[45, (0.37, 0.11), (-2.2, 2.2), []]],
            [[0, (0.37, 0.11), (0.7, 1.3), [4, -2]]],
        ],
        ids=["solid-lines", "dashed-lines"],
    )
    def test_rendered_pattern_is_transformed_like_the_boundary(self, m, definition):
        from ezdxf.render import hatching

        def total_length(lines):
            return math.fsum(s.distance(e) for s, e in lines)

        hatch = self.pattern_hatch(definition)
        expected = [
            (m.transform(s), m.transform(e))
            for s, e in hatching.hatch_entity(hatch, jiggle_origin=False)
        ]
        assert len(expected) > 40

        hatch.transform(m)
        result = list(hatching.hatch_entity(hatch, jiggle_origin=False))

        assert len(result) == len(expected)
        assert total_length(result) == pytest.approx(total_length(expected))
