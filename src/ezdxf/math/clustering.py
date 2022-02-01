#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Callable, Set
from ezdxf.math import AnyVec, RTree


__all__ = ["dbscan", "dbscan_rt"]


SearchFunc = Callable[[AnyVec, float], Set[AnyVec]]


def dbscan(
    points: List[AnyVec],
    *,
    radius: float,
    search_func: SearchFunc,
    min_points: int = 4,
) -> List[List[AnyVec]]:
    """DBSCAN clustering.

    Args:
        points: list of points to cluster
        radius: radius of the dense regions
        search_func: function to search points in the spherical envelope
            defined by the given center and radius
        min_points: minimum number of points that needs to be within the
            `radius` for a point to be a core point (must be >= 2)

    """
    if min_points < 2:
        raise ValueError("min_points must be >= 2")

    clusters: List[Set[AnyVec]] = []
    done: Set[AnyVec] = set()

    for point in points:
        if point in done:
            continue
        done.add(point)
        todo = {point}
        cluster: Set[AnyVec] = {point}
        clusters.append(cluster)
        while len(todo) > 0:
            chk_point = todo.pop()
            neighbors = search_func(chk_point, radius)
            if len(neighbors) < min_points:
                continue
            cluster.add(chk_point)
            done.add(chk_point)
            todo |= neighbors - done
    return [list(cluster) for cluster in clusters]


def dbscan_rt(
    points: List[AnyVec],
    *,
    radius: float,
    min_points: int = 4,
    rtree: RTree = None,
    max_node_size: int = 5,
) -> List[List[AnyVec]]:
    """DBSCAN clustering using an given or otherwise automatically created
    :class:`RTree` as spatial search tree.

    Args:
        points: list of points to cluster
        radius: radius of the dense regions
        min_points: minimum number of points that needs to be within the
            `radius` for a point to be a core point (must be >= 2)
        rtree: optional RTree
        max_node_size: max node size for internally created RTree

    """
    if rtree is None:
        rtree = RTree(points, max_node_size)
    return dbscan(
        points,
        radius=radius,
        search_func=rtree_search_func(rtree),
        min_points=min_points,
    )


def rtree_search_func(tree: "RTree") -> SearchFunc:
    def search(center: AnyVec, radius: float) -> Set[AnyVec]:
        return set(tree.points_in_sphere(center, radius))

    return search
