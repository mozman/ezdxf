#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import pytest
from ezdxf.layouts import VirtualLayout
from ezdxf.math import Matrix44, OCS
from ezdxf.render.path import (
    Path, bbox, fit_paths_into_box, transform_paths, transform_paths_to_ocs,
    Command, to_polylines3d, to_lines,
)
from ezdxf.render import make_path


class TestTransformPaths():
    def test_empty_paths(self):
        result = transform_paths([], Matrix44())
        assert len(result) == 0

    def test_start_point_only_paths(self):
        result = transform_paths([Path((1, 2, 3))], Matrix44())
        assert len(result) == 1
        assert len(result[0]) == 0
        assert result[0].start == (1, 2, 3)

    def test_transformation_is_executed(self):
        # Real transformation is just tested once, because Matrix44
        # transformation is tested in 605:
        result = transform_paths([Path((1, 2, 3))], Matrix44.translate(1, 1, 1))
        assert result[0].start == (2, 3, 4)

    def test_one_path_line_to(self):
        path = Path()
        path.line_to((1, 0))
        result = transform_paths([path], Matrix44())
        path0 = result[0]
        assert path0[0].type == Command.LINE_TO
        assert path0.start == (0, 0)
        assert path0.end == (1, 0)

    def test_one_path_curve3_to(self):
        path = Path()
        path.curve3_to((2, 0), (1, 1))
        result = transform_paths([path], Matrix44())
        path0 = result[0]
        assert path0[0].type == Command.CURVE3_TO
        assert len(path0[0]) == 2
        assert path0.start == (0, 0)
        assert path0.end == (2, 0)

    def test_one_path_curve4_to(self):
        path = Path()
        path.curve4_to((2, 0), (0, 1), (2, 1))
        result = transform_paths([path], Matrix44())
        path0 = result[0]
        assert path0[0].type == Command.CURVE4_TO
        assert len(path0[0]) == 3
        assert path0.start == (0, 0)
        assert path0.end == (2, 0)

    def test_one_path_multiple_command(self):
        path = Path()
        path.line_to((1, 0))
        path.curve3_to((2, 0), (2.5, 1))
        path.curve4_to((3, 0), (2, 1), (3, 1))
        result = transform_paths([path], Matrix44())

        path0 = result[0]
        assert path0[0].type == Command.LINE_TO
        assert path0[1].type == Command.CURVE3_TO
        assert path0[2].type == Command.CURVE4_TO
        assert path0.start == (0, 0)
        assert path0.end == (3, 0)

    def test_two_paths_one_command(self):
        path_a = Path()
        path_a.line_to((1, 0))
        path_b = Path((2, 0))
        path_b.line_to((3, 0))
        result = transform_paths([path_a, path_b], Matrix44())

        path0 = result[0]
        assert path0[0].type == Command.LINE_TO
        assert path0.start == (0, 0)
        assert path0.end == (1, 0)

        path1 = result[1]
        assert path1[0].type == Command.LINE_TO
        assert path1.start == (2, 0)
        assert path1.end == (3, 0)

    def test_two_paths_multiple_commands(self):
        path_a = Path()
        path_a.line_to((1, 0))
        path_a.curve3_to((2, 0), (2.5, 1))
        path_a.curve4_to((3, 0), (2, 1), (3, 1))

        path_b = path_a.transform(Matrix44.translate(4, 0, 0))
        result = transform_paths([path_a, path_b], Matrix44())

        path0 = result[0]
        assert path0[0].type == Command.LINE_TO
        assert path0[1].type == Command.CURVE3_TO
        assert path0[2].type == Command.CURVE4_TO
        assert path0.start == (0, 0)
        assert path0.end == (3, 0)

        path1 = result[1]
        assert path1[0].type == Command.LINE_TO
        assert path1[1].type == Command.CURVE3_TO
        assert path1[2].type == Command.CURVE4_TO
        assert path1.start == (4, 0)
        assert path1.end == (7, 0)

    def test_to_ocs(self):
        p = Path((0, 1, 1))
        p.line_to((0, 1, 3))
        ocs = OCS((1, 0, 0))  # x-Axis
        result = list(transform_paths_to_ocs([p], ocs))
        p0 = result[0]
        assert ocs.from_wcs((0, 1, 1)) == p0.start
        assert ocs.from_wcs((0, 1, 3)) == p0[0].end


class TestBoundingBox:
    def test_empty_paths(self):
        result = bbox([])
        assert result.has_data is False

    def test_one_path(self):
        p = Path()
        p.line_to((1, 2, 3))
        assert bbox([p]).size == (1, 2, 3)

    def test_two_path(self):
        p1 = Path()
        p1.line_to((1, 2, 3))
        p2 = Path()
        p2.line_to((-3, -2, -1))
        assert bbox([p1, p2]).size == (4, 4, 4)

    @pytest.fixture(scope='class')
    def quadratic(self):
        p = Path()
        p.curve3_to((2, 0), (1, 1))
        return p

    def test_not_precise_box(self, quadratic):
        result = bbox([quadratic], precise=False)
        assert result.extmax.y == pytest.approx(1)  # control point

    def test_precise_box(self, quadratic):
        result = bbox([quadratic], precise=True)
        assert result.extmax.y == pytest.approx(0.5)  # parabola


