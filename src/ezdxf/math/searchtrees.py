#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

# Immutable Spatial Search Trees:
# - SsTree: based on the JS algorithm in "Advanced Algorithms and Data Structures"
#   https://github.com/mlarocca/AlgorithmsAndDataStructuresInAction/tree/master/JavaScript/src/ss_tree
# - RTree: adaptation of SsTree to use rectangular boxes to store vertices
#   Further information: http://www-db.deis.unibo.it/courses/SI-LS/papers/Gut84.pdf
#
# To keep things simple the search tree is buildup once in the initialization
# phase and immutable afterwards. Rebuilding the tree after inserting or deleting
# nodes is very costly.

from typing import (
    List,
    Optional,
    Sequence,
    Iterator,
    Tuple,
    Callable,
    TypeVar,
    Type,
)
import abc
import math
import statistics

from ezdxf.math import Vec3, NULLVEC, BoundingBox

__all__ = ["AbstractSearchTree", "SsTree", "RTree"]

INF = float("inf")


class AbstractNode(abc.ABC):
    @abc.abstractmethod
    def __len__(self):
        ...

    @abc.abstractmethod
    def contains(self, point: Vec3) -> bool:
        ...

    @abc.abstractmethod
    def nearest_neighbour(self, target: Vec3) -> Vec3:
        ...

    @abc.abstractmethod
    def points_in_sphere(self, center: Vec3, radius: float) -> Iterator[Vec3]:
        ...

    @abc.abstractmethod
    def points_in_bbox(self, bbox: BoundingBox) -> Iterator[Vec3]:
        ...


class AbstractSearchTree(abc.ABC):
    _root: AbstractNode

    def __len__(self):
        return len(self._root)

    def contains(self, point: Vec3) -> bool:
        return self._root.contains(point)

    def nearest_neighbour(self, target: Vec3) -> Vec3:
        return self._root.nearest_neighbour(target)

    def points_in_sphere(self, center: Vec3, radius: float) -> Iterator[Vec3]:
        return self._root.points_in_sphere(center, radius)

    def points_in_bbox(self, bbox: BoundingBox) -> Iterator[Vec3]:
        return self._root.points_in_bbox(bbox)


