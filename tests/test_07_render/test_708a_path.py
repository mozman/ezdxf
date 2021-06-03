# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import math

from ezdxf.path import (
    Path,
    make_path,
    converter,
    Command,
    tools,
)
from ezdxf.math import Vec3, Matrix44, Bezier4P, Bezier3P, close_vectors, OCS
from ezdxf.entities import (
    factory,
    DXFEntity,
    Polymesh,
    LWPolyline,
    PolylinePath,
    EdgePath,
)


def test_init():
    path = Path()
    assert path.start == (0, 0)
    assert len(path) == 0
    assert path.end == (0, 0)


def test_init_start():
    path = Path(start=(1, 2))
    assert path.start == (1, 2)


def test_line_to():
    path = Path()
    path.line_to((1, 2, 3))
    assert path[0] == (Vec3(1, 2, 3),)
    assert path.end == (1, 2, 3)


def test_curve3_to():
    path = Path()
    path.curve3_to((10, 0), (5, 5))
    assert path[0] == ((10, 0), (5, 5))
    assert path.end == (10, 0)


def test_curve4_to():
    path = Path()
    path.curve4_to((1, 2, 3), (0, 1, 0), (0, 2, 0))
    assert path[0] == ((1, 2, 3), (0, 1, 0), (0, 2, 0))
    assert path.end == (1, 2, 3)


def test_add_curves3():
    path = Path()
    c1 = Bezier3P(((0, 0), (1, 1), (2, 0)))
    c2 = Bezier3P(((2, 0), (1, -1), (0, 0)))
    tools.add_bezier3p(path, [c1, c2])
    assert len(path) == 2
    assert path.end == (0, 0)


def test_add_curves4():
    path = Path()
    c1 = Bezier4P(((0, 0), (0, 1), (2, 1), (2, 0)))
    c2 = Bezier4P(((2, 0), (2, -1), (0, -1), (0, 0)))
    tools.add_bezier4p(path, [c1, c2])
    assert len(path) == 2
    assert path.end == (0, 0)


def test_add_curves3_with_gap():
    path = Path()
    c1 = Bezier3P(((0, 0), (1, 1), (2, 0)))
    c2 = Bezier3P(((2, -1), (3, -2), (0, -1)))
    tools.add_bezier3p(path, [c1, c2])
    assert len(path) == 3  # added a line segment between curves
    assert path.end == (0, -1)


def test_add_curves4_with_gap():
    path = Path()
    c1 = Bezier4P(((0, 0, 0), (0, 1, 0), (2, 1, 0), (2, 0, 0)))
    c2 = Bezier4P(((2, -1, 0), (2, -2, 0), (0, -2, 0), (0, -1, 0)))
    tools.add_bezier4p(path, [c1, c2])
    assert len(path) == 3  # added a line segment between curves
    assert path.end == (0, -1, 0)


def test_add_curves3_reverse():
    path = Path(start=(0, 0))
    c1 = Bezier3P(((2, 0), (1, 1), (0, 0)))
    tools.add_bezier3p(path, [c1])
    assert len(path) == 1
    assert path.end == (2, 0, 0)


def test_add_curves4_reverse():
    path = Path(start=(0, 0, 0))
    c1 = Bezier4P(((2, 0, 0), (2, 1, 0), (0, 1, 0), (0, 0, 0)))
    tools.add_bezier4p(path, [c1])
    assert len(path) == 1
    assert path.end == (2, 0, 0)


