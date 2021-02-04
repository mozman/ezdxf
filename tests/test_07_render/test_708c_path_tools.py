#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

pytest.importorskip('matplotlib')  # requires matplotlib!

from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from ezdxf.render import path


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

    @pytest.fixture
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


class TestFitPathsIntoBox:
    pass


if __name__ == '__main__':
    pytest.main([__file__])
