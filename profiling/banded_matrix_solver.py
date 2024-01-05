# Copyright (c) 2020-2022, Manfred Moitzi
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
        lu.solve_matrix(B)


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

# Advantage Banded Matrix starts at ~ N=15
# Matrix 10x10, m1=1, m2=1, 5x: Standard LU 0.001s Banded LU 0.00057s factor: x2.1
# Matrix 10x10, m1=2, m2=1, 5x: Standard LU 0.001s Banded LU 0.000922s factor: x1.4
# Matrix 10x10, m1=1, m2=2, 5x: Standard LU 0.001s Banded LU 0.00055s factor: x2.1
# Matrix 10x10, m1=2, m2=2, 5x: Standard LU 0.001s Banded LU 0.000908s factor: x1.3
# Matrix 10x10, m1=2, m2=3, 5x: Standard LU 0.001s Banded LU 0.000901s factor: x1.4
# Matrix 10x10, m1=3, m2=2, 5x: Standard LU 0.001s Banded LU 0.00122s factor: x1.0
# Matrix 10x10, m1=3, m2=3, 5x: Standard LU 0.001s Banded LU 0.00128s factor: x1.0
# Matrix 10x10, m1=3, m2=4, 5x: Standard LU 0.001s Banded LU 0.00126s factor: x1.0
# Matrix 10x10, m1=4, m2=3, 5x: Standard LU 0.001s Banded LU 0.00158s factor: x0.8
# Matrix 10x10, m1=4, m2=4, 5x: Standard LU 0.001s Banded LU 0.0016s factor: x0.8
# Matrix 15x15, m1=1, m2=1, 5x: Standard LU 0.003s Banded LU 0.000709s factor: x3.9
# Matrix 15x15, m1=2, m2=1, 5x: Standard LU 0.003s Banded LU 0.00126s factor: x2.4
# Matrix 15x15, m1=1, m2=2, 5x: Standard LU 0.003s Banded LU 0.000705s factor: x3.9
# Matrix 15x15, m1=2, m2=2, 5x: Standard LU 0.003s Banded LU 0.00122s factor: x2.4
# Matrix 15x15, m1=2, m2=3, 5x: Standard LU 0.003s Banded LU 0.00123s factor: x2.4
# Matrix 15x15, m1=3, m2=2, 5x: Standard LU 0.003s Banded LU 0.00179s factor: x1.7
# Matrix 15x15, m1=3, m2=3, 5x: Standard LU 0.003s Banded LU 0.00176s factor: x1.7
# Matrix 15x15, m1=3, m2=4, 5x: Standard LU 0.003s Banded LU 0.00176s factor: x1.7
# Matrix 15x15, m1=4, m2=3, 5x: Standard LU 0.003s Banded LU 0.00228s factor: x1.3
# Matrix 15x15, m1=4, m2=4, 5x: Standard LU 0.003s Banded LU 0.00227s factor: x1.3
# Matrix 20x20, m1=1, m2=1, 5x: Standard LU 0.005s Banded LU 0.000869s factor: x6.2
# Matrix 20x20, m1=2, m2=1, 5x: Standard LU 0.006s Banded LU 0.00161s factor: x3.6
# Matrix 20x20, m1=1, m2=2, 5x: Standard LU 0.005s Banded LU 0.000868s factor: x6.2
# Matrix 20x20, m1=2, m2=2, 5x: Standard LU 0.006s Banded LU 0.00157s factor: x3.6
# Matrix 20x20, m1=2, m2=3, 5x: Standard LU 0.006s Banded LU 0.00158s factor: x3.6
# Matrix 20x20, m1=3, m2=2, 5x: Standard LU 0.006s Banded LU 0.00223s factor: x2.6
# Matrix 20x20, m1=3, m2=3, 5x: Standard LU 0.006s Banded LU 0.00225s factor: x2.6
# Matrix 20x20, m1=3, m2=4, 5x: Standard LU 0.006s Banded LU 0.0023s factor: x2.5
# Matrix 20x20, m1=4, m2=3, 5x: Standard LU 0.006s Banded LU 0.00293s factor: x2.0
# Matrix 20x20, m1=4, m2=4, 5x: Standard LU 0.006s Banded LU 0.00297s factor: x1.9
# ...
# ...
# ...
# Matrix 100x100, m1=1, m2=1, 5x: Standard LU 0.398s Banded LU 0.00359s factor: x111.1
# Matrix 100x100, m1=2, m2=1, 5x: Standard LU 0.402s Banded LU 0.00701s factor: x57.4
# Matrix 100x100, m1=1, m2=2, 5x: Standard LU 0.396s Banded LU 0.00364s factor: x108.7
# Matrix 100x100, m1=2, m2=2, 5x: Standard LU 0.405s Banded LU 0.00692s factor: x58.5
# Matrix 100x100, m1=2, m2=3, 5x: Standard LU 0.405s Banded LU 0.00698s factor: x58.0
# Matrix 100x100, m1=3, m2=2, 5x: Standard LU 0.406s Banded LU 0.0103s factor: x39.5
# Matrix 100x100, m1=3, m2=3, 5x: Standard LU 0.406s Banded LU 0.0104s factor: x39.0
# Matrix 100x100, m1=3, m2=4, 5x: Standard LU 0.405s Banded LU 0.0104s factor: x38.8
# Matrix 100x100, m1=4, m2=3, 5x: Standard LU 0.408s Banded LU 0.0141s factor: x28.9
# Matrix 100x100, m1=4, m2=4, 5x: Standard LU 0.407s Banded LU 0.014s factor: x29.0