class TestSubPath:
    def simple_multi_path(self):
        path = Path(start=(1, 0, 0))
        path.line_to((2, 0, 0))
        path.move_to((3, 0, 0))
        return path

    def test_has_no_sub_paths_by_default(self):
        path = Path()
        assert path.has_sub_paths is False

    def test_first_move_to(self):
        path = Path(start=(1, 0, 0))
        path.move_to((2, 0, 0))
        assert path.start.isclose((2, 0, 0)), "should reset the start point"
        assert len(path) == 0, "should not add a MOVETO cmd as first cmd"
        assert path.has_sub_paths is False

    def test_multiple_first_move_to(self):
        path = Path(start=(1, 0, 0))
        path.move_to((2, 0, 0))
        path.move_to((3, 0, 0))
        path.move_to((4, 0, 0))
        assert path.start.isclose((4, 0, 0)), "should reset the start point"
        assert len(path) == 0, "should not add a MOVETO cmd as first cmd"
        assert path.has_sub_paths is False

    def test_move_to_creates_a_multi_path_object(self):
        path = Path(start=(1, 0, 0))
        path.line_to((2, 0, 0))
        path.move_to((3, 0, 0))
        assert len(path) == 2, "should add a MOVETO cmd as last cmd"
        assert path.has_sub_paths is True, "should be a multi path object"
        assert path.end.isclose((3, 0, 0)), "should end at the MOVETO location"

    def test_merge_multiple_move_to_commands_at_the_end(self):
        path = self.simple_multi_path()
        path.move_to((4, 0, 0))
        path.move_to((4, 0, 0))
        assert (
            len(path) == 2
        ), "should merge multiple MOVETO commands at the end of the path"

    def test_clone_multi_path_object(self):
        path = self.simple_multi_path()
        path2 = path.clone()
        assert path2.has_sub_paths
        assert path.end == path2.end

    def test_cant_detect_orientation_of_multi_path_object(self):
        path = self.simple_multi_path()
        pytest.raises(TypeError, path.has_clockwise_orientation)

    def test_cant_convert_multi_path_object_to_clockwise_orientation(self):
        path = self.simple_multi_path()
        pytest.raises(TypeError, path.clockwise)

    def test_cant_convert_multi_path_object_to_ccw_orientation(self):
        path = self.simple_multi_path()
        pytest.raises(TypeError, path.counter_clockwise)

    def test_approximate_multi_path_object(self):
        path = self.simple_multi_path()
        vertices = list(path.approximate())
        assert len(vertices) == 3

    def test_flatten_multi_path_object(self):
        path = self.simple_multi_path()
        vertices = list(path.flattening(0.1))
        assert len(vertices) == 3

    def test_multi_path_object_to_wcs(self):
        path = self.simple_multi_path()
        path.to_wcs(OCS(), 0)
        assert path.end.isclose((3, 0, 0))

    def test_transform_multi_path_object(self):
        path = self.simple_multi_path()
        m = Matrix44.translate(1, 1, 1)
        path2 = path.transform(m)
        assert path.end.isclose((3, 0, 0))
        assert path2.has_sub_paths is True
        assert path2.end.isclose((4, 1, 1))

    def test_sub_paths_from_single_path_object(self):
        path = Path(start=(1, 2, 3))
        paths = list(path.sub_paths())
        assert len(paths) == 1
        s0 = paths[0]
        assert s0.start == (1, 2, 3)
        assert s0.end == (1, 2, 3)
        assert s0.has_sub_paths is False
        assert len(s0) == 0

    def test_sub_paths_from_multi_path_object(self):
        path = self.simple_multi_path()
        s0, s1 = path.sub_paths()
        assert s0.start == (1, 0, 0)
        assert s0.end == (2, 0, 0)
        assert s0.has_sub_paths is False
        assert len(s0) == 1

        assert s1.start == (3, 0, 0)
        assert s1.end == (3, 0, 0)
        assert len(s1) == 0
        assert s1.has_sub_paths is False


def test_add_spline():
    from ezdxf.math import BSpline

    spline = BSpline.from_fit_points([(2, 0), (4, 1), (6, -1), (8, 0)])
    path = Path()
    tools.add_spline(path, spline)
    assert path.start == (2, 0)
    assert path.end == (8, 0)

    # set start point to end of spline
    path = Path(start=(8, 0))
    # add reversed spline, by default the start of
    # an empty path is set to the spline start
    tools.add_spline(path, spline, reset=False)
    assert path.start == (8, 0)
    assert path.end == (2, 0)

    path = Path()
    # add a line segment from (0, 0) to start of spline
    tools.add_spline(path, spline, reset=False)
    assert path.start == (0, 0)
    assert path.end == (8, 0)


def test_from_spline():
    spline = factory.new("SPLINE")
    spline.fit_points = [(2, 0), (4, 1), (6, -1), (8, 0)]
    path = make_path(spline)
    assert path.start == (2, 0)
    assert path.end == (8, 0)


