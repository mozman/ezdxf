#  Copyright (c) 2021-2023, Manfred Moitzi
#  License: MIT License

import pytest

pytest.importorskip("matplotlib")

from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from ezdxf import path
from ezdxf.math import Vec2
from ezdxf import npshapes


class TestFromMatplotlibPath:
    fp = FontProperties(family="Arial")

    def to_mpath(self, text: str):
        return TextPath((0, 0), text, size=1, prop=self.fp, usetex=False)

    def test_curve_path_from_text_path(self):
        mpath = self.to_mpath("obc")
        paths = list(path.from_matplotlib_path(mpath))

        # Last command is a LINE_TO created by CLOSEPOLY only if the path
        # isn't closed:
        assert (
            paths[0][-1].type != path.Command.LINE_TO
        ), "did not expected LINE_TO as last command"

        commands = list(paths[0])[:-1]
        assert all(
            (cmd.type == path.Command.CURVE3_TO for cmd in commands)
        ), "expected only CURVE3_TO commands"
        assert len(paths) == 5  # 2xo 2xb 1xc

    def test_line_path_from_text_path(self):
        mpath = self.to_mpath("abc")
        paths = list(path.from_matplotlib_path(mpath, curves=False))
        path0 = paths[0]
        assert all(
            (cmd.type == path.Command.LINE_TO for cmd in path0)
        ), "expected only LINE_TO commands"
        assert len(paths) == 5  # 2xa 2xb 1xc


from ezdxf.path.converter import MplCmd as MC


class TestPathToMatplotlibPath:
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
            MC.MOVETO,
            MC.CURVE4,
            MC.CURVE4,
            MC.CURVE4,
        )
        assert Vec2.list(mpath.vertices) == [(0, 0), (1, 1), (3, 1), (4, 0)]

    def test_two_single_paths(self):
        p1 = path.Path()
        p1.line_to((4, 5, 6))
        p2 = path.Path()
        p2.line_to((7, 8, 6))
        mpath = path.to_matplotlib_path([p1, p2])
        assert tuple(mpath.codes) == (
            MC.MOVETO,
            MC.LINETO,
            MC.MOVETO,
            MC.LINETO,
        )
        assert Vec2.list(mpath.vertices) == [
            (0, 0),
            (4, 5),
            (0, 0),
            (7, 8),
        ]

    def test_one_multi_path(self):
        p = path.Path()
        p.line_to((4, 5, 6))
        p.move_to((0, 0, 0))
        p.line_to((7, 8, 9))

        mpath = path.to_matplotlib_path([p])
        assert tuple(mpath.codes) == (
            MC.MOVETO,
            MC.LINETO,
            MC.MOVETO,
            MC.LINETO,
        )
        assert Vec2.list(mpath.vertices) == [
            (0, 0),
            (4, 5),
            (0, 0),
            (7, 8),
        ]


class TestNumpyPath2dToMatplotlibPath:
    def test_no_paths(self):
        with pytest.raises(ValueError):
            npshapes.to_matplotlib_path([])

    def test_line_to(self):
        p = path.Path()
        p.line_to((4, 5, 6))
        p.line_to((7, 8, 6))
        mpath = npshapes.to_matplotlib_path([npshapes.NumpyPath2d(p)])
        assert tuple(mpath.codes) == (MC.MOVETO, MC.LINETO, MC.LINETO)
        assert Vec2.list(mpath.vertices) == [(0, 0), (4, 5), (7, 8)]

    def test_curve3_to(self):
        p = path.Path()
        p.curve3_to((4, 0, 2), (2, 1, 7))
        mpath = npshapes.to_matplotlib_path([npshapes.NumpyPath2d(p)])
        assert tuple(mpath.codes) == (MC.MOVETO, MC.CURVE3, MC.CURVE3)
        assert Vec2.list(mpath.vertices) == [(0, 0), (2, 1), (4, 0)]

    def test_curve4_to(self):
        p = path.Path()
        p.curve4_to((4, 0, 2), (1, 1, 7), (3, 1, 5))
        mpath = npshapes.to_matplotlib_path([npshapes.NumpyPath2d(p)])
        assert tuple(mpath.codes) == (
            MC.MOVETO,
            MC.CURVE4,
            MC.CURVE4,
            MC.CURVE4,
        )
        assert Vec2.list(mpath.vertices) == [(0, 0), (1, 1), (3, 1), (4, 0)]

    def test_two_single_paths(self):
        p1 = path.Path()
        p1.line_to((4, 5, 6))
        p2 = path.Path()
        p2.line_to((7, 8, 6))
        mpath = npshapes.to_matplotlib_path(
            [npshapes.NumpyPath2d(p1), npshapes.NumpyPath2d(p2)]
        )
        assert tuple(mpath.codes) == (
            MC.MOVETO,
            MC.LINETO,
            MC.MOVETO,
            MC.LINETO,
        )
        assert Vec2.list(mpath.vertices) == [
            (0, 0),
            (4, 5),
            (0, 0),
            (7, 8),
        ]

    def test_one_multi_path(self):
        p = path.Path()
        p.line_to((4, 5, 6))
        p.move_to((0, 0, 0))
        p.line_to((7, 8, 9))

        mpath = npshapes.to_matplotlib_path([npshapes.NumpyPath2d(p)])
        assert tuple(mpath.codes) == (
            MC.MOVETO,
            MC.LINETO,
            MC.MOVETO,
            MC.LINETO,
        )
        assert Vec2.list(mpath.vertices) == [
            (0, 0),
            (4, 5),
            (0, 0),
            (7, 8),
        ]


if __name__ == "__main__":
    pytest.main([__file__])
