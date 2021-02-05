#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

pytest.importorskip('matplotlib')  # requires matplotlib!

from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from ezdxf.render import path
from ezdxf.math import Vec2


class TestFromMatplotlibPath:
    fp = FontProperties(family='Arial')

    def to_mpath(self, text: str):
        return TextPath((0, 0), text, size=1, prop=self.fp, usetex=False)

    def test_curve_path_from_text_path(self):
        mpath = self.to_mpath('obc')
        paths = list(path.from_matplotlib_path(mpath))

        # Last command is a LINE_TO created by CLOSEPOLY:
        assert paths[0][-1].type == \
               path.Command.LINE_TO, "expected LINE_TO as last command"

        commands = paths[0][:-1]
        assert all((cmd.type == path.Command.CURVE3_TO
                    for cmd in commands)), "expected only CURVE3_TO commands"
        assert len(paths) == 5  # 2xo 2xb 1xc

    def test_line_path_from_text_path(self):
        mpath = self.to_mpath('abc')
        paths = list(path.from_matplotlib_path(mpath, curves=False))
        path0 = paths[0]
        assert all((cmd.type == path.Command.LINE_TO
                    for cmd in path0)), "expected only LINE_TO commands"
        assert len(paths) == 5  # 2xa 2xb 1xc


class TestBoundingBox:
    def test_empty_paths(self):
        result = path.bbox([])
        assert result.has_data is False

    def test_one_path(self):
        p = path.Path()
        p.line_to((1, 2, 3))
        assert path.bbox([p]).size == (1, 2, 3)

    def test_two_path(self):
        p1 = path.Path()
        p1.line_to((1, 2, 3))
        p2 = path.Path()
        p2.line_to((-3, -2, -1))
        assert path.bbox([p1, p2]).size == (4, 4, 4)

    @pytest.fixture(scope='class')
    def quadratic(self):
        p = path.Path()
        p.curve3_to((2, 0), (1, 1))
        return p

    def test_not_precise_box(self, quadratic):
        result = path.bbox([quadratic], precise=False)
        assert result.extmax.y == pytest.approx(1)  # control point

    def test_precise_box(self, quadratic):
        result = path.bbox([quadratic], precise=True)
        assert result.extmax.y == pytest.approx(0.5)  # parabola


class TestFitPathsIntoBoxUniformScaling:
    @pytest.fixture(scope='class')
    def spath(self):
        p = path.Path()
        p.line_to((1, 2, 3))
        return p

    def test_empty_paths(self):
        assert path.fit_paths_into_box([], (0, 0, 0)) == []

    def test_uniform_stretch_paths_limited_by_z(self, spath):
        result = path.fit_paths_into_box([spath], (6, 6, 6))
        box = path.bbox(result)
        assert box.size == (2, 4, 6)

    def test_uniform_stretch_paths_limited_by_y(self, spath):
        result = path.fit_paths_into_box([spath], (6, 3, 6))
        box = path.bbox(result)
        # stretch factor: 1.5
        assert box.size == (1.5, 3, 4.5)

    def test_uniform_stretch_paths_limited_by_x(self, spath):
        result = path.fit_paths_into_box([spath], (1.2, 6, 6))
        box = path.bbox(result)
        # stretch factor: 1.2
        assert box.size == (1.2, 2.4, 3.6)

    def test_uniform_shrink_paths(self, spath):
        result = path.fit_paths_into_box([spath], (1.5, 1.5, 1.5))
        box = path.bbox(result)
        assert box.size == (0.5, 1, 1.5)

    def test_project_into_xy(self, spath):
        result = path.fit_paths_into_box([spath], (6, 6, 0))
        box = path.bbox(result)
        # Note: z-axis is also ignored by extent detection:
        # scaling factor = 3x
        assert box.size == (3, 6, 0), "z-axis should be ignored"

    def test_project_into_xz(self, spath):
        result = path.fit_paths_into_box([spath], (6, 0, 6))
        box = path.bbox(result)
        assert box.size == (2, 0, 6), "y-axis should be ignored"

    def test_project_into_yz(self, spath):
        result = path.fit_paths_into_box([spath], (0, 6, 6))
        box = path.bbox(result)
        assert box.size == (0, 4, 6), "x-axis should be ignored"

    def test_invalid_target_size(self, spath):
        with pytest.raises(ValueError):
            path.fit_paths_into_box([spath], (0, 0, 0))


class TestFitPathsIntoBoxNonUniformScaling:
    @pytest.fixture(scope='class')
    def spath(self):
        p = path.Path()
        p.line_to((1, 2, 3))
        return p

    def test_non_uniform_stretch_paths(self, spath):
        result = path.fit_paths_into_box([spath], (8, 7, 6), uniform=False)
        box = path.bbox(result)
        assert box.size == (8, 7, 6)

    def test_non_uniform_shrink_paths(self, spath):
        result = path.fit_paths_into_box([spath], (1.5, 1.5, 1.5),
                                         uniform=False)
        box = path.bbox(result)
        assert box.size == (1.5, 1.5, 1.5)

    def test_project_into_xy(self, spath):
        result = path.fit_paths_into_box([spath], (6, 6, 0), uniform=False)
        box = path.bbox(result)
        assert box.size == (6, 6, 0), "z-axis should be ignored"

    def test_project_into_xz(self, spath):
        result = path.fit_paths_into_box([spath], (6, 0, 6), uniform=False)
        box = path.bbox(result)
        assert box.size == (6, 0, 6), "y-axis should be ignored"

    def test_project_into_yz(self, spath):
        result = path.fit_paths_into_box([spath], (0, 6, 6), uniform=False)
        box = path.bbox(result)
        assert box.size == (0, 6, 6), "x-axis should be ignored"


MC = path.MplCmd


class TestToMatplotlibPath:
    def test_no_paths(self):
        with pytest.raises(ValueError):
            path.to_matplotlib_path([])

    def test_line_to(self):
        p = path.Path()
        p.line_to((4, 5, 6))
        p.line_to((7, 8, 6))
        mpath = path.to_matplotlib_path([p])
        assert tuple(mpath.codes) == (MC.MOVETO, MC.LINETO, MC.LINETO)
        assert Vec2.list(mpath.vertices) == [(0, 0), (4, 5), (7, 8)]

    def test_curve3_to(self):
        p = path.Path()
        p.curve3_to((4, 0, 2), (2, 1, 7))
        mpath = path.to_matplotlib_path([p])
        assert tuple(mpath.codes) == (MC.MOVETO, MC.CURVE3, MC.CURVE3)
        assert Vec2.list(mpath.vertices) == [(0, 0), (2, 1), (4, 0)]

    def test_curve4_to(self):
        p = path.Path()
        p.curve4_to((4, 0, 2), (1, 1, 7), (3, 1, 5))
        mpath = path.to_matplotlib_path([p])
        assert tuple(mpath.codes) == (
            MC.MOVETO, MC.CURVE4, MC.CURVE4, MC.CURVE4
        )
        assert Vec2.list(mpath.vertices) == [(0, 0), (1, 1), (3, 1), (4, 0)]

    def test_two_paths(self):
        p1 = path.Path()
        p1.line_to((4, 5, 6))
        p2 = path.Path()
        p2.line_to((7, 8, 6))
        mpath = path.to_matplotlib_path([p1, p2])
        assert tuple(mpath.codes) == (
            MC.MOVETO, MC.LINETO,
            MC.MOVETO, MC.LINETO,
        )
        assert Vec2.list(mpath.vertices) == [
            (0, 0), (4, 5),
            (0, 0), (7, 8),
        ]


if __name__ == '__main__':
    pytest.main([__file__])