def test_add_ellipse():
    from ezdxf.math import ConstructionEllipse

    ellipse = ConstructionEllipse(
        center=(3, 0),
        major_axis=(1, 0),
        ratio=0.5,
        start_param=0,
        end_param=math.pi,
    )
    path = Path()
    tools.add_ellipse(path, ellipse)
    assert path.start.isclose((4, 0))
    assert path.end.isclose((2, 0))

    # set start point to end of ellipse
    path = Path(start=(2, 0))
    # add reversed ellipse, by default the start of
    # an empty path is set to the ellipse start
    tools.add_ellipse(path, ellipse, reset=False)
    assert path.start.isclose((2, 0))
    assert path.end.isclose((4, 0))

    path = Path()
    # add a line segment from (0, 0) to start of ellipse
    tools.add_ellipse(path, ellipse, reset=False)
    assert path.start.isclose((0, 0))
    assert path.end.isclose((2, 0))


def test_raises_type_error_for_unsupported_objects():
    with pytest.raises(TypeError):
        make_path(DXFEntity())
    with pytest.raises(TypeError):
        make_path(Polymesh.new(dxfattribs={"flags": Polymesh.POLYMESH}))
    with pytest.raises(TypeError):
        make_path(Polymesh.new(dxfattribs={"flags": Polymesh.POLYFACE}))


def test_from_ellipse():
    ellipse = factory.new(
        "ELLIPSE",
        dxfattribs={
            "center": (3, 0),
            "major_axis": (1, 0),
            "ratio": 0.5,
            "start_param": 0,
            "end_param": math.pi,
        },
    )
    path = make_path(ellipse)
    assert path.start.isclose((4, 0))
    assert path.end.isclose((2, 0))


def test_from_arc():
    arc = factory.new(
        "ARC",
        dxfattribs={
            "center": (1, 0, 0),
            "radius": 1,
            "start_angle": 0,
            "end_angle": 180,
        },
    )
    path = make_path(arc)
    assert path.start.isclose((2, 0))
    assert path.end.isclose((0, 0))


@pytest.mark.parametrize("radius", [1, -1])
def test_from_circle(radius):
    circle = factory.new(
        "CIRCLE",
        dxfattribs={
            "center": (1, 0, 0),
            "radius": radius,
        },
    )
    path = make_path(circle)
    assert path.start.isclose((2, 0))
    assert path.end.isclose((2, 0))
    assert path.is_closed is True


def test_from_circle_with_zero_radius():
    circle = factory.new(
        "CIRCLE",
        dxfattribs={
            "center": (1, 0, 0),
            "radius": 0,
        },
    )
    path = make_path(circle)
    assert len(path) == 0


def test_from_line():
    start = Vec3(1, 2, 3)
    end = Vec3(4, 5, 6)
    line = factory.new("LINE", dxfattribs={"start": start, "end": end})
    path = make_path(line)
    assert path.start.isclose(start)
    assert path.end.isclose(end)


@pytest.mark.parametrize("dxftype", ["SOLID", "TRACE", "3DFACE"])
def test_from_quadrilateral_with_4_points(dxftype):
    entity = factory.new(dxftype)
    entity.dxf.vtx0 = (0, 0, 0)
    entity.dxf.vtx1 = (1, 0, 0)
    entity.dxf.vtx2 = (1, 1, 0)
    entity.dxf.vtx3 = (0, 1, 0)
    path = make_path(entity)
    assert path.start == (0, 0, 0)
    assert path.is_closed is True
    assert len(list(path.approximate())) == 5


@pytest.mark.parametrize("dxftype", ["SOLID", "TRACE", "3DFACE"])
def test_from_quadrilateral_with_3_points(dxftype):
    entity = factory.new(dxftype)
    entity.dxf.vtx0 = (0, 0, 0)
    entity.dxf.vtx1 = (1, 0, 0)
    entity.dxf.vtx2 = (1, 1, 0)
    entity.dxf.vtx3 = (1, 1, 0)  # last two points are equal
    path = make_path(entity)
    assert path.is_closed is True
    assert len(list(path.approximate())) == 4


