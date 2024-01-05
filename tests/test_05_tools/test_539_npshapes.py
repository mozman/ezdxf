#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.npshapes import NumpyPoints2d, NumpyPath2d, NumpyPoints3d
from ezdxf.math import Matrix44, BoundingBox2d, close_vectors, Vec2, Vec3
from ezdxf.path import Command, from_vertices, Path
from ezdxf.render import forms


class TestNumpyPoints2d:
    @pytest.fixture
    def points(self):
        return Vec2.list([(1, 2), (7, 4), (4, 7), (0, 1)])

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


class TestNumpyPoints3d:
    @pytest.fixture
    def points(self):
        return Vec3.list([(1, 2, 3), (7, 4, 3), (4, 7, 9), (0, 1, 3)])

    def test_conversion(self, points):
        pl = NumpyPoints3d(points)
        assert len(pl) == len(points)
        assert all(v0.isclose(v1) for v0, v1 in zip(pl.vertices(), points))

    def test_extents(self, points):
        pl = NumpyPoints3d(points)
        extmin, extmax = pl.extents()
        assert extmin.isclose((0, 1, 3))
        assert extmax.isclose((7, 7, 9))

    def test_transform_inplace(self, points):
        m = Matrix44.translate(7, 8, 0)
        t_pts = list(m.transform_vertices(points))
        pl = NumpyPoints3d(points)
        pl.transform_inplace(m)
        assert all(v0.isclose(v1) for v0, v1 in zip(pl.vertices(), t_pts))


class TestNumpyPath2d:
    @pytest.fixture
    def path(self):
        p = Path((1, 2))
        p.line_to((7, 4))
        p.curve3_to((4, 7), (0, 1))
        p.move_to((10, 0))
        p.curve4_to((15, 7), (13, 3), (14, 5))
        return p

    def test_clone(self, path):
        np_path = NumpyPath2d(path)
        clone_ = np_path.clone().to_path()
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
        np_path = NumpyPath2d(Path((1, 2)))
        assert np_path.has_sub_paths is False

    def test_to_path_2d(self, path):
        np_path = NumpyPath2d(path)
        assert len(np_path) == len(path)

        path = np_path.to_path()
        assert len(path) == 4
        assert path.start.isclose((1, 2))
        assert path.end.isclose((15, 7))

        cmds = path.commands()
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
        p = NumpyPath2d(Path((10, 20)))
        assert p.start.isclose((10, 20))
        # and back
        assert p.to_path().start.isclose((10, 20))

    def test_from_empty_path(self):
        p = NumpyPath2d(Path())
        assert len(p) == 0
        assert p.start == (0, 0)
        assert p.end == (0, 0)
        # and back
        assert p.to_path().start == (0, 0)  # default start point

    def test_create_empty_path_from_none(self):
        p = NumpyPath2d(None)
        assert len(p) == 0
        with pytest.raises(IndexError):
            assert p.start
        with pytest.raises(IndexError):
            assert p.end
        # and back
        assert p.to_path().start == (0, 0)  # default start point


@pytest.fixture
def first():
    p = Path()
    p.line_to((10, 0))
    return NumpyPath2d(p)


@pytest.fixture
def second():
    p = Path((10, 0))
    p.line_to((20, 0))
    return NumpyPath2d(p)


@pytest.fixture
def third():
    p = Path((20, 0))
    p.line_to((30, 0))
    return NumpyPath2d(p)


@pytest.fixture
def curve3():
    p = Path((0, 0))
    p.curve3_to((10, 0), (5, 3))
    return NumpyPath2d(p)


@pytest.fixture
def curve4():
    p = Path((10, 0))
    p.curve4_to((20, 0), (13, -3), (17, 3))
    return NumpyPath2d(p)


