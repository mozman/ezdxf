#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.math import Vec3, SsTree, BoundingBox
from ezdxf.math.searchtrees import (
    _min_distance,
    _point_variances,
    _st_split_points,
)


def test_empty_tree():
    tree = SsTree([])
    assert len(tree) == 0


class TestFirstLevel:
    def test_from_one_point(self):
        tree = SsTree([Vec3(1, 2, 3)])
        assert len(tree) == 1

    def test_contains_point(self):
        point = Vec3(1, 2, 3)
        tree = SsTree([point])
        assert tree.contains(point)

    def test_from_two_points(self):
        tree = SsTree([Vec3(1, 2, 3), Vec3(3, 2, 1)])
        assert len(tree) == 2

    def test_store_duplicate_points(self):
        p = Vec3(1, 2, 3)
        tree = SsTree([p, p])
        assert len(tree) == 2


class TestBiggerTree:
    @pytest.fixture(scope="class")
    def tree(self):
        return SsTree([Vec3(x, 0, 0) for x in range(100)], max_node_size=5)

    def test_setup_is_correct(self, tree):
        assert len(tree) == 100

    @pytest.mark.parametrize(
        "point", [Vec3(0, 0, 0), Vec3(1, 0, 0), Vec3(99, 0, 0)]
    )
    def test_known_point_is_present(self, tree, point):
        assert tree.contains(point) is True

    @pytest.mark.parametrize(
        "n, point",
        [
            (Vec3(0.1, 0, 0), Vec3(0, 0, 0)),
            (Vec3(1, 0.1, 0), Vec3(1, 0, 0)),
            (Vec3(99, 0, 0.1), Vec3(99, 0, 0)),
        ],
    )
    def test_nearest_neighbour(self, tree, n, point):
        assert tree.nearest_neighbour(n).isclose(point)

    def test_find_points_in_sphere(self, tree):
        points = list(tree.points_in_sphere(Vec3(50, 0, 0), radius=5))
        assert len(points) == 11
        expected_x_coords = set(range(45, 56))
        x_coords = set(int(p.x) for p in points)
        assert x_coords == expected_x_coords

    def test_find_points_in_bbox(self, tree):
        bbox = BoundingBox([(45, 0, 0), (55, 0, 0)])
        points = list(tree.points_in_bbox(bbox))
        assert len(points) == 11
        expected_x_coords = set(range(45, 56))
        x_coords = set(int(p.x) for p in points)
        assert x_coords == expected_x_coords


class TestSplitPoints:
    def test_max_node_size_must_be_gt_1(self):
        with pytest.raises(AssertionError):
            _st_split_points([], 1)

    def test_point_count_gt_max_node_size(self):
        with pytest.raises(AssertionError):
            _st_split_points([], 2)

    def test_four_points(self):
        points = Vec3.list([(0, 0), (10, 0), (0, 10), (10, 20)])
        n1, n2 = _st_split_points(points, 2)
        assert len(n1) == 2
        assert len(n2) == 2

    def test_100_points(self):
        Vec3.random()
        points = [Vec3.random(100) for _ in range(100)]
        nodes = _st_split_points(points, 5)
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