def test_lwpolyline_lines():
    from ezdxf.entities import LWPolyline

    pline = LWPolyline()
    pline.append_points([(1, 1), (2, 1), (2, 2)], format="xy")
    path = make_path(pline)
    assert path.start.isclose((1, 1))
    assert path.end.isclose((2, 2))
    assert len(path) == 2

    pline.dxf.elevation = 1.0
    path = make_path(pline)
    assert path.start.isclose((1, 1, 1))
    assert path.end.isclose((2, 2, 1))


POINTS = [
    (0, 0, 0),
    (3, 0, -1),
    (6, 0, 0),
    (9, 0, 0),
    (9, -3, 0),
]


def test_make_path_from_lwpolyline_with_bulges():
    pline = LWPolyline()
    pline.closed = True
    pline.append_points(POINTS, format="xyb")
    path = make_path(pline)
    assert path.start == (0, 0)
    assert path.end == (0, 0)  # closed
    assert any(cmd.type == Command.CURVE4_TO for cmd in path)


def test_make_path_from_full_circle_lwpolyline():
    pline = LWPolyline()
    pline.closed = True
    pline.append_points([(0, 0, 1), (1, 0, 1)], format="xyb")
    path = make_path(pline)
    assert path.start.isclose((0, 0))
    assert path.end.isclose((0, 0))
    assert len(path) == 4
    assert any(cmd.type == Command.CURVE4_TO for cmd in path)
    vertices = list(path.flattening(0.1))
    assert len(vertices) == 65


def test_make_path_from_full_circle_lwpolyline_issue_424():
    pline = LWPolyline()
    pline.closed = True
    points = [
        (39_482_129.9462793, 3_554_328.753243976, 1.0),
        (39_482_129.95781776, 3_554_328.753243976, 1.0),
    ]
    pline.append_points(points, format="xyb")
    path = make_path(pline)
    assert len(path) == 2


S_SHAPE = [
    (0, 0, 0),
    (5, 0, 1),
    (5, 1, 0),
    (0, 1, -1),
    (0, 2, 0),
    (5, 2, 0),
]


class TestIssue414:
    # Issue 414 shows an error in the bounding box calculation for a closed
    # LWPOLYLINE representing a filled circle (const_width=0.45) and an
    # inverted extrusion (0, 0, -1).
    #
    # original data of the LWPOLYLINE:
    # [
    #     (-43710.28841108403, 19138.631023711587, 0.0, 0.0, -1.0),
    #     (-43710.28841108403, 19139.079023711445, 0.0, 0.0, -1.0),
    # ]

    @pytest.fixture
    def lwpolyline(self) -> LWPolyline:
        # simplified test data:
        points = [(-10.0, 1.0, 0.0, 0.0, -1.0), (-10.0, 1.45, 0.0, 0.0, -1.0)]
        pline = LWPolyline.new(
            dxfattribs={"extrusion": (0, 0, -1), "const_width": 0.45}
        )
        pline.append_points(points)
        pline.close()
        return pline

    def test_WCS_calculation(self, lwpolyline):
        vertices = list(lwpolyline.vertices_in_wcs())
        assert vertices[0].isclose((10, 1, 0))
        assert vertices[1].isclose((10, 1.45, 0))

    def test_make_path(self, lwpolyline):
        p = make_path(lwpolyline)
        assert p.start.isclose((10, 1, 0))
        assert p.is_closed is True

    def test_bounding_box_calculation(self, lwpolyline):
        box = tools.bbox([make_path(lwpolyline)])
        assert box.extmin.isclose((9.775, 1.0))
        assert box.extmax.isclose((10.225, 1.45))


def test_lwpolyline_s_shape():
    from ezdxf.entities import LWPolyline

    pline = LWPolyline()
    pline.append_points(S_SHAPE, format="xyb")
    path = make_path(pline)
    assert path.start == (0, 0)
    assert path.end == (5, 2)  # closed
    assert any(cmd.type == Command.CURVE4_TO for cmd in path)


