# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Sequence, Iterable, Iterator
import time

import numpy as np
from ezdxf.math import Bezier3P, Vec3, UVec, Bezier4P


class NumpyQuadraticBezier:
    def __init__(self, control_points: Iterable[UVec]) -> None:
        cpts = np.array(Vec3.list(control_points), dtype=np.double)
        assert cpts.shape[0] == 3
        # first control point is (0, 0, 0)
        offset = cpts[0].copy()
        cpts -= offset
        self._cpts = cpts
        self._offset = offset

    def points(self, params: Sequence[float]) -> Iterator[Vec3]:
        # 1st control point is always (0, 0, 0) => a = 0
        t = np.array(params, dtype=np.double)
        b = t * 2.0 * (1.0 - t)
        c = t * t
        return self._eval(Vec3(self._offset), b, c)

    def tangents(self, params: Sequence[float]) -> Iterator[Vec3]:
        # 1st control point is always (0, 0, 0) => a = 0
        t = np.array(params, dtype=np.double)
        b = t * -4.0 + 2.0
        c = t * 2.0
        return self._eval(Vec3(), b, c)

    def _eval(self, offset: Vec3, b, c) -> Iterator[Vec3]:
        _, cp1, cp2 = self._cpts
        x = b * cp1[0] + c * cp2[0]
        y = b * cp1[1] + c * cp2[1]
        z = b * cp1[2] + c * cp2[2]
        return (offset + xyz for xyz in np.column_stack((x, y, z)))


class NumpyCubicBezier:
    def __init__(self, control_points: Iterable[UVec]) -> None:
        cpts = np.array(Vec3.list(control_points), dtype=np.double)
        assert cpts.shape[0] == 4
        # first control point is (0, 0, 0)
        offset = cpts[0].copy()
        cpts -= offset
        self._cpts = cpts
        self._offset = offset

    def points(self, params: Sequence[float]) -> Iterator[Vec3]:
        # 1st control point is always (0, 0, 0) => a = 0
        t = np.array(params, dtype=np.double)
        t2 = t * t
        _1_minus_t = 1.0 - t
        _1_minus_t_square = _1_minus_t * _1_minus_t
        b = 3.0 * _1_minus_t_square * t
        c = 3.0 * _1_minus_t * t2
        d = t2 * t
        return self._eval(Vec3(self._offset), b, c, d)

    def tangents(self, params: Sequence[float]) -> Iterator[Vec3]:
        # 1st control point is always (0, 0, 0) => a = 0
        t = np.array(params, dtype=np.double)
        _3t = t * 3.0
        d = t * _3t
        b = 3.0 * (1.0 - 4.0 * t + d)
        c = _3t * (2.0 - _3t)
        return self._eval(Vec3(), b, c, d)

    def _eval(self, offset: Vec3, b, c, d) -> Iterator[Vec3]:
        _, cp1, cp2, cp3 = self._cpts
        x = b * cp1[0] + c * cp2[0] + d * cp3[0]
        y = b * cp1[1] + c * cp2[1] + d * cp3[1]
        z = b * cp1[2] + c * cp2[2] + d * cp3[2]
        return (offset + xyz for xyz in np.column_stack((x, y, z)))


def compare_quad_curves():
    print("\nQuadratic Bèzier Curve")
    cpts = [(1, 2, 3), (4, 3, 1), (5, 6, 7)]
    c0 = NumpyQuadraticBezier(cpts)
    c1 = Bezier3P(cpts)
    execute(c0, c1)


def compare_cubic_curves():
    print("\nCubic Bèzier Curve")
    cpts = [(1, 2, 3), (4, 3, 1), (5, 6, 7), (3, 4, 8)]
    c0 = NumpyCubicBezier(cpts)
    c1 = Bezier4P(cpts)
    execute(c0, c1)


def execute(c0, c1):
    params = [0.5, 0.6, 0.7]
    print("Points Calculation")
    print("Numpy:   ", list(c0.points(params)))
    print("Cython:  ", [c1.point(t) for t in params])

    print("\n1st Derivative Calculation")
    print("Numpy:  ", list(c0.tangents(params)))
    print("Cython: ", [c1.tangent(t) for t in params])


def profile():
    print("\nQuadratic Bèzier Curve")
    cpts = [(1, 2, 3), (4, 3, 1), (5, 6, 7)]
    curve = NumpyQuadraticBezier(cpts)
    params = np.linspace(0.1, 0.9, 100)
    count = 10_000

    t0 = time.perf_counter()
    profile_numpy(count, curve, params)
    print(f"Numpy:  {time.perf_counter() - t0}")

    curve = Bezier3P(cpts)
    t0 = time.perf_counter()
    profile_cython(count, curve, params)
    print(f"Cython: {time.perf_counter() - t0}")

    print("\nCubic Bèzier Curve")
    cpts = [(1, 2, 3), (4, 3, 1), (5, 6, 7), (3, 4, 8)]
    curve = NumpyCubicBezier(cpts)

    t0 = time.perf_counter()
    profile_numpy(count, curve, params)
    print(f"Numpy:  {time.perf_counter() - t0}")

    curve = Bezier4P(cpts)
    t0 = time.perf_counter()
    profile_cython(count, curve, params)
    print(f"Cython: {time.perf_counter() - t0}")


def profile_numpy(count, curve, params):
    for _ in range(count):
        list(curve.points(params))
        list(curve.tangents(params))


def profile_cython(count, curve, params):
    for _ in range(count):
        [curve.point(t) for t in params]
        [curve.tangent(t) for t in params]


if __name__ == "__main__":
    compare_quad_curves()
    compare_cubic_curves()
    profile()
