#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

# RTree:
# Immutable spatial search tree based on the SsTree implementation of the book
# "Advanced Algorithms and Data Structures"
# - JS SsTree implementation: https://github.com/mlarocca/AlgorithmsAndDataStructuresInAction/tree/master/JavaScript/src/ss_tree
# - Research paper of Antonin Guttman: http://www-db.deis.unibo.it/courses/SI-LS/papers/Gut84.pdf
#
# To keep things simple the search tree is buildup once in the initialization
# phase and immutable afterwards. Rebuilding the tree after inserting or deleting
# nodes is very costly.

from typing import List, Optional, Iterator, Tuple, Callable, Sequence
import abc
import math

from ezdxf.math import Vec3, BoundingBox

__all__ = ["RTree"]

INF = float("inf")


class Node:
    __slots__ = ("bbox",)

    def __init__(self, bbox: BoundingBox):
        self.bbox = bbox

    @abc.abstractmethod
    def __len__(self):
        ...

    @abc.abstractmethod
    def contains(self, point: Vec3) -> bool:
        ...

    @abc.abstractmethod
    def _nearest_neighbor(
        self, target: Vec3, nn: Vec3 = None, nn_dist: float = INF
    ) -> Tuple[Optional[Vec3], float]:
        ...

    @abc.abstractmethod
    def points_in_sphere(self, center: Vec3, radius: float) -> Iterator[Vec3]:
        ...

    @abc.abstractmethod
    def points_in_bbox(self, bbox: BoundingBox) -> Iterator[Vec3]:
        ...

    def nearest_neighbor(self, target: Vec3) -> Vec3:
        nn = self._nearest_neighbor(target)[0]
        assert (
            nn is not None
        ), "empty tree should be prevented by tree constructor"
        return nn


class LeafNode(Node):
    __slots__ = ("points", "bbox")

    def __init__(self, points: List[Vec3]):
        self.points = tuple(points)
        super().__init__(BoundingBox(self.points))

    def __len__(self):
        return len(self.points)

    def contains(self, point: Vec3) -> bool:
        return any(point.isclose(p) for p in self.points)

    def _nearest_neighbor(
        self, target: Vec3, nn: Vec3 = None, nn_dist: float = INF
    ) -> Tuple[Optional[Vec3], float]:

        distance, point = min((target.distance(p), p) for p in self.points)
        if distance < nn_dist:
            nn, nn_dist = point, distance
        return nn, nn_dist

    def points_in_sphere(self, center: Vec3, radius: float) -> Iterator[Vec3]:
        return (p for p in self.points if center.distance(p) <= radius)

    def points_in_bbox(self, bbox: BoundingBox) -> Iterator[Vec3]:
        return (p for p in self.points if bbox.inside(p))


class InnerNode(Node):
    __slots__ = ("children", "bbox")

    def __init__(self, children: Sequence[Node]):
        super().__init__(BoundingBox())
        self.children = tuple(children)
        for child in self.children:
            # build union of all child bounding boxes
            self.bbox.extend([child.bbox.extmin, child.bbox.extmax])

    def __len__(self):
        return sum(len(c) for c in self.children)

    def contains(self, point: Vec3) -> bool:
        for child in self.children:
            if child.bbox.inside(point) and child.contains(point):
                return True
        return False

    def _nearest_neighbor(
        self, target: Vec3, nn: Vec3 = None, nn_dist: float = INF
    ) -> Tuple[Optional[Vec3], float]:
        def grow_box(box: BoundingBox, dist) -> BoundingBox:
            b = box.copy()
            b.grow(dist)
            return b

        closest_child = _closest_child(self.children, target)
        nn, nn_dist = closest_child._nearest_neighbor(target, nn, nn_dist)
        for child in self.children:
            if child is closest_child:
                continue
            # is target inside the child bounding box + nn_dist in all directions
            if grow_box(child.bbox, nn_dist).inside(target):
                point, distance = child._nearest_neighbor(target, nn, nn_dist)
                if distance < nn_dist:
                    nn = point
                    nn_dist = distance
        return nn, nn_dist

    def points_in_sphere(self, center: Vec3, radius: float) -> Iterator[Vec3]:
        for child in self.children:
            if _is_sphere_intersecting_bbox(
                center, radius, child.bbox.center, child.bbox.size
            ):
                yield from child.points_in_sphere(center, radius)

    def points_in_bbox(self, bbox: BoundingBox) -> Iterator[Vec3]:
        for child in self.children:
            if bbox.has_overlap(child.bbox):
                yield from child.points_in_bbox(bbox)


class RTree:
    __slots__ = ("_root", )

    def __init__(self, points: List[Vec3], max_node_size: int = 5):
        if max_node_size < 2:
            raise ValueError("max node size must be > 1")
        if len(points) == 0:
            raise ValueError("no points given")
        self._root = make_node(points, max_node_size, _box_split)

    def __len__(self):
        return len(self._root)

    def contains(self, point: Vec3) -> bool:
        return self._root.contains(point)

    def nearest_neighbor(self, target: Vec3) -> Vec3:
        return self._root.nearest_neighbor(target)

    def points_in_sphere(self, center: Vec3, radius: float) -> Iterator[Vec3]:
        return self._root.points_in_sphere(center, radius)

    def points_in_bbox(self, bbox: BoundingBox) -> Iterator[Vec3]:
        return self._root.points_in_bbox(bbox)


def make_node(
    points: List[Vec3],
    max_size: int,
    split_strategy: Callable[[List[Vec3], int], Sequence[Node]],
) -> Node:
    if len(points) > max_size:
        return InnerNode(split_strategy(points, max_size))
    else:
        return LeafNode(points)


def _box_split(points: List[Vec3], max_size: int) -> Sequence[Node]:
    n = len(points)
    size = BoundingBox(points).size.xyz
    dim = size.index(max(size))
    points = sorted(points, key=lambda vec: vec[dim])
    k = math.ceil(n / max_size)
    return tuple(
        make_node(points[i : i + k], max_size, _box_split)
        for i in range(0, n, k)
    )


def _is_sphere_intersecting_bbox(
    centroid: Vec3, radius: float, center: Vec3, size: Vec3
) -> bool:
    distance = centroid - center
    intersection_distance = size * 0.5 + Vec3(radius, radius, radius)
    # non-intersection is more often likely:
    if abs(distance.x) > intersection_distance.x:
        return False
    if abs(distance.y) > intersection_distance.y:
        return False
    if abs(distance.z) > intersection_distance.z:
        return False
    return True


def _closest_child(children: Sequence[Node], point: Vec3) -> Node:
    assert len(children) > 0
    _, node = min(
        (point.distance(child.bbox.center), child) for child in children
    )
    return node