class TestFitPathsIntoBoxUniformScaling:
    @pytest.fixture(scope='class')
    def spath(self):
        p = Path()
        p.line_to((1, 2, 3))
        return p

    def test_empty_paths(self):
        assert fit_paths_into_box([], (0, 0, 0)) == []

    def test_uniform_stretch_paths_limited_by_z(self, spath):
        result = fit_paths_into_box([spath], (6, 6, 6))
        box = bbox(result)
        assert box.size == (2, 4, 6)

    def test_uniform_stretch_paths_limited_by_y(self, spath):
        result = fit_paths_into_box([spath], (6, 3, 6))
        box = bbox(result)
        # stretch factor: 1.5
        assert box.size == (1.5, 3, 4.5)

    def test_uniform_stretch_paths_limited_by_x(self, spath):
        result = fit_paths_into_box([spath], (1.2, 6, 6))
        box = bbox(result)
        # stretch factor: 1.2
        assert box.size == (1.2, 2.4, 3.6)

    def test_uniform_shrink_paths(self, spath):
        result = fit_paths_into_box([spath], (1.5, 1.5, 1.5))
        box = bbox(result)
        assert box.size == (0.5, 1, 1.5)

    def test_project_into_xy(self, spath):
        result = fit_paths_into_box([spath], (6, 6, 0))
        box = bbox(result)
        # Note: z-axis is also ignored by extent detection:
        # scaling factor = 3x
        assert box.size == (3, 6, 0), "z-axis should be ignored"

    def test_project_into_xz(self, spath):
        result = fit_paths_into_box([spath], (6, 0, 6))
        box = bbox(result)
        assert box.size == (2, 0, 6), "y-axis should be ignored"

    def test_project_into_yz(self, spath):
        result = fit_paths_into_box([spath], (0, 6, 6))
        box = bbox(result)
        assert box.size == (0, 4, 6), "x-axis should be ignored"

    def test_invalid_target_size(self, spath):
        with pytest.raises(ValueError):
            fit_paths_into_box([spath], (0, 0, 0))


class TestFitPathsIntoBoxNonUniformScaling:
    @pytest.fixture(scope='class')
    def spath(self):
        p = Path()
        p.line_to((1, 2, 3))
        return p

    def test_non_uniform_stretch_paths(self, spath):
        result = fit_paths_into_box([spath], (8, 7, 6), uniform=False)
        box = bbox(result)
        assert box.size == (8, 7, 6)

    def test_non_uniform_shrink_paths(self, spath):
        result = fit_paths_into_box([spath], (1.5, 1.5, 1.5),
                                    uniform=False)
        box = bbox(result)
        assert box.size == (1.5, 1.5, 1.5)

    def test_project_into_xy(self, spath):
        result = fit_paths_into_box([spath], (6, 6, 0), uniform=False)
        box = bbox(result)
        assert box.size == (6, 6, 0), "z-axis should be ignored"

    def test_project_into_xz(self, spath):
        result = fit_paths_into_box([spath], (6, 0, 6), uniform=False)
        box = bbox(result)
        assert box.size == (6, 0, 6), "y-axis should be ignored"

    def test_project_into_yz(self, spath):
        result = fit_paths_into_box([spath], (0, 6, 6), uniform=False)
        box = bbox(result)
        assert box.size == (0, 6, 6), "x-axis should be ignored"


class TestToEntityConverter:
    @pytest.fixture
    def path(self):
        p = Path()
        p.line_to((4, 0, 0))
        p.curve4_to((0, 0, 0), (3, 1, 1), (1, 1, 1))
        return p

    def test_path_to_polylines3d(self, path):
        polylines = list(to_polylines3d(path))
        assert len(polylines) == 1
        p0 = polylines[0]
        assert p0.dxftype() == 'POLYLINE'
        assert p0.is_3d_polyline is True
        assert len(p0) == 18
        assert p0.vertices[0].dxf.location == (0, 0, 0)
        assert p0.vertices[-1].dxf.location == (0, 0, 0)

    def test_path_to_lines(self, path):
        lines = list(to_lines(path))
        assert len(lines) == 17
        l0 = lines[0]
        assert l0.dxftype() == 'LINE'
        assert l0.dxf.start == (0, 0, 0)
        assert l0.dxf.end == (4, 0, 0)


# Issue #224 regression test
@pytest.fixture
def ellipse():
    layout = VirtualLayout()
    return layout.add_ellipse(
        center=(1999.488177113287, -1598.02265357955, 0.0),
        major_axis=(629.968069297, 0.0, 0.0),
        ratio=0.495263197,
        start_param=-1.261396328799999,
        end_param=-0.2505454928,
        dxfattribs={
            'layer': "0",
            'linetype': "Continuous",
            'color': 3,
            'extrusion': (0.0, 0.0, -1.0),
        },
    )


def test_issue_224_end_points(ellipse):
    p = make_path(ellipse)

    assert ellipse.start_point.isclose(p.start)
    assert ellipse.end_point.isclose(p.end)

    # end point locations measured in BricsCAD:
    assert ellipse.start_point.isclose((2191.3054, -1300.8375), abs_tol=1e-4)
    assert ellipse.end_point.isclose((2609.7870, -1520.6677), abs_tol=1e-4)
