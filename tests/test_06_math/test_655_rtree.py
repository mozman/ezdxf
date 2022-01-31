#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.math import Vec3, RTree, BoundingBox
from ezdxf.math.rtree import box_split, InnerNode


def test_can_not_build_empty_tree():
    with pytest.raises(ValueError):
        RTree([])


class TestFirstLevel:
    def test_from_one_point(self):
        tree = RTree([Vec3(1, 2, 3)])
        assert len(tree) == 1

    def test_contains_point(self):
        point = Vec3(1, 2, 3)
        tree = RTree([point])
        assert tree.contains(point)

    def test_from_two_points(self):
        tree = RTree([Vec3(1, 2, 3), Vec3(3, 2, 1)])
        assert len(tree) == 2

    def test_store_duplicate_points(self):
        p = Vec3(1, 2, 3)
        tree = RTree([p, p])
        assert len(tree) == 2


class TestBiggerTree:
    @pytest.fixture(scope="class")
    def tree(self):
        return RTree([Vec3(x, 0, 0) for x in range(100)], max_node_size=5)

    def test_setup_is_correct(self, tree):
        assert len(tree) == 100

    @pytest.mark.parametrize(
        "point", [Vec3(0, 0, 0), Vec3(1, 0, 0), Vec3(99, 0, 0)]
    )
    def test_known_point_is_present(self, tree, point):
        assert tree.contains(point) is True

    def test_contains_all_random_points(self):
        points = [Vec3.random(50) for _ in range(100)]
        tree = RTree(points, 5)
        for point in points:
            assert tree.contains(point) is True

    @pytest.mark.parametrize(
        "n, point",
        [
            (Vec3(0.1, 0, 0), Vec3(0, 0, 0)),
            (Vec3(1, 0.1, 0), Vec3(1, 0, 0)),
            (Vec3(99, 0, 0.1), Vec3(99, 0, 0)),
        ],
    )
    def test_nearest_neighbor(self, tree, n, point):
        assert tree.nearest_neighbor(n).isclose(point)

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


@pytest.mark.parametrize("strategy", [box_split])
def test_split_strategies(strategy):
    Vec3.random()
    points = [Vec3.random(100) for _ in range(100)]
    nodes = strategy(points, 5)
    assert len(nodes) == 5
    for node in nodes:
        assert len(node) == 20
        assert isinstance(node, InnerNode) is True
        assert len(node.children) == 5


if __name__ == "__main__":
    pytest.main([__file__])
