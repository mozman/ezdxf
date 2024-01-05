# Copyright (c) 2020-2024, Manfred Moitzi
# License: MIT License
import time
import random
import csv
import pathlib
from ezdxf.math.linalg import (
    Matrix,
    BandedMatrixLU,
    banded_matrix,
    NumpySolver,
)


CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def random_values(n, spread=1.0):
    s = spread / 2.0
    return [s - random.random() * s for _ in range(n)]


def random_matrix(shape, m1: int, m2: int):
    m = Matrix(shape=shape)
    for i in range(-m1, m2):
        m.set_diag(-i, random_values(m.nrows))
    return m


def profile_numpy_matrix_solver(count: int, A: Matrix, B: Matrix):
    for _ in range(count):
        lu = NumpySolver(A.matrix)
        lu.solve_matrix(B.matrix)


def profile_banded_matrix_solver(count, A: Matrix, B: Matrix):
    for _ in range(count):
        lu = BandedMatrixLU(*banded_matrix(A, check_all=False))
        lu.solve_matrix(B.matrix)


def profile(func, *args):
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    delta = t1 - t0
    return delta


REPEAT = 5

with open(CWD / "profiling_banded_matrix.csv", mode="wt", newline="") as f:
    writer = csv.writer(f, dialect="excel")
    writer.writerow(["Parameters", "Standard LU", "Banded LU", "Factor"])
    for size in range(10, 101, 5):
        for m1, m2 in [
            (1, 1),
            (2, 1),
            (1, 2),
            (2, 2),
            (2, 3),
            (3, 2),
            (3, 3),
            (3, 4),
            (4, 3),
            (4, 4),
        ]:
            A = random_matrix((size, size), m1, m2)
            B = Matrix(
                list(
                    zip(
                        random_values(size),
                        random_values(size),
                        random_values(size),
                    )
                )
            )
            t0 = profile(profile_numpy_matrix_solver, REPEAT, A, B)
            t1 = profile(profile_banded_matrix_solver, REPEAT, A, B)
            factor = t0 / t1
            print(
                f"Matrix {size}x{size}, m1={m1}, m2={m2}, {REPEAT}x: Numpy {t0:0.3f}s Banded LU {t1:0.3}s factor: x{factor:.1f}"
            )
            writer.writerow(
                [
                    f"N={size}, m1+m2+1={m1 + m2 + 1}",
                    round(t0, 3),
                    round(t1, 3),
                    round(factor, 1),
                ]
            )
