#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.npshapes import NumpyPoints2d, NumpyPath2d
from ezdxf.math import Matrix44, BoundingBox2d, close_vectors
from ezdxf.path import Path2d, Command, from_vertices
from ezdxf.fonts import fonts


class TestNumpyPoints:
    @pytest.fixture
    def points(self):
        return [(1, 2), (7, 4), (4, 7), (0, 1)]

    def test_conversion(self, points):
        pl = NumpyPoints2d(points)
        assert len(pl) == len(points)
        assert all(v0.isclose(v1) for v0, v1 in zip(pl.vertices(), points))

    def test_extents(self, points):
        pl = NumpyPoints2d(points)
        extmin, extmax = pl.extents()
        assert extmin.isclose((0, 1))
        assert extmax.isclose((7, 7))

    def test_transform_inplace(self, points):
        m = Matrix44.translate(7, 8, 0)
        t_pts = m.fast_2d_transform(points)
        pl = NumpyPoints2d(points)
        pl.transform_inplace(m)
        assert all(v0.isclose(v1) for v0, v1 in zip(pl.vertices(), t_pts))


class TestNumpyPath2d:
    @pytest.fixture
    def path(self):
        p = Path2d((1, 2))
        p.line_to((7, 4))
        p.curve3_to((4, 7), (0, 1))
        p.move_to((10, 0))
        p.curve4_to((15, 7), (13, 3), (14, 5))
        return p

    def test_clone(self, path):
        np_path = NumpyPath2d(path)
        clone_ = np_path.clone().to_path2d()
        assert clone_.control_vertices() == path.control_vertices()
        assert clone_.command_codes() == path.command_codes()

    def test_start_point(self, path):
        assert path.start.isclose((1, 2))

    def test_end_point(self, path):
        assert path.end.isclose((15, 7))

    def test_has_subpaths(self, path):
        np_path = NumpyPath2d(path)
        assert np_path.has_sub_paths is True

    def test_has_no_subpaths(self):
        np_path = NumpyPath2d(Path2d((1, 2)))
        assert np_path.has_sub_paths is False

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

    def test_extents(self, path):
        np_path = NumpyPath2d(path)
        extmin, extmax = np_path.extents()
        box = BoundingBox2d(path.control_vertices())

        assert extmin.isclose(box.extmin)
        assert extmax.isclose(box.extmax)

    def test_transform(self, path):
        m = Matrix44.scale(2, 3, 1) @ Matrix44.translate(-2, 10, 0)
        np_path = NumpyPath2d(path)
        np_path.transform_inplace(m)
        assert all(
            v0.isclose(v1)
            for v0, v1 in zip(np_path.vertices(), path.transform(m).control_vertices())
        )

    def test_start_point_only_path(self):
        p = NumpyPath2d(Path2d((10, 20)))
        assert p.start.isclose((10, 20))
        # and back
        assert p.to_path2d().start.isclose((10, 20))

    def test_from_empty_path(self):
        p = NumpyPath2d(Path2d())
        assert len(p) == 0
        assert p.start == (0, 0)
        assert p.end == (0, 0)
        # and back
        assert p.to_path2d().start == (0, 0)  # default start point

    def test_create_empty_path_from_none(self):
        p = NumpyPath2d(None)
        assert len(p) == 0
        with pytest.raises(IndexError):
            assert p.start
        with pytest.raises(IndexError):
            assert p.end
        # and back
        assert p.to_path2d().start == (0, 0)  # default start point


def test_path2d_conversion_methods():
    f = fonts.make_font("DejaVuSans.ttf", 1.0)
    source_path = f.text_path("ABCDEFabcdef")
    assert source_path.has_sub_paths is True
    assert source_path.has_curves is True
    assert source_path.has_lines is True

    converted_path = NumpyPath2d(source_path).to_path2d()
    assert converted_path.has_sub_paths is True
    assert converted_path.has_curves is True
    assert converted_path.has_lines is True

    assert source_path.start.isclose(converted_path.start)
    assert source_path.end.isclose(converted_path.end)

    assert source_path.command_codes() == converted_path.command_codes()
    cv0 = source_path.control_vertices()
    cv1 = converted_path.control_vertices()
    assert len(cv0) == len(cv1)
    for v0, v1 in zip(cv0, cv1):
        assert v0.isclose(v1)
    assert source_path._start_index == converted_path._start_index