def test_polyline_lines():
    from ezdxf.entities import Polyline

    pline = Polyline()
    pline.append_formatted_vertices([(1, 1), (2, 1), (2, 2)], format="xy")
    path = make_path(pline)
    assert path.start == (1, 1)
    assert path.end == (2, 2)
    assert len(path) == 2

    pline.dxf.elevation = (0, 0, 1)
    path = make_path(pline)
    assert path.start == (1, 1, 1)
    assert path.end == (2, 2, 1)


def test_polyline_with_bulges():
    from ezdxf.entities import Polyline

    pline = Polyline()
    pline.close(True)
    pline.append_formatted_vertices(POINTS, format="xyb")
    path = make_path(pline)
    assert path.start == (0, 0)
    assert path.end == (0, 0)  # closed
    assert any(cmd.type == Command.CURVE4_TO for cmd in path)


def test_3d_polyline():
    from ezdxf.entities import Polyline

    pline = Polyline.new(dxfattribs={"flags": Polyline.POLYLINE_3D})
    pline.append_vertices([(1, 1, 1), (2, 1, 3), (2, 2, 2)])
    path = make_path(pline)
    assert path.start == (1, 1, 1)
    assert path.end == (2, 2, 2)
    assert len(path) == 2


def test_approximate_lines():
    path = Path()
    path.line_to((1, 1))
    path.line_to((2, 0))
    vertices = list(path.approximate())
    assert len(vertices) == 3
    assert vertices[0] == path.start == (0, 0)
    assert vertices[2] == path.end == (2, 0)


def test_approximate_curves():
    path = Path()
    path.curve3_to((2, 0), (1, 1))
    path.curve4_to((3, 0), (2, 1), (3, 1))
    vertices = list(path.approximate(20))
    assert len(vertices) == 41
    assert vertices[0] == (0, 0)
    assert vertices[-1] == (3, 0)


def test_path_from_hatch_polyline_path_without_bulge():
    polyline_path = PolylinePath()
    polyline_path.set_vertices(
        [(0, 0), (0, 1), (1, 1), (1, 0)], is_closed=False
    )
    path = converter.from_hatch_polyline_path(polyline_path)
    assert len(path) == 3
    assert path.start == (0, 0)
    assert path.end == (1, 0)

    polyline_path.is_closed = True
    path = converter.from_hatch_polyline_path(polyline_path)
    assert len(path) == 4
    assert path.start == (0, 0)
    assert path.end == (0, 0)


def test_path_from_hatch_polyline_path_with_bulge():
    polyline_path = PolylinePath()
    polyline_path.set_vertices(
        [(0, 0), (1, 0, 0.5), (2, 0), (3, 0)], is_closed=False
    )
    path = converter.from_hatch_polyline_path(polyline_path)
    assert len(path) == 4
    assert path.start == (0, 0)
    assert path.end == (3, 0)

    assert path[1].type == Command.CURVE4_TO
    assert path[1].end.isclose((1.5, -0.25))


@pytest.fixture
def p1():
    path = Path()
    path.line_to((2, 0))
    path.curve4_to((4, 0), (2, 1), (4, 1))  # end, ctrl1, ctrl2
    path.curve3_to((6, 0), (5, -1))  # end, ctrl
    return path


def test_path_cloning(p1):
    p2 = p1.clone()
    # p1 and p2 share immutable data:
    for cmd1, cmd2 in zip(p1, p2):
        assert cmd1 is cmd2

    # but have different command lists:
    p2.line_to((4, 4))
    assert len(p2) == len(p1) + 1


def test_approximate_line_curves(p1):
    vertices = list(p1.approximate(20))
    assert len(vertices) == 42
    assert vertices[0].isclose((0, 0))
    assert vertices[-1].isclose((6, 0))


def test_transform(p1):
    p2 = p1.transform(Matrix44.translate(1, 1, 0))
    assert p2.start.isclose((1, 1))
    assert p2[0].end.isclose((3, 1))  # line to location
    assert p2[1].end.isclose((5, 1))  # cubic to location
    assert p2[1].ctrl1.isclose((3, 2))  # cubic ctrl1
    assert p2[1].ctrl2.isclose((5, 2))  # cubic ctrl2
    assert p2[2].end.isclose((7, 1))  # quadratic to location
    assert p2[2].ctrl.isclose((6, 0))  # quadratic ctrl
    assert p2.end.isclose((7, 1))


