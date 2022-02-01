#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Callable, Set, Dict
import random
from collections import defaultdict
from ezdxf.math import AnyVec, RTree, Vec3


__all__ = ["dbscan", "k_means"]


SearchFunc = Callable[[AnyVec, float], Set[AnyVec]]


def dbscan(
    points: List[AnyVec],
    *,
    radius: float,
    min_points: int = 4,
    rtree: RTree = None,
    max_node_size: int = 5,
) -> List[List[AnyVec]]:
    """DBSCAN clustering.

    Args:
        points: list of points to cluster
        radius: radius of the dense regions
        min_points: minimum number of points that needs to be within the
            `radius` for a point to be a core point (must be >= 2)
        rtree: optional RTree
        max_node_size: max node size for internally created RTree

    """
    if min_points < 2:
        raise ValueError("min_points must be >= 2")
    if rtree is None:
        rtree = RTree(points, max_node_size)

    clusters: List[Set[AnyVec]] = []
    point_set = set(points)
    while len(point_set):
        point = point_set.pop()
        todo = {point}
        cluster = {point}  # the cluster has only a single entry if noise
        clusters.append(cluster)
        while len(todo):
            chk_point = todo.pop()
            neighbors = set(rtree.points_in_sphere(chk_point, radius))
            if len(neighbors) < min_points:
                continue
            cluster.add(chk_point)
            point_set.discard(chk_point)
            todo |= neighbors.intersection(point_set)

    return [list(cluster) for cluster in clusters]


def k_means(
    points: List[AnyVec], k: int, max_iter: int = 10
) -> List[List[AnyVec]]:
    """K-means clustering.

    Args:
        points: list of points to cluster
        k: number of clusters
        max_iter: max iterations

    """

    def classify(centroids):
        clusters: Dict[AnyVec, Set[AnyVec]] = defaultdict(set)
        tree = RTree(centroids)
        for point in points:
            nn, _ = tree.nearest_neighbor(point)
            clusters[nn].add(point)
        return clusters

    def recenter():
        for points in clusters.values():
            if len(points):
                yield Vec3.sum(points) / len(points)

    assert k < len(points)
    centroids = set(random.sample(points, k))
    clusters = classify(centroids)
    for _ in range(max_iter):
        centroids = set(recenter())
        counter = 0
        while len(centroids) < k and counter < 16:
            counter += 1
            centroids.add(random.choice(points))
        clusters = classify(centroids)
        # todo: break if new clusters are unchanged
    return [list(p) for p in clusters.values()]
