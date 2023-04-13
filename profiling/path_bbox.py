# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import time
import math
from ezdxf.math import BoundingBox, Vec3
from ezdxf.render.forms import circle
import ezdxf.path

LARGE_PATH = ezdxf.path.from_vertices(circle(100, radius=10))

def current_fast_bbox():
    ezdxf.path.bbox((LARGE_PATH, ), fast=True)

def current_precise_bbox():
    ezdxf.path.bbox((LARGE_PATH, ), fast=False)

def new_fast_bbox():
    fast_bbox(LARGE_PATH)


def fast_bbox(path) -> BoundingBox:
    # it's much slower!
    bbox = BoundingBox()
    if len(path) == 0:
        return bbox
    min_x = math.inf
    min_y = math.inf
    min_z = math.inf
    max_x = -math.inf
    max_y = -math.inf
    max_z = -math.inf
    for x, y, z in path.control_vertices():
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        min_z = min(min_z, z)
        max_x = max(max_x, x)
        max_y = max(max_y, y)
        max_z = max(max_z, z)
    bbox.extend([Vec3(min_x, min_y, min_z), Vec3(max_x, max_y, max_z)])
    return bbox


def profile(text, func, runs):
    t0 = time.perf_counter()
    for _ in range(runs):
        func()
    t1 = time.perf_counter()
    t = t1 - t0
    print(f"{text} {t:.3f}s")


RUNS = 10_000

print(f"Profiling bounding box calculation:")
profile(f"current_precise_bbox() {RUNS}:", current_precise_bbox, RUNS)
profile(f"current_fast_bbox() {RUNS}:", current_fast_bbox, RUNS)
profile(f"new_fast_bbox() {RUNS}:", new_fast_bbox, RUNS)