def test_control_vertices(p1):
    vertices = list(p1.control_vertices())
    assert close_vectors(
        vertices, [(0, 0), (2, 0), (2, 1), (4, 1), (4, 0), (5, -1), (6, 0)]
    )
    path = Path()
    assert len(list(path.control_vertices())) == 0
    assert list(path.control_vertices()) == list(path.approximate(2))
    path = converter.from_vertices([(0, 0), (1, 0)])
    assert len(list(path.control_vertices())) == 2


def test_has_clockwise_orientation():
    # basic has_clockwise_orientation() function is tested in:
    # test_617_clockwise_orientation
    path = converter.from_vertices([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert path.has_clockwise_orientation() is False

    path = Path()
    path.line_to((2, 0))
    path.curve4_to((4, 0), (2, 1), (4, 1))  # end, ctrl1, ctrl2
    assert path.has_clockwise_orientation() is True


def test_reversing_empty_path():
    p = Path()
    assert len(p.reversed()) == 0


def test_reversing_one_line():
    p = Path()
    p.line_to((1, 0))
    p2 = list(p.reversed().control_vertices())
    assert close_vectors(p2, [(1, 0), (0, 0)])


def test_reversing_one_curve3():
    p = Path()
    p.curve3_to((3, 0), (1.5, 1))
    p2 = list(p.reversed().control_vertices())
    assert close_vectors(p2, [(3, 0), (1.5, 1), (0, 0)])


def test_reversing_one_curve4():
    p = Path()
    p.curve4_to((3, 0), (1, 1), (2, 1))
    p2 = list(p.reversed().control_vertices())
    assert close_vectors(p2, [(3, 0), (2, 1), (1, 1), (0, 0)])


def test_reversing_path(p1):
    p2 = p1.reversed()
    assert close_vectors(
        p2.control_vertices(), reversed(list(p1.control_vertices()))
    )


def test_reversing_multi_path():
    p = Path()
    p.line_to((1, 0, 0))
    p.move_to((2, 0, 0))
    p.line_to((3, 0, 0))
    r = p.reversed()
    assert r.has_sub_paths is True
    assert len(r) == 3
    assert r.start == (3, 0, 0)
    assert r.end == (0, 0, 0)

    r0, r1 = r.sub_paths()
    assert r0.start == (3, 0, 0)
    assert r0.end == (2, 0, 0)
    assert r1.start == (1, 0, 0)
    assert r1.end == (0, 0, 0)


def test_reversing_multi_path_with_a_move_to_cmd_at_the_end():
    p = Path()
    p.line_to((1, 0, 0))
    p.move_to((2, 0, 0))
    # The last move_to will become the first move_to.
    # A move_to as first command just moves the start point.
    r = p.reversed()
    assert len(r) == 1
    assert r.start == (1, 0, 0)
    assert r.end == (0, 0, 0)
    assert r.has_sub_paths is False


def test_clockwise(p1):
    from ezdxf.math import has_clockwise_orientation

    cw_path = p1.clockwise()
    ccw_path = p1.counter_clockwise()
    assert has_clockwise_orientation(cw_path.control_vertices()) is True
    assert has_clockwise_orientation(ccw_path.control_vertices()) is False


@pytest.fixture
def edge_path():
    ep = EdgePath()
    ep.add_line(
        (70.79594401862802, 38.81021154906707),
        (61.49705431814723, 38.81021154906707),
    )
    ep.add_ellipse(
        center=(49.64089977339618, 36.43095770602131),
        major_axis=(16.69099826506408, 6.96203799241026),
        ratio=0.173450304570581,
        start_angle=348.7055398636587,
        end_angle=472.8737032507014,
        ccw=True,
    )
    ep.add_line(
        (47.21845383585098, 38.81021154906707),
        (32.00406637283394, 38.81021154906707),
    )
    ep.add_arc(
        center=(27.23255482392775, 37.32841621274949),
        radius=4.996302620946588,
        start_angle=17.25220809399113,
        end_angle=162.7477919060089,
        ccw=True,
    )
    ep.add_line(
        (22.46104327502155, 38.81021154906707),
        (15.94617981131185, 38.81021154906707),
    )
    ep.add_line(
        (15.94617981131185, 38.81021154906707),
        (15.94617981131185, 17.88970141145027),
    )
    ep.add_line(
        (15.94617981131185, 17.88970141145027),
        (22.07965616927404, 17.88970141145026),
    )
    ep.add_spline(
        control_points=[
            (22.07965616927404, 17.88970141145027),
            (23.44151487263461, 19.56130038573538),
            (28.24116384863678, 24.26061858002495),
            (35.32501805918895, 14.41241846270862),
            (46.6153937930182, 11.75667640124574),
            (47.53794331191931, 23.11460620899234),
            (51.8076764251228, 12.06821526039212),
            (60.37405963053161, 14.60131364832752),
            (63.71393926002737, 20.24075830571701),
            (67.36423789268184, 19.07462271006858),
            (68.72358721334537, 17.88970141145026),
        ],
        knot_values=[
            2.825276861104652,
            2.825276861104652,
            2.825276861104652,
            2.825276861104652,
            8.585563484895022,
            22.93271064560279,
            29.77376253023298,
            35.89697937194972,
            41.26107011625705,
            51.23489795733507,
            54.82267350174899,
            59.57512798605262,
            59.57512798605262,
            59.57512798605262,
            59.57512798605262,
        ],
        degree=3,
        periodic=0,
    )
    ep.add_line(
        (68.72358721334535, 17.88970141145027),
        (70.79594401862802, 17.88970141145027),
    )
    ep.add_line(
        (70.79594401862802, 17.88970141145027),
        (70.79594401862802, 38.81021154906707),
    )
    return ep


def test_from_edge_path(edge_path):
    path = converter.from_hatch_edge_path(edge_path)
    assert len(path) == 19


def test_extend_path_by_another_path():
    path = Path((1, 0, 0))
    path.line_to((2, 0, 0))
    path.extend_multi_path(Path((3, 0, 0)))
    assert path.has_sub_paths is True
    assert path.start == (1, 0, 0)
    assert path.end == (3, 0, 0)


def test_extend_path_by_another_single_path():
    path = Path((1, 0, 0))
    path.line_to((2, 0, 0))
    p1 = Path((3, 0, 0))
    p1.line_to((4, 0, 0))
    path.extend_multi_path(p1)
    assert path.has_sub_paths is True
    assert path.start == (1, 0, 0)
    assert path.end == (4, 0, 0)


def test_extend_path_by_another_multi_path():
    path = Path((1, 0, 0))
    path.line_to((2, 0, 0))
    p1 = Path((3, 0, 0))
    p1.line_to((4, 0, 0))
    p1.move_to((5, 0, 0))
    path.extend_multi_path(p1)
    assert path.has_sub_paths is True
    assert path.start == (1, 0, 0)
    assert path.end == (5, 0, 0)


class TestCloseSubPath:
    def test_close_last_sub_path(self):
        p = Path()
        p.line_to((1, 0, 0))
        p.move_to((2, 0, 0))
        p.line_to((3, 0, 0))
        p.close_sub_path()
        assert p.end == (2, 0, 0)

    def test_does_nothing_if_last_sub_path_is_closed(self):
        p = Path()
        p.line_to((1, 0, 0))
        p.move_to((2, 0, 0))
        p.line_to((3, 0, 0))
        p.line_to((2, 0, 0))
        assert len(p) == 4
        p.close_sub_path()
        assert len(p) == 4
        assert p.end == (2, 0, 0)

    def test_does_nothing_if_last_sub_path_is_empty(self):
        p = Path()
        p.line_to((1, 0, 0))
        p.move_to((2, 0, 0))
        assert len(p) == 2
        p.close_sub_path()
        assert len(p) == 2
        assert p.end == (2, 0, 0)

    def test_close_single_path(self):
        p = Path((1, 0, 0))
        p.line_to((3, 0, 0))
        p.close_sub_path()
        assert p.end == (1, 0, 0)


if __name__ == "__main__":
    pytest.main([__file__])