class TestNumpyPath2dExtend:
    def test_extend_empty_path(self, second):
        empty = NumpyPath2d(None)
        empty.extend([second])
        assert len(empty) == 1
        assert empty.start.isclose((10, 0))
        assert empty.end.isclose((20, 0))

    def test_extend_by_empty_path(self, first):
        first.extend([NumpyPath2d(None)])
        assert len(first) == 1
        assert first.start.isclose((0, 0))
        assert first.end.isclose((10, 0))

    def test_extend_by_empty_2d_path(self, first):
        empty = Path(Vec2(7, 7))  # has no drawing commands
        first.extend([NumpyPath2d(empty)])
        assert len(first) == 1
        assert first.start.isclose((0, 0))
        assert first.end.isclose((10, 0))

    def test_extend_by_empty_list(self, first):
        first.extend([])
        assert len(first) == 1
        assert first.start.isclose((0, 0))
        assert first.end.isclose((10, 0))

    def test_concatenate_adjacent_paths(self, first, second):
        base = NumpyPath2d.concatenate([first, second])
        assert base.command_codes() == [1, 1]
        assert base.start.isclose((0, 0))
        assert base.end.isclose((20, 0))

    def test_concatenate_separated_paths(self, first, third):
        base = NumpyPath2d.concatenate([first, third])
        assert base.has_sub_paths is True, "expected a MOVE_TO command"
        assert base.command_codes() == [1, 4, 1]
        vertices = base.vertices()
        assert len(vertices) == 4
        assert vertices[0].isclose((0, 0))  # start
        assert vertices[1].isclose((10, 0))  # line_to
        assert vertices[2].isclose((20, 0))  # move_to
        assert vertices[3].isclose((30, 0))  # line_to

    def test_concatenate_all_paths(self, first, second, third):
        base = NumpyPath2d.concatenate([first, second, third])
        assert base.command_codes() == [1, 1, 1]
        vertices = base.vertices()
        assert len(vertices) == 4
        assert vertices[0].isclose((0, 0))  # start
        assert vertices[1].isclose((10, 0))  # line_to
        assert vertices[2].isclose((20, 0))  # line_to
        assert vertices[3].isclose((30, 0))  # line_to

    def test_concatenate_curves(self, curve3, curve4):
        base = NumpyPath2d.concatenate([curve3, curve4])
        assert base.command_codes() == [2, 3]
        vertices = base.vertices()
        assert len(vertices) == 6
        assert vertices[0].isclose((0, 0))  # start
        assert vertices[1].isclose((5, 3))  # curve_3_to - ctrl
        assert vertices[2].isclose((10, 0))  # curve_3_to - end
        assert vertices[3].isclose((13, -3))  # curve_4_to - ctrl1
        assert vertices[4].isclose((17, 3))  # curve_4_to - ctrl2
        assert vertices[5].isclose((20, 0))  # curve_4_to - end

    def test_concatenate_empty_list_returns_empty_path(self):
        base = NumpyPath2d.concatenate([])
        assert base.command_codes() == []
        assert base.vertices() == []
        with pytest.raises(IndexError):
            base.start.isclose((0, 0))
        with pytest.raises(IndexError):
            base.end.isclose((0, 0))


