# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
import time

from archive import tripy
try:
    from archive import tricy
except ImportError:
    print("module 'tricy' from archive not importable!")
    print("build module:\n")
    print("    cd archive")
    print("    python setup.py build_ext -i")
    exit(1)

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
    tripy_time = profile1(func, tripy.earclip, *args)
    tricy_time = profile1(func, tricy.earclip, *args)
    print(f"tripy.earclip (CPython) - {text} {tripy_time:.3f}s")
    print(f"tricy.earclip (Cython) - {text} {tricy_time:.3f}s")
    print(f"Ratio tripy/tricy {tripy_time / tricy_time:.1f}x")
    mapbox_earcut_2d_time = profile1(func, mapbox_earcut_2d, *args)
    print(f"mapbox_earcut_2d (Cython) - {text} {mapbox_earcut_2d_time:.3f}s")
    print(f"Ratio tricy/mapbox {tricy_time/mapbox_earcut_2d_time:.1f}x\n")


RUNS = 100

print(f"Profiling triangulation implementations:")
profile(f"small gear {RUNS}: ", small_gear, RUNS)
profile(f"big gear {RUNS}: ", big_gear, RUNS)
