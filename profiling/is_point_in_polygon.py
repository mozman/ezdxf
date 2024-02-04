#  Copyright (c) 2024, Manfred Moitzi
#  License: MIT License
import time

from ezdxf.math import Vec2
from ezdxf.math._construct import is_point_in_polygon_2d
from ezdxf.acc.construct import is_point_in_polygon_2d as is_point_in_polygon_cy

VERTICES = [(1, 1), (5, 1), (5, 3), (3, 3), (3, 5), (5, 5), (5, 7), (1, 7)]
SHAPE_PY = Vec2.list(VERTICES)

POINTS_INSIDE = Vec2.list(
    [(2, 2), (3, 2), (4, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 6), (4, 6)]
)

POINTS_OUTSIDE = Vec2.list(
    [
        (0, 0),  # 0
        (2, 0),  # 1
        (4, 0),  # 2
        (6, 0),  # 3
        (0, 2),  # 4
        (6, 2),  # 5
        (0, 4),  # 6
        (4, 4),  # 7
        (6, 2),  # 8
        (0, 6),  # 9
        (6, 6),  # a
        (0, 8),  # b
        (2, 8),  # c
        (4, 8),  # d
        (6, 8),  # e
    ]
)


ROUNDS = 2000


def python_version():
    for point in POINTS_INSIDE + POINTS_OUTSIDE:
        is_point_in_polygon_2d(point, SHAPE_PY)


def cython_version():
    for point in POINTS_INSIDE + POINTS_OUTSIDE:
        is_point_in_polygon_cy(point, SHAPE_PY)


def profile(func) -> float:
    t0 = time.perf_counter()
    for _ in range(ROUNDS):
        func()
    t1 = time.perf_counter()
    return t1 - t0


def main():
    py_t = profile(python_version)
    print(f"python version: {py_t:.3f}s")

    # Numpy/Cython version was just 10x faster, this Cython version is 23x faster!
    cy_t = profile(cython_version)
    print(f"cython version: {cy_t:.3f}s")
    print(f"ratio python/cython: {py_t/cy_t:.3f}")


if __name__ == "__main__":
    main()
