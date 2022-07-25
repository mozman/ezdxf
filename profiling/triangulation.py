# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
import time

from archive import tripy
from ezdxf.render import forms
from ezdxf.math.triangulation import mapbox_earcut_2d

SMALL_GEAR = list(
    forms.gear(8, top_width=1, bottom_width=3, height=2, outside_radius=10)
)
BIG_GEAR = list(
    forms.gear(64, top_width=1, bottom_width=3, height=2, outside_radius=20)
)


def small_gear(func, count):
    for _ in range(count):
        list(func(SMALL_GEAR))


def big_gear(func, count):
    for _ in range(count):
        list(func(BIG_GEAR))


def profile1(func, *args) -> float:
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    return t1 - t0


def profile(text, func, *args):
    ear_clipping_2d_time = profile1(func, tripy.earclip, *args)
    mapbox_earcut_2d_time = profile1(func, mapbox_earcut_2d, *args)
    ratio = ear_clipping_2d_time / mapbox_earcut_2d_time
    print(f"tripy.earclip (CPython) - {text} {ear_clipping_2d_time:.3f}s")
    print(f"mapbox_earcut_2d (Cython) - {text} {mapbox_earcut_2d_time:.3f}s")
    print(f"Ratio {ratio:.1f}x")


RUNS = 100

print(f"Profiling triangulation implementations:")
profile(f"small gear {RUNS}: ", small_gear, RUNS)
profile(f"big gear {RUNS}: ", big_gear, RUNS)
