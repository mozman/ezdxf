#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

# based on the JS algorithm in "Advanced Algorithms and Data Structures"
# https://github.com/mlarocca/AlgorithmsAndDataStructuresInAction/tree/master/JavaScript/src/ss_tree


from typing import List, Optional, Sequence, Iterator, Iterable, Tuple
import math

from ezdxf.math import Vec3, NULLVEC, BoundingBox
import statistics

__all__ = ["SsTree"]

INF = float("inf")


class Node:
    __slots__ = ("_children", "_points", "centroid", "radius")

    def __init__(self, points: List[Vec3], max_size: int):
        self._children: Optional[List["Node"]] = None
        self._points: Optional[List[Vec3]] = None
        self.centroid: Vec3 = NULLVEC
        self.radius: float = 0.0
        if len(points) > max_size:
            self.set_children(_split_points(points, max_size))
        else:
            self.set_points(points.copy())

    @classmethod
    def internal_node(cls, children: List["Node"], max_size) -> "Node":
        assert len(children) <= max_size, "invalid children count"
        node = cls([], max_size)
        node.set_children(children)
        return node

    def __len__(self):
        count: int = 0
        if self._points:
            count = len(self._points)
        if self._children:
            count += sum(len(c) for c in self._children)
        return count

    @property
    def is_leaf(self) -> bool:
        return self._children is None

    @property
    def children(self) -> List["Node"]:
        if self._children is None:
            return []
        return self._children

    def set_children(self, children: List["Node"]) -> None:
        self._points = None  # its an inner node
        self._children = children
        points = list(self.iter_points())
        if len(points):
            self.centroid, self.radius = _get_sphere_params(points)
            return
        self.centroid = NULLVEC
        self.radius = 0.0

    @property
    def points(self) -> List[Vec3]:
        if self._points is None:
            return []
        return self._points

    def set_points(self, points: List[Vec3]) -> None:
        self._children = None  # its a leaf
        self._points = points
        if len(points):
            self.centroid, self.radius = _get_sphere_params(points)
            return
        self.centroid = NULLVEC
        self.radius = 0.0

    def clear_points(self):
        self._points = None
        self.centroid = NULLVEC
        self.radius = 0.0

    def contains(self, point: Vec3) -> bool:
        if self.is_leaf:
            return any(point.isclose(p) for p in self.points)
        else:
            for child in self.children:
                if point.distance(child.centroid) <= child.radius:
                    return child.contains(point)
        return False

    def add(self, point: Vec3, max_size: int, is_root=False) -> List["Node"]:
        new_nodes: List[Node] = []
        if self.is_leaf:
            points = self.points
            points.append(point)
            if len(points) > max_size:
                self.clear_points()  # moving points into sub-nodes
                if is_root:
                    self.set_children(_split_points(points, max_size))
                else:
                    new_nodes = _split_points(points, max_size)
            else:
                self.set_points(points)
        else:
            # internal node no need to update point stats!
            index = self.closest_child_index(point)
            children = self.children
            closest_child = children[index]
            resulting_nodes = closest_child.add(point, max_size)
            if len(resulting_nodes):
                children.pop(index)
                children.extend(resulting_nodes)
                if len(children) > max_size:
                    new_nodes = _split_children(children, max_size)
                    if is_root:
                        self.set_children(new_nodes)
                        new_nodes = []
                else:  # update of centroid and radius is required
                    self.set_children(children)
            else:  # update of centroid and radius is required
                self.set_children(children)
        return new_nodes

    def nearest_neighbour(
        self, target: Vec3, nn: Vec3 = None, nn_dist: float = INF
    ) -> Tuple[Optional[Vec3], float]:
        if self.is_leaf:
            points = self.points
            if len(points):
                point, distance = _min_distance(points, target)
                if distance < nn_dist:
                    nn, nn_dist = point, distance
        elif self._children is not None:
            children = self._children
            closest_child = children[self.closest_child_index(target)]
            nn, nn_dist = closest_child.nearest_neighbour(target, nn, nn_dist)
            for child in children:
                if child is closest_child:
                    continue
                if target.distance(child.centroid) - child.radius < nn_dist:
                    point, distance = child.nearest_neighbour(
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

    def closest_child_index(self, point: Vec3) -> int:
        min_distance: float = INF
        min_index: int = 0
        for index, child in enumerate(self.children):
            distance = point.distance(child.centroid)
            if distance < min_distance:
                min_distance = distance
                min_index = index
        return min_index

    def iter_points(self) -> Iterator[Vec3]:
        if self._points is not None:
            yield from self._points
        else:
            for child in self.children:
                yield from child.iter_points()


class SsTree:
    def __init__(self, points: List[Vec3], max_node_size: int = 5):
        self.root: Node = Node(points, max_node_size)
        if max_node_size < 2:
            raise ValueError("max node size must be > 1")
        self.max_node_size = max_node_size

    def __len__(self):
        return len(self.root)

    def contains(self, point: Vec3) -> bool:
        return self.root.contains(point)

    def add(self, point: Vec3):
        if not self.root.contains(point):
            self.root.add(point, self.max_node_size, is_root=True)

    def extend(self, points: Iterable[Vec3]):
        for point in points:
            self.add(point)

    def nearest_neighbour(self, target: Vec3) -> Optional[Vec3]:
        return self.root.nearest_neighbour(target)[0]

    def points_in_sphere(self, center: Vec3, radius: float) -> Iterator[Vec3]:
        return self.root.points_in_sphere(center, radius)

    def points_in_bbox(self, bbox: BoundingBox) -> Iterator[Vec3]:
        return self.root.points_in_bbox(bbox)

    def iter_points(self) -> Iterator[Vec3]:
        return self.root.iter_points()


def _split_points(points: List[Vec3], max_size: int) -> List[Node]:
    assert max_size > 1
    n = len(points)
    assert n > max_size
    variances: Sequence[float] = _point_variances(points)
    dim = variances.index(max(variances))
    points = sorted(points, key=lambda vec: vec[dim])
    k = math.ceil(n / max_size)
    children: List[Node] = [
        Node(points[i : i + k], max_size) for i in range(0, n, k)
    ]
    return children


def _split_children(children: List[Node], max_size: int) -> List[Node]:
    assert max_size > 1
    n = len(children)
    centroids = [child.centroid for child in children]
    variances = _point_variances(centroids)
    dim = variances.index(max(variances))
    sorted_children = sorted(children, key=lambda child: child.centroid[dim])
    k = math.ceil(n / max_size)
    nodes: List[Node] = [
        Node.internal_node(sorted_children[i : i + k], max_size)
        for i in range(0, n, k)
    ]
    return nodes


def _point_variances(points: Sequence[Vec3]) -> Sequence[float]:
    if len(points) > 1:
        x_var = statistics.variance((v.x for v in points))
        y_var = statistics.variance((v.y for v in points))
        z_var = statistics.variance((v.z for v in points))
        return x_var, y_var, z_var
    return 0.0, 0.0, 0.0


def _min_distance(points: Iterable[Vec3], target: Vec3) -> Tuple[Vec3, float]:
    min_distance = INF
    min_point = target
    for p in points:
        distance = target.distance(p)
        if distance < min_distance:
            min_distance = distance
            min_point = p
    return min_point, min_distance


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
