# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import time
import random
import csv
from pathlib import Path
from ezdxf.math.linalg import Matrix, BandedMatrixLU, banded_matrix, LUDecomposition

DIR = Path('~/Desktop/Outbox').expanduser()

def random_values(n, spread=1.0):
    s = spread / 2.0
    return [s - random.random() * s for _ in range(n)]


def random_matrix(shape, m1: int, m2: int):
    m = Matrix(shape=shape)
    for i in range(-m1, m2):
        m.set_diag(-i, random_values(m.nrows))
    return m


def profile_LU_matrix_solver(count: int, A: Matrix, B: Matrix):
    for _ in range(count):
        lu = LUDecomposition(A)
        lu.solve_matrix(B)


def profile_banded_matrix_solver(count, A: Matrix, B: Matrix):
    for _ in range(count):
        lu = BandedMatrixLU(*banded_matrix(A))
        lu.solve_matrix(B)


def profile(func, *args):
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    delta = t1 - t0
    return delta

REPEAT = 5

with open(DIR/'profiling_banded_matrix.csv', mode='wt', newline='') as f:
    writer = csv.writer(f, dialect='excel')
    writer.writerow(['Parameters', 'Standard LU', 'Banded LU', 'Factor'])
    for size in range(90, 101, 5):
        for m1, m2 in [(1, 1), (2, 1), (1, 2), (2, 2), (2, 3), (3, 2), (3, 3), (3, 4), (4, 3), (4, 4)]:
            A = random_matrix((size, size), m1, m1)
            B = Matrix(list(zip(random_values(size), random_values(size), random_values(size))))
            t0 = profile(profile_LU_matrix_solver, REPEAT, A, B)
            t1 = profile(profile_banded_matrix_solver, REPEAT, A, B)
            factor = t0 / t1
            print(f'Matrix {size}x{size}, m1={m1}, m2={m2}, {REPEAT}x: Standard LU {t0:0.3f}s Banded LU {t1:0.3}s factor: x{factor:.1f}')
            writer.writerow([f"N={size}, m1+m2+1={m1+m2+1}", round(t0, 3), round(t1, 3), round(factor, 1)])

# Advantage Banded Matrix starts at ~ N=15
# Matrix 10x10, m1=1, m2=1, 5x: Standard LU 0.001s Banded LU 0.000877s factor: x1.4
# Matrix 10x10, m1=2, m2=1, 5x: Standard LU 0.001s Banded LU 0.00117s factor: x1.0
# Matrix 10x10, m1=1, m2=2, 5x: Standard LU 0.001s Banded LU 0.000845s factor: x1.4
# Matrix 10x10, m1=2, m2=2, 5x: Standard LU 0.001s Banded LU 0.00114s factor: x1.1
# Matrix 10x10, m1=2, m2=3, 5x: Standard LU 0.001s Banded LU 0.00115s factor: x1.1
# Matrix 10x10, m1=3, m2=2, 5x: Standard LU 0.001s Banded LU 0.00144s factor: x0.9
# Matrix 10x10, m1=3, m2=3, 5x: Standard LU 0.002s Banded LU 0.00152s factor: x1.2
# Matrix 10x10, m1=3, m2=4, 5x: Standard LU 0.001s Banded LU 0.00147s factor: x0.9
# Matrix 10x10, m1=4, m2=3, 5x: Standard LU 0.001s Banded LU 0.00173s factor: x0.7
# Matrix 10x10, m1=4, m2=4, 5x: Standard LU 0.001s Banded LU 0.00328s factor: x0.4
# Matrix 15x15, m1=1, m2=1, 5x: Standard LU 0.007s Banded LU 0.00315s factor: x2.2
# Matrix 15x15, m1=2, m2=1, 5x: Standard LU 0.007s Banded LU 0.00441s factor: x1.6
# Matrix 15x15, m1=1, m2=2, 5x: Standard LU 0.006s Banded LU 0.00307s factor: x2.1
# Matrix 15x15, m1=2, m2=2, 5x: Standard LU 0.007s Banded LU 0.00428s factor: x1.7
# Matrix 15x15, m1=2, m2=3, 5x: Standard LU 0.007s Banded LU 0.00425s factor: x1.6
# Matrix 15x15, m1=3, m2=2, 5x: Standard LU 0.004s Banded LU 0.0022s factor: x1.8
# Matrix 15x15, m1=3, m2=3, 5x: Standard LU 0.003s Banded LU 0.00224s factor: x1.3
# Matrix 15x15, m1=3, m2=4, 5x: Standard LU 0.003s Banded LU 0.00222s factor: x1.5
# Matrix 15x15, m1=4, m2=3, 5x: Standard LU 0.003s Banded LU 0.00266s factor: x1.1
# Matrix 15x15, m1=4, m2=4, 5x: Standard LU 0.003s Banded LU 0.00265s factor: x1.1
# Matrix 20x20, m1=1, m2=1, 5x: Standard LU 0.005s Banded LU 0.00188s factor: x2.8
# Matrix 20x20, m1=2, m2=1, 5x: Standard LU 0.006s Banded LU 0.00251s factor: x2.2
# Matrix 20x20, m1=1, m2=2, 5x: Standard LU 0.007s Banded LU 0.00236s factor: x2.8
# Matrix 20x20, m1=2, m2=2, 5x: Standard LU 0.007s Banded LU 0.00286s factor: x2.4
# Matrix 20x20, m1=2, m2=3, 5x: Standard LU 0.007s Banded LU 0.00306s factor: x2.3
# Matrix 20x20, m1=3, m2=2, 5x: Standard LU 0.007s Banded LU 0.00382s factor: x1.9
# Matrix 20x20, m1=3, m2=3, 5x: Standard LU 0.007s Banded LU 0.00379s factor: x1.8
# Matrix 20x20, m1=3, m2=4, 5x: Standard LU 0.007s Banded LU 0.00383s factor: x1.9
# Matrix 20x20, m1=4, m2=3, 5x: Standard LU 0.007s Banded LU 0.00458s factor: x1.6
# Matrix 20x20, m1=4, m2=4, 5x: Standard LU 0.007s Banded LU 0.00647s factor: x1.0
# ...
# ...
# ...
# Matrix 100x100, m1=1, m2=1, 5x: Standard LU 0.397s Banded LU 0.0237s factor: x16.8
# Matrix 100x100, m1=2, m2=1, 5x: Standard LU 0.407s Banded LU 0.0263s factor: x15.5
# Matrix 100x100, m1=1, m2=2, 5x: Standard LU 0.397s Banded LU 0.023s factor: x17.3
# Matrix 100x100, m1=2, m2=2, 5x: Standard LU 0.424s Banded LU 0.0333s factor: x12.7
# Matrix 100x100, m1=2, m2=3, 5x: Standard LU 0.454s Banded LU 0.0269s factor: x16.9
# Matrix 100x100, m1=3, m2=2, 5x: Standard LU 0.430s Banded LU 0.029s factor: x14.8
# Matrix 100x100, m1=3, m2=3, 5x: Standard LU 0.411s Banded LU 0.0303s factor: x13.6
# Matrix 100x100, m1=3, m2=4, 5x: Standard LU 0.415s Banded LU 0.0294s factor: x14.1
# Matrix 100x100, m1=4, m2=3, 5x: Standard LU 0.412s Banded LU 0.038s factor: x10.8
# Matrix 100x100, m1=4, m2=4, 5x: Standard LU 0.409s Banded LU 0.0325s factor: x12.6
