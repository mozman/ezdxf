# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import time
from pathlib import Path
from ezdxf.math import SsTree, Vec3, closest_point, RTree
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

DIR = Path("~/Desktop/Outbox").expanduser()


def random_points(n, size=1.0):
    return [Vec3.random() * size for _ in range(n)]


def profile_build_time_random_ss_tree(count: int, points, max_node_size: int):
    for _ in range(count):
        SsTree(points, max_node_size)


def profile_build_time_random_rtree(count: int, points, max_node_size: int):
    for _ in range(count):
        RTree(points, max_node_size)


def profile_tree_contains_points(count, tree, points):
    for _ in range(count):
        for point in points:
            assert tree.contains(point) is True


def profile_tree_nearest_neighbour(count, tree, points):
    for _ in range(count):
        for point in points:
            assert isinstance(tree.nearest_neighbour(point), Vec3)


def brute_force_contains(points, point):
    for p in points:
        if p.isclose(point):
            return True
    return False


def profile_brute_force_contains_points(count, points):
    for _ in range(count):
        for point in points:
            assert brute_force_contains(points, point) is True


def profile_brute_force_closest_point(count, points, search_points):
    for _ in range(count):
        for point in search_points:
            assert isinstance(closest_point(point, points), Vec3)


def profile(func, *args):
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    delta = t1 - t0
    return delta


def profile_sstree_building(repeat: int, max_size: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        name = f"SsTree({size}, {max_size})"
        t0 = profile(
            profile_build_time_random_ss_tree, repeat, points, max_size
        )
        time_str = f"{t0:6.2f}s"
        print(f"Build random {name}, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_rtree_building(repeat: int, max_size: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        name = f"RTree({size}, {max_size})"
        t0 = profile(
            profile_build_time_random_rtree, repeat, points, max_size
        )
        time_str = f"{t0:6.2f}s"
        print(f"Build random {name}, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_sstree_contains_all_points(repeat: int, max_size: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        tree = SsTree(points, max_size)
        name = f"SsTree({size}, {max_size})"
        t0 = profile(
            profile_tree_contains_points, repeat, tree, points
        )
        time_str = f"{t0:6.2f}s"
        print(f"{name} contains all points, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_rtree_contains_all_points(repeat: int, max_size: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        tree = RTree(points, max_size)
        name = f"RTree({size}, {max_size})"
        t0 = profile(
            profile_tree_contains_points, repeat, tree, points
        )
        time_str = f"{t0:6.2f}s"
        print(f"{name} contains all points, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_sstree_nearest_neighbour(repeat: int, max_size: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        tree = SsTree(points, max_size)
        name = f"SsTree({size}, {max_size})"

        search_points = random_points(100, 50.0)
        t0 = profile(
            profile_tree_nearest_neighbour, repeat, tree, search_points
        )
        time_str = f"{t0:6.2f}s"
        print(f"{name} nearest neighbour, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_rtree_nearest_neighbour(repeat: int, max_size: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        tree = RTree(points, max_size)
        name = f"RTree({size}, {max_size})"

        search_points = random_points(100, 50.0)
        t0 = profile(
            profile_tree_nearest_neighbour, repeat, tree, search_points
        )
        time_str = f"{t0:6.2f}s"
        print(f"{name} nearest neighbour, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_brute_force_contains_all_points(repeat: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)

        name = f"Brute Force({size})"
        t0 = profile(
            profile_brute_force_contains_points, repeat, points
        )
        time_str = f"{t0:6.2f}s"
        print(f"{name} contains all points, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_brute_force_nearest_neighbour(repeat: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        name = f"Brute Force({size})"

        search_points = random_points(100, 50.0)
        t0 = profile(
            profile_brute_force_closest_point, repeat, points, search_points
        )
        time_str = f"{t0:6.2f}s"
        print(f"{name} contains all points, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def show_log(log, name: str):
    x = []
    y = []
    for size, t0 in log:
        x.append(size)
        y.append(t0)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set(
        xlabel="Size",
        ylabel="Time",
        title=name,
    )
    ax.grid()
    plt.show()


PROFILE_SSTREE_BUILD = False
PROFILE_SSTREE_CONTAINS = False
PROFILE_SSTREE_NEIGHBOUR = True

PROFILE_RTREE_BUILD = False
PROFILE_RTREE_CONTAINS = False
PROFILE_RTREE_NEIGHBOUR = True

PROFILE_BRUTE_FORCE_CONTAINS = False
PROFILE_BRUTE_FORCE_NEIGHBOUR = False

if __name__ == "__main__":
    max_size = 5
    if PROFILE_SSTREE_BUILD:
        log = profile_sstree_building(10, max_size)
        if plt:
            show_log(log, f"Build Random SsTree, max node size={max_size}")
    if PROFILE_RTREE_BUILD:
        log = profile_rtree_building(10, max_size)
        if plt:
            show_log(log, f"Build Random RTree, max node size={max_size}")
    if PROFILE_SSTREE_CONTAINS:
        log = profile_sstree_contains_all_points(10, max_size)
        if plt:
            show_log(log, f"Random SsTree contains all points, max node size={max_size}")
    if PROFILE_RTREE_CONTAINS:
        log = profile_rtree_contains_all_points(10, max_size)
        if plt:
            show_log(log, f"Random RTree contains all points, max node size={max_size}")
    if PROFILE_BRUTE_FORCE_CONTAINS:
        log = profile_brute_force_contains_all_points(10)
        if plt:
            show_log(log, f"Brute force contains all points")
    if PROFILE_SSTREE_NEIGHBOUR:
        log = profile_sstree_nearest_neighbour(10, max_size)
        if plt:
            show_log(log, f"Random SsTree nearest neighbour, max node size={max_size}")
    if PROFILE_RTREE_NEIGHBOUR:
        log = profile_rtree_nearest_neighbour(10, max_size)
        if plt:
            show_log(log, f"Random RTree nearest neighbour, max node size={max_size}")
    if PROFILE_BRUTE_FORCE_NEIGHBOUR:
        log = profile_brute_force_nearest_neighbour(10)
        if plt:
            show_log(log, f"Brute force nearest neighbour")