@pytest.fixture(scope="module")
def p1():
    path = Path2d()
    path.line_to((2, 0))
    path.curve4_to((4, 0), (2, 1), (4, 1))  # end, ctrl1, ctrl2
    path.curve3_to((6, 0), (5, -1))  # end, ctrl
    return path


def test_flatten_path(p1):
    p2 = NumpyPath2d(p1)
    v1 = list(p1.flattening(0.01))
    v2 = list(p2.flattening(0.01))
    assert close_vectors(v1, v2)


class TestReversePath:
    def test_reversing_empty_path(self):
        p = NumpyPath2d(None)
        p.reverse()
        assert len(p) == 0

    def test_reversing_one_line(self):
        p = Path2d()
        p.line_to((1, 0))
        p2 = NumpyPath2d(p).reverse()
        vertices = p2.control_vertices()
        assert close_vectors(vertices, [(1, 0), (0, 0)])

    def test_reversing_one_curve3(self):
        p = Path2d()
        p.curve3_to((3, 0), (1.5, 1))
        p2 = NumpyPath2d(p).reverse()
        assert close_vectors(p2.control_vertices(), [(3, 0), (1.5, 1), (0, 0)])

    def test_reversing_one_curve4(self):
        p = Path2d()
        p.curve4_to((3, 0), (1, 1), (2, 1))
        p2 = NumpyPath2d(p).reverse()
        assert close_vectors(p2.control_vertices(), [(3, 0), (2, 1), (1, 1), (0, 0)])

    def test_reversing_path_ctrl_vertices(self, p1):
        p2 = NumpyPath2d(p1).reverse()
        assert close_vectors(
            p2.control_vertices(), reversed(list(p1.control_vertices()))
        )

    def test_reversing_flattened_path(self, p1):
        p2 = NumpyPath2d(p1)
        p2.reverse()
        v1 = list(p1.flattening(0.01))
        v2 = list(p2.flattening(0.01))
        assert close_vectors(v1, reversed(v2))

    def test_reversing_multi_path(self):
        p = Path2d()
        p.line_to((1, 0, 0))
        p.move_to((2, 0, 0))
        p.line_to((3, 0, 0))

        r = NumpyPath2d(p).reverse()
        assert r.has_sub_paths is True
        assert len(r) == 3
        assert r.start == (3, 0, 0)
        assert r.end == (0, 0, 0)

    def test_reversing_multi_path_with_a_move_to_cmd_at_the_end(self):
        p = Path2d()
        p.line_to((1, 0, 0))
        p.move_to((2, 0, 0))
        # The last move_to will become the first move_to.
        # A move_to as first command just moves the start point.
        r = NumpyPath2d(p).reverse()
        assert len(r) == 1
        assert r.start == (1, 0, 0)
        assert r.end == (0, 0, 0)
        assert r.has_sub_paths is False

    def test_has_clockwise_orientation(self, p1):
        p2 = NumpyPath2d(p1)
        assert p2.has_clockwise_orientation() is True

    def test_has_counter_clockwise_orientation(self, p1):
        p2 = NumpyPath2d(p1)
        assert p2.reverse().has_clockwise_orientation() is False

    def test_cw_and_ccw_orientation(self, p1):
        from ezdxf.math import has_clockwise_orientation

        p2 = NumpyPath2d(p1)
        assert has_clockwise_orientation(p2.clockwise().control_vertices()) is True
        assert (
            has_clockwise_orientation(p2.counter_clockwise().control_vertices())
            is False
        )


def test_clockwise_orientation_of_implicit_closed_path():
    p2 = NumpyPath2d(from_vertices([(0, 0), (10, 0), (10, 10), (0, 10)]))
    assert p2.has_clockwise_orientation() is False


def test_clockwise_orientation_of_explicit_closed_path():
    p2 = NumpyPath2d(from_vertices([(0, 0), (10, 0), (10, 10), (0, 10)], close=True))
    assert p2.has_clockwise_orientation() is False


def test_counter_clockwise_orientation_of_implicit_closed_path():
    p2 = NumpyPath2d(from_vertices([(0, 10), (10, 10), (10, 0), (0, 0)]))
    assert p2.has_clockwise_orientation() is True


def test_counter_clockwise_orientation_of_explicit_closed_path():
    p2 = NumpyPath2d(from_vertices([(0, 10), (10, 10), (10, 0), (0, 0)], close=True))
    assert p2.has_clockwise_orientation() is True


if __name__ == "__main__":
    pytest.main([__file__])
