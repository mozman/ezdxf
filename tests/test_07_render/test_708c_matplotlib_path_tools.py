#  Copyright (c) 2021-2023, Manfred Moitzi
#  License: MIT License

import pytest

pytest.importorskip("matplotlib")
from ezdxf import path
from ezdxf.math import Vec2
from ezdxf import npshapes


class MC:
    CLOSEPOLY = 79
    CURVE3 = 3
    CURVE4 = 4
    LINETO = 2
    MOVETO = 1
    STOP = 0


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
