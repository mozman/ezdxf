# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import time
import numpy as np
from ezdxf.math import Vec2
from ezdxf.render.forms import circle
from ezdxf import path
from ezdxf.npshapes import NumpyPath2d
VEC2_LIST = Vec2.list(circle(512, 10, close=True))
TUPLE_LIST = list(tuple(v) for v in VEC2_LIST)
PATH = path.from_vertices(VEC2_LIST)


def setup_numpy_from_vec2():
    _ = np.array(VEC2_LIST, dtype=np.float64)


def setup_numpy_from_xy_tuple():
    _ = np.array(TUPLE_LIST, dtype=np.float64)


def setup_numpy_path2d():
    _ = NumpyPath2d(PATH)


def setup_from_vertices():
    _ = NumpyPath2d.from_vertices(VEC2_LIST)


def profile(text, func, runs):
    t0 = time.perf_counter()
    for _ in range(runs):
        func()
    t1 = time.perf_counter()
    t = t1 - t0
    print(f"{text} {t:.3f}s")


RUNS = 10_000

print(f"Profiling setup NumpyPath2d:")
print(
    f"Test array has {len(VEC2_LIST)} vertices."
)
profile(f"numpy_from_vec2() {RUNS}:", setup_numpy_from_vec2, RUNS)
profile(f"numpy_from_xy_tuple() {RUNS}:", setup_numpy_from_xy_tuple, RUNS)
profile(f"setup_numpy_path2d() {RUNS}:", setup_numpy_path2d, RUNS)
profile(f"setup_from_vertices() {RUNS}:", setup_from_vertices, RUNS)