class SNode(AbstractNode):
    __slots__ = ("_children", "_points", "centroid", "radius")

    def __init__(
        self,
        points: List[Vec3],
        max_size: int,
        split_strategy: Callable,
    ):
        self._children: Optional[List["SNode"]] = None
        self._points: Optional[List[Vec3]] = None
        self.centroid: Vec3 = NULLVEC
        self.radius: float = 0.0
        if len(points) > max_size:
            self.set_children(split_strategy(points, max_size, SNode))
        else:
            self.set_points(points.copy())

    def __len__(self):
        if self._children:
            return sum(len(c) for c in self._children)
        return len(self.points)

    @property
    def is_leaf(self) -> bool:
        return self._children is None

    @property
    def children(self) -> List["SNode"]:
        if self._children is None:
            return []
        return self._children

    def set_children(self, children: List["SNode"]) -> None:
        """Set inner node content."""
        self._children = children
        points = list(self.iter_points())
        if len(points):
            self.centroid, self.radius = _get_sphere_params(points)

    @property
    def points(self) -> List[Vec3]:
        if self._points is None:
            return []
        return self._points

    def set_points(self, points: List[Vec3]) -> None:
        """Set leaf node content."""
        self._points = points
        if len(points):
            self.centroid, self.radius = _get_sphere_params(points)

    def iter_points(self) -> Iterator[Vec3]:
        if self._points is not None:
            yield from self._points
        else:
            for child in self.children:
                yield from child.iter_points()

    def contains(self, point: Vec3) -> bool:
        if self.is_leaf:
            return any(point.isclose(p) for p in self.points)
        else:
            for child in self.children:
                if point.distance(
                    child.centroid
                ) <= child.radius and child.contains(point):
                    return True
        return False

    def nearest_neighbour(self, target: Vec3) -> Vec3:
        nn = self._nearest_neighbour(target)[0]
        assert (
            nn is not None
        ), "empty tree should be prevented by tree constructor"
        return nn

    def _nearest_neighbour(
        self, target: Vec3, nn: Vec3 = None, nn_dist: float = INF
    ) -> Tuple[Optional[Vec3], float]:
        if self.is_leaf:
            points = self.points
            if len(points):
                distance, point = min((target.distance(p), p) for p in points)
                if distance < nn_dist:
                    nn, nn_dist = point, distance
        elif self._children is not None:
            children = self._children
            closest_child = _st_closest_child(children, target)
            nn, nn_dist = closest_child._nearest_neighbour(target, nn, nn_dist)
            for child in children:
                if child is closest_child:
                    continue
                if target.distance(child.centroid) - child.radius < nn_dist:
                    point, distance = child._nearest_neighbour(
                        target, nn, nn_dist
                    )
                    if distance < nn_dist:
                        nn = point
                        nn_dist = distance
        return nn, nn_dist

    def points_in_sphere(self, center: Vec3, radius: float) -> Iterator[Vec3]:
        if self.is_leaf:
            for p in self.points:
                if center.distance(p) <= radius:
                    yield p
        else:
            for child in self.children:
                if center.distance(child.centroid) - child.radius <= radius:
                    yield from child.points_in_sphere(center, radius)

    def points_in_bbox(self, bbox: BoundingBox) -> Iterator[Vec3]:
        if self.is_leaf:
            for p in self.points:
                if bbox.inside(p):
                    yield p
        else:
            bbox_center = bbox.center
            bbox_size = bbox.size
            for child in self.children:
                if _is_sphere_intersecting_bbox(
                    child.centroid, child.radius, bbox_center, bbox_size
                ):
                    yield from child.points_in_bbox(bbox)


class SsTree(AbstractSearchTree):
    def __init__(self, points: List[Vec3], max_node_size: int = 5):
        if max_node_size < 2:
            raise ValueError("max node size must be > 1")
        if len(points) == 0:
            raise ValueError("no points given")
        self._root = SNode(points, max_node_size, _box_split)


class RNode(AbstractNode):
    __slots__ = ("_children", "_points", "_bbox")

    def __init__(
        self,
        points: List[Vec3],
        max_size: int,
        split_strategy: Callable,
    ):
        self._children: Optional[List["RNode"]] = None
        self._points: Optional[List[Vec3]] = None
        self.bbox = BoundingBox()
        if len(points) > max_size:
            self.set_children(split_strategy(points, max_size, RNode))
        else:
            self.set_points(points.copy())

    def __len__(self):
        if self._children:
            return sum(len(c) for c in self._children)
        return len(self.points)

    @property
    def is_leaf(self) -> bool:
        return self._children is None

    @property
    def children(self) -> List["RNode"]:
        if self._children is None:
            return []
        return self._children

    def set_children(self, children: List["RNode"]) -> None:
        """Set inner node content."""
        self._children = children
        self.bbox = BoundingBox()
        for child in children:
            # build union of all child bounding boxes
            self.bbox.extend([child.bbox.extmin, child.bbox.extmax])

    @property
    def points(self) -> List[Vec3]:
        if self._points is None:
            return []
        return self._points

    def set_points(self, points: List[Vec3]) -> None:
        """Set leaf node content."""
        self._points = points
        self.bbox = BoundingBox(points)

    def contains(self, point: Vec3) -> bool:
        if self.is_leaf:
            return any(point.isclose(p) for p in self.points)
        else:
            for child in self.children:
                if child.bbox.inside(point) and child.contains(point):
                    return True
        return False

    def nearest_neighbour(self, target: Vec3) -> Vec3:
        nn = self._nearest_neighbour(target)[0]
        assert (
            nn is not None
        ), "empty tree should be prevented by tree constructor"
        return nn

    def _nearest_neighbour(
        self, target: Vec3, nn: Vec3 = None, nn_dist: float = INF
    ) -> Tuple[Optional[Vec3], float]:
        def grow_box(box: BoundingBox, dist) -> BoundingBox:
            b = box.copy()
            b.grow(dist)
            return b

        if self.is_leaf:
            points = self.points
            if len(points):
                distance, point = min((target.distance(p), p) for p in points)
                if distance < nn_dist:
                    nn, nn_dist = point, distance
        elif self._children is not None:
            children = self._children
            closest_child = _rt_closest_child(children, target)
            nn, nn_dist = closest_child._nearest_neighbour(target, nn, nn_dist)
            for child in children:
                if child is closest_child:
                    continue
                # is target inside the child bounding box + nn_dist in all directions
                if grow_box(child.bbox, nn_dist).inside(target):
                    point, distance = child._nearest_neighbour(
                        target, nn, nn_dist
                    )
                    if distance < nn_dist:
                        nn = point
                        nn_dist = distance
        return nn, nn_dist

    def points_in_sphere(self, center: Vec3, radius: float) -> Iterator[Vec3]:
        if self.is_leaf:
            for p in self.points:
                if center.distance(p) <= radius:
                    yield p
        else:
            for child in self.children:
                if _is_sphere_intersecting_bbox(
                    center, radius, child.bbox.center, child.bbox.size
                ):
                    yield from child.points_in_sphere(center, radius)

    def points_in_bbox(self, bbox: BoundingBox) -> Iterator[Vec3]:
        if self.is_leaf:
            for p in self.points:
                if bbox.inside(p):
                    yield p
        else:
            for child in self.children:
                if bbox.has_overlap(child.bbox):
                    yield from child.points_in_bbox(bbox)


