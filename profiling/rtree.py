# Copyright (c) 2020-2024, Manfred Moitzi
# License: MIT License
import time
from ezdxf.math import Vec3, closest_point
from ezdxf.math.rtree import RTree

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def random_points(n, size=1.0):
    return [Vec3.random() * size for _ in range(n)]


def profile_build_time_random_rtree(count: int, points, max_node_size: int):
    for _ in range(count):
        RTree(points, max_node_size)


def profile_tree_contains_points(count, tree, points):
    for _ in range(count):
        for point in points:
            assert tree.contains(point) is True


def profile_tree_nearest_neighbor(count, tree, points):
    for _ in range(count):
        for point in points:
            assert isinstance(tree.nearest_neighbor(point)[0], Vec3)


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


def profile_rtree_building(repeat: int, max_size: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        name = f"RTree({size}, {max_size})"
        t0 = profile(profile_build_time_random_rtree, repeat, points, max_size)
        time_str = f"{t0:6.2f}s"
        print(f"Build random {name}, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_rtree_contains_all_points(repeat: int, max_size: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        tree = RTree(points, max_size)
        name = f"RTree({size}, {max_size})"
        t0 = profile(profile_tree_contains_points, repeat, tree, points)
        time_str = f"{t0:6.2f}s"
        print(f"{name} contains all points, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_rtree_nearest_neighbor(repeat: int, max_size: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        tree = RTree(points, max_size)
        name = f"RTree({size}, {max_size})"

        search_points = random_points(100, 50.0)
        t0 = profile(profile_tree_nearest_neighbor, repeat, tree, search_points)
        time_str = f"{t0:6.2f}s"
        print(f"{name} nearest neighbor, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_brute_force_contains_all_points(repeat: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)

        name = f"Brute Force({size})"
        t0 = profile(profile_brute_force_contains_points, repeat, points)
        time_str = f"{t0:6.2f}s"
        print(f"{name} contains all points, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def profile_brute_force_nearest_neighbor(repeat: int):
    log = []
    for size in range(100, 2000, 100):
        points = random_points(size, 50.0)
        name = f"Brute Force({size})"

        search_points = random_points(100, 50.0)
        t0 = profile(profile_brute_force_closest_point, repeat, points, search_points)
        time_str = f"{t0:6.2f}s"
        print(f"{name} contains all points, {repeat}x , {time_str}")
        log.append((size, t0))
    return log


def show_log(log, name: str):
    if plt is None:
        return
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


PROFILE_RTREE_BUILD = True
PROFILE_RTREE_CONTAINS = True
PROFILE_RTREE_NEIGHBOR = True

PROFILE_BRUTE_FORCE_CONTAINS = True
PROFILE_BRUTE_FORCE_NEIGHBOR = True

if __name__ == "__main__":
    max_size = 5
    if PROFILE_RTREE_BUILD:
        log = profile_rtree_building(10, max_size)
        if plt:
            show_log(log, f"Build Random RTree, max node size={max_size}")
    if PROFILE_RTREE_CONTAINS:
        log = profile_rtree_contains_all_points(10, max_size)
        if plt:
            show_log(
                log,
                f"Random RTree contains all points, max node size={max_size}",
            )
    if PROFILE_BRUTE_FORCE_CONTAINS:
        log = profile_brute_force_contains_all_points(10)
        if plt:
            show_log(log, f"Brute force contains all points")
    if PROFILE_RTREE_NEIGHBOR:
        log = profile_rtree_nearest_neighbor(10, max_size)
        if plt:
            show_log(log, f"Random RTree nearest neighbor, max node size={max_size}")
    if PROFILE_BRUTE_FORCE_NEIGHBOR:
        log = profile_brute_force_nearest_neighbor(10)
        if plt:
            show_log(log, f"Brute force nearest neighbor")
