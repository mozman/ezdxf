#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Callable, Set, Dict, Iterator, Iterable
import random
from collections import defaultdict
import operator
from functools import reduce
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

    def classify(centroids: Iterable[AnyVec]):
        new_clusters: Dict[AnyVec, List[AnyVec]] = defaultdict(list)
        tree = RTree(centroids)
        for point in points:
            nn, _ = tree.nearest_neighbor(point)
            new_clusters[nn].append(point)
        return new_clusters

    def recenter() -> Iterator[AnyVec]:
        for cluster_points in clusters.values():
            yield Vec3.sum(cluster_points) / len(cluster_points)
        if len(clusters) < k:  # refill centroids if required
            yield from random.sample(points, k - len(clusters))

    def is_equal_clustering(old_clusters, new_clusters):
        def hash_list(lst):
            lst.sort()
            return reduce(operator.xor, map(hash, lst))

        h1 = sorted(map(hash_list, old_clusters.values()))
        h2 = sorted(map(hash_list, new_clusters.values()))
        return h1 == h2

    assert k < len(points)
    clusters: Dict[AnyVec, List[AnyVec]] = classify(random.sample(points, k))
    for _ in range(max_iter):
        new_clusters = classify(recenter())
        if is_equal_clustering(clusters, new_clusters):
            break
        clusters = new_clusters
    return list(clusters.values())