class RTree(AbstractSearchTree):
    def __init__(self, points: List[Vec3], max_node_size: int = 5):
        if max_node_size < 2:
            raise ValueError("max node size must be > 1")
        if len(points) == 0:
            raise ValueError("no points given")
        self._root = RNode(points, max_node_size, _box_split)


T = TypeVar("T")


def _variant_split(points: List[Vec3], max_size: int, cls: Type[T]) -> List[T]:
    """Slower split strategy"""
    n = len(points)
    variances: Sequence[float] = _point_variances(points)
    dim = variances.index(max(variances))
    points = sorted(points, key=lambda vec: vec[dim])
    k = math.ceil(n / max_size)
    children: List[T] = [
        cls(points[i : i + k], max_size, _variant_split) for i in range(0, n, k)  # type: ignore
    ]
    return children


def _box_split(points: List[Vec3], max_size: int, cls: Type[T]) -> List[T]:
    """Faster split strategy"""
    n = len(points)
    size = BoundingBox(points).size.xyz
    dim = size.index(max(size))
    points = sorted(points, key=lambda vec: vec[dim])
    k = math.ceil(n / max_size)
    children: List[T] = [
        cls(points[i : i + k], max_size, _box_split) for i in range(0, n, k)  # type: ignore
    ]
    return children


def _point_variances(points: Sequence[Vec3]) -> Sequence[float]:
    if len(points) > 1:
        x_var = statistics.variance(v.x for v in points)
        y_var = statistics.variance(v.y for v in points)
        z_var = statistics.variance(v.z for v in points)
        return x_var, y_var, z_var
    return 0.0, 0.0, 0.0


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


def _get_sphere_params(points: List[Vec3]) -> Tuple[Vec3, float]:
    assert len(points) > 0
    centroid = Vec3.sum(points) / len(points)
    radius = max(centroid.distance(p) for p in points)
    return centroid, radius


def _st_closest_child(children: List[SNode], point: Vec3) -> SNode:
    assert len(children) > 0
    _, node = min((point.distance(child.centroid), child) for child in children)
    return node


def _rt_closest_child(children: List[RNode], point: Vec3) -> RNode:
    assert len(children) > 0
    _, node = min(
        (point.distance(child.bbox.center), child) for child in children
    )
    return node