class TestSubPaths:
    def test_empty_path(self):
        paths = NumpyPath2d(None).sub_paths()
        assert len(paths) == 0

    def test_single_path(self, first):
        paths = first.sub_paths()
        assert len(paths) == 1
        assert paths[0] is first

    def test_multipath_of_two(self, first, third):
        multi_path = NumpyPath2d.concatenate([first, third])
        paths = multi_path.sub_paths()
        assert len(paths) == 2
        for p in paths:
            assert p.command_codes() == [1]

        first, second = paths
        vertices = first.vertices()
        assert len(vertices) == 2
        assert vertices[0].isclose((0, 0))
        assert vertices[1].isclose((10, 0))

        vertices = second.vertices()
        assert len(vertices) == 2
        assert vertices[0].isclose((20, 0))
        assert vertices[1].isclose((30, 0))

    def test_multipath_with_curve3(self, first, curve3, third):
        multi_path = NumpyPath2d.concatenate([first, curve3, third])
        paths = multi_path.sub_paths()
        assert len(paths) == 3
        first, second, third = paths
        assert first.command_codes() == [1]
        assert second.command_codes() == [2]
        assert third.command_codes() == [1]

        vertices = first.vertices()
        assert len(vertices) == 2
        assert vertices[0].isclose((0, 0))
        assert vertices[1].isclose((10, 0))

        vertices = second.vertices()
        assert len(vertices) == 3
        assert vertices[0].isclose((0, 0))  # curve3_to, start
        assert vertices[1].isclose((5, 3))  # curve3_to, ctrl
        assert vertices[2].isclose((10, 0))  # curve3_to, end

        vertices = third.vertices()
        assert len(vertices) == 2
        assert vertices[0].isclose((20, 0))
        assert vertices[1].isclose((30, 0))

    def test_multipath_with_curve4(self, curve4, third, first):
        # curve4 and third are connected as a single path
        multi_path = NumpyPath2d.concatenate([curve4, third, first])
        paths = multi_path.sub_paths()
        assert len(paths) == 2
        first, second = paths
        assert first.command_codes() == [3, 1]
        assert second.command_codes() == [1]

        vertices = first.vertices()  # curve3 + third
        assert len(vertices) == 5
        assert vertices[0].isclose((10, 0))  # curve4_to, start
        assert vertices[1].isclose((13, -3))  # curve4_to, ctrl1
        assert vertices[2].isclose((17, 3))  # curve4_to, ctrl2
        assert vertices[3].isclose((20, 0))  # curve4_to, end
        assert vertices[4].isclose((30, 0))  # line_to

        vertices = second.vertices()
        assert len(vertices) == 2
        assert vertices[0].isclose((0, 0))
        assert vertices[1].isclose((10, 0))

    def test_sub_paths_are_reversible(self, first, third):
        multi_path = NumpyPath2d.concatenate([first, third])
        paths = multi_path.sub_paths()
        first, second = paths
        first.reverse()
        vertices = first.vertices()
        assert vertices[0].isclose((10, 0))
        assert vertices[1].isclose((0, 0))


def test_path_conversion_methods():
    source_path = from_vertices(forms.circle(32))
    p0 = Path((2, 0))
    p0.curve3_to((3, 0), (2.5, 1))
    source_path.extend_multi_path(p0)
    p0 = Path((3, 0))
    p0.curve4_to((4, 0), (3.3, -1), (3.7, 1))

    p0 = from_vertices(forms.translate(forms.circle(32)), (5, 0))
    source_path.extend_multi_path(p0)
    assert source_path.has_sub_paths is True
    assert source_path.has_curves is True
    assert source_path.has_lines is True

    converted_path = NumpyPath2d(source_path).to_path()
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
    path = Path()
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
        p = Path()
        p.line_to((1, 0))
        p2 = NumpyPath2d(p).reverse()
        vertices = p2.control_vertices()
        assert close_vectors(vertices, [(1, 0), (0, 0)])

    def test_reversing_one_curve3(self):
        p = Path()
        p.curve3_to((3, 0), (1.5, 1))
        p2 = NumpyPath2d(p).reverse()
        assert close_vectors(p2.control_vertices(), [(3, 0), (1.5, 1), (0, 0)])

    def test_reversing_one_curve4(self):
        p = Path()
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
        p = Path()
        p.line_to((1, 0, 0))
        p.move_to((2, 0, 0))
        p.line_to((3, 0, 0))

        r = NumpyPath2d(p).reverse()
        assert r.has_sub_paths is True
        assert len(r) == 3
        assert r.command_codes() == [1, 4, 1]
        assert r.start == (3, 0, 0)
        assert r.end == (0, 0, 0)

    def test_reversing_multi_path_with_a_move_to_cmd_at_the_end(self):
        p = Path()
        p.line_to((1, 0, 0))
        p.move_to((2, 0, 0))
        # The last move_to will become the first move_to.
        # A move_to as first command just moves the start point.
        r = NumpyPath2d(p).reverse()
        assert len(r) == 1
        assert r.command_codes() == [1]
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
