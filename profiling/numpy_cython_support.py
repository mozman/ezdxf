# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import time
import numpy as np
from ezdxf.math import Vec2, has_clockwise_orientation
from ezdxf.acc import np_support
from ezdxf.render.forms import circle


VEC2_LIST = Vec2.list(circle(512, 10, close=True))
NP_ARRAY = np.array(VEC2_LIST, dtype=np.float64)


def has_cw_vec2():
    has_clockwise_orientation(VEC2_LIST)


def has_cw_numpy():
    np_support.has_clockwise_orientation(NP_ARRAY)


def profile(text, func, runs):
    t0 = time.perf_counter()
    for _ in range(runs):
        func()
    t1 = time.perf_counter()
    t = t1 - t0
    print(f"{text} {t:.3f}s")


RUNS = 100_000

print(f"Profiling Cython support module for numpy arrays:")
print(
    f"Test array has {len(VEC2_LIST)} vertices."
)
profile(f"has_clockwise_orientation() Vec2 {RUNS}:", has_cw_vec2, RUNS)
profile(f"np_support.has_clockwise_orientation() {RUNS}:", has_cw_numpy, RUNS)
