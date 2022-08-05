# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
import time
from ezdxf.render.linetypes import LineTypeRenderer


def dashed_lines(func, count):
    for _ in range(count):
        func()


def profile1(func, *args) -> float:
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    return t1 - t0


def py_rendering():
    r = LineTypeRenderer((1., 1., 2., 1.))  # line-gap-line-gap
    list(r.line_segment((0, 0), (100, 0)))


def profile(text, func, *args):
    py_time = profile1(func, py_rendering, *args)
    print(f"CPython: {text} {py_time:.3f}s")
    cy_time = profile1(func, py_rendering, *args)
    print(f"Cython: {text} {cy_time:.3f}s")
    print(f"Ratio CPython/Cython {py_time/cy_time:.1f}x\n")


RUNS = 40_000

print(f"Profiling linetype rendering implementations:")
profile(f"{RUNS} dashed lines: ", dashed_lines, RUNS)

