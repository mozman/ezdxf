#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import time
import random
import math
import numpy as np
from ezdxf.acc import USE_C_EXT
from ezdxf.math import Matrix44, Vec2


RUNS = 10_000
POINT_COUNT = 1000


def points(count):
    return [
        Vec2(random.randint(-1000, 1000), random.randint(-1000, 1000))
        for _ in range(count)
    ]


def make_m44(sx, sy, angle, tx, ty):
    return (
        Matrix44.scale(sx, sy, 1)
        @ Matrix44.z_rotate(angle)
        @ Matrix44.translate(tx, ty, 0)
    )


def python_manual_transform(a, b, c, d, e, f, points: list[Vec2]):
    # runs faster in pure Python mode and PyPy
    return (Vec2(x * a + y * c + e, x * b + y * d + f) for x, y in points)


def transform_vertices(points, count):
    m44 = make_m44(2, 2, math.pi / 2, 100, 200)
    for _ in range(count):
        result = list(m44.transform_vertices(points))


def fast_2d_transform(points, count):
    # CPython (c-extension): ~1.1x faster than a transform_vertices()
    # PyPy: ~4x faster than a transform_vertices()
    m44 = make_m44(2, 2, math.pi / 2, 100, 200)
    for _ in range(count):
        result = list(m44.fast_2d_transform(points))


def array_2d_inplace_transform(points, count):
    # CPython (cython): 34.9x faster than fast_2d_transform()
    array = np.array(points, dtype=np.float64)
    m44 = make_m44(2, 2, math.pi / 2, 100, 200)
    for _ in range(count):
        copy = array.copy()
        m44.transform_array_inplace(copy, 2)


def translate_points_by_transform_vertices(points, count):
    m44 = Matrix44.translate(10, 20, 0)
    for _ in range(count):
        result = list(m44.transform_vertices(points))


def translate_points_by_fast_2d_transform(points, count):
    m44 = Matrix44.translate(10, 20, 0)
    for _ in range(count):
        result = list(m44.fast_2d_transform(points))


def translate_points_by_vec2_addition(points, count):
    # CPython (c-extension):
    # ~1.3x faster than transform_vertices()
    # ~1.2x faster than fast_2d_transformation()
    # PyPy:
    # ~12-14x faster than transform_vertices()
    # ~3-4x faster than fast_2d_transformation()
    offset = Vec2(10, 20)
    for _ in range(count):
        result = [offset + p for p in points]


def translate_and_scale_points_by_vec2_add_mul(points, count):
    # CPython (c-extension): 0.7x (slower) than fast_2d_transform()
    # PyPy: ~3x faster than fast_2d_transform()
    offset = Vec2(10, 20)
    for _ in range(count):
        result = [offset + (p * 2.0) for p in points]


def profile1(func, *args) -> float:
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    return t1 - t0


def profile(text, func0, func1, points):
    run0 = profile1(func0, points, RUNS)
    run1 = profile1(func1, points, RUNS)
    ratio = run0 / run1
    print(f"{func0.__name__} - {text} {run0:.3f}s")
    print(f"{func1.__name__} - {text} {run1:.3f}s")
    print(f"Ratio {ratio:.1f}x")


print(f"C-extension is {USE_C_EXT}")
print(f"Profiling 2d transformation:")
profile(
    f"inplace transformation of {POINT_COUNT} random points, {RUNS} times: ",
    translate_points_by_fast_2d_transform,
    array_2d_inplace_transform,
    points(POINT_COUNT),
)

profile(
    f"fast transform {POINT_COUNT} random points, {RUNS} times: ",
    transform_vertices,
    fast_2d_transform,
    points(POINT_COUNT),
)

profile(
    f"translate {POINT_COUNT} random points, {RUNS} times: ",
    translate_points_by_fast_2d_transform,
    translate_points_by_vec2_addition,
    points(POINT_COUNT),
)

profile(
    f"translate {POINT_COUNT} random points, {RUNS} times: ",
    translate_points_by_transform_vertices,
    translate_points_by_vec2_addition,
    points(POINT_COUNT),
)

profile(
    f"translate and scale {POINT_COUNT} random points, {RUNS} times: ",
    translate_points_by_fast_2d_transform,
    translate_and_scale_points_by_vec2_add_mul,
    points(POINT_COUNT),
)
