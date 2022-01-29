#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.math import Vec3, SsTree
from ezdxf.math.sstree import _min_distance, _point_variances, _split_points


def test_empty_tree():
    tree = SsTree([])
    assert len(tree) == 0


class TestFirstLevel:
    def test_add_point(self):
        tree = SsTree([])
        tree.add(Vec3())
        assert len(tree) == 1

    def test_add_two_points(self):
        tree = SsTree([])
        tree.add(Vec3(1, 2, 3))
        tree.add(Vec3(3, 2, 1))
        assert len(tree) == 2

    def test_reject_adding_existing_point(self):
        """SsTree stores only unique points."""
        tree = SsTree([])
        p = Vec3(1, 2, 3)
        tree.add(p)
        tree.add(p)
        assert len(tree) == 1


class TestSplitPoints:
    def test_max_node_size_must_be_gt_1(self):
        with pytest.raises(AssertionError):
            _split_points([], 1)

    def test_point_count_gt_max_node_size(self):
        with pytest.raises(AssertionError):
            _split_points([], 2)

    def test_four_points(self):
        points = Vec3.list([(0, 0), (10, 0), (0, 10), (10, 20)])
        n1, n2 = _split_points(points, 2)
        assert len(n1) == 2
        assert len(n2) == 2

    def test_100_points(self):
        Vec3.random()
        points = [Vec3.random(100) for _ in range(100)]
        nodes = _split_points(points, 5)
        assert len(nodes) == 5
        for node in nodes:
            assert len(node) == 20
            assert len(node.children) == 5
            assert len(node.points) == 0


def test_point_variances():
    points = Vec3.list([(0, 0), (10, 0), (0, 10), (10, 20)])
    x, y, z = _point_variances(points)
    assert x == pytest.approx(33.333333333)
    assert y == pytest.approx(91.666666667)
    assert z == 0.0


def test_point_variances_for_less_than_2_points():
    assert _point_variances([]) == (0.0, 0.0, 0.0)
    assert _point_variances([Vec3(1, 2, 3)]) == (0.0, 0.0, 0.0)


def test_min_distance():
    points = Vec3.list([(0, 0), (10, 0), (0, 10), (10, 20)])
    for index in range(len(points)):
        target = points[index] + (1.5, 0)
        p1, distance = _min_distance(points, target)
        assert p1 is points[index]
        assert distance == pytest.approx(1.5)


if __name__ == "__main__":
    pytest.main([__file__])
