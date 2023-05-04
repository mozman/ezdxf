#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.npshapes import NumpyPoints2d, NumpyPath2d
from ezdxf.math import Matrix44, BoundingBox2d
from ezdxf.path import Path2d, Command


class TestNumpyPolyline:
    @pytest.fixture
    def points(self):
        return [(1, 2), (7, 4), (4, 7), (0, 1)]

    def test_conversion(self, points):
        pl = NumpyPoints2d(points)
        assert len(pl) == len(points)
        assert all(v0.isclose(v1) for v0, v1 in zip(pl.vertices(), points))

    def test_bounding_box(self, points):
        pl = NumpyPoints2d(points)
        bbox = pl.bbox()
        assert bbox.extmin.isclose((0, 1))
        assert bbox.extmax.isclose((7, 7))

    def test_transform_inplace(self, points):
        m = Matrix44.translate(7, 8, 0)
        t_pts = m.fast_2d_transform(points)
        pl = NumpyPoints2d(points)
        pl.transform_inplace(m)
        assert all(v0.isclose(v1) for v0, v1 in zip(pl.vertices(), t_pts))


class TestNumpyPath:
    @pytest.fixture
    def path(self):
        p = Path2d((1, 2))
        p.line_to((7, 4))
        p.curve3_to((4, 7), (0, 1))
        p.move_to((10, 0))
        p.curve4_to((15, 7), (13, 3), (14, 5))
        return p

    def test_to_path_2d(self, path):
        np_path = NumpyPath2d(path)
        assert len(np_path) == len(path)

        path2d = np_path.to_path2d()
        assert len(path2d) == 4
        assert path2d.start.isclose((1, 2))
        assert path2d.end.isclose((15, 7))

        cmds = path2d.commands()
        assert cmds[0].type == Command.LINE_TO
        assert cmds[0].end.isclose((7, 4))

        assert cmds[1].type == Command.CURVE3_TO
        assert cmds[1].end.isclose((4, 7))
        assert cmds[1].ctrl.isclose((0, 1))

        assert cmds[2].type == Command.MOVE_TO
        assert cmds[2].end.isclose((10, 0))

        assert cmds[3].type == Command.CURVE4_TO
        assert cmds[3].end.isclose((15, 7))
        assert cmds[3].ctrl1.isclose((13, 3))
        assert cmds[3].ctrl2.isclose((14, 5))

    def test_bounding_box(self, path):
        np_path = NumpyPath2d(path)
        np_bbox = np_path.bbox()
        box = BoundingBox2d(path.control_vertices())

        assert np_bbox.extmin.isclose(box.extmin)
        assert np_bbox.extmax.isclose(box.extmax)

    def test_transform(self, path):
        m = Matrix44.scale(2, 3, 1) @ Matrix44.translate(-2, 10, 0)
        np_path = NumpyPath2d(path)
        np_path.transform_inplace(m)
        assert all(
            v0.isclose(v1)
            for v0, v1 in zip(np_path.vertices(), path.transform(m).control_vertices())
        )


if __name__ == "__main__":
    pytest.main([__file__])
