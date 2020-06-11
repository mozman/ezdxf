# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import time
import random

from ezdxf.math.linalg import Matrix, gauss_vector_solver


def random_matrix(rows, cols):
    return Matrix.reshape(items=(random.random() for _ in range(rows * cols)), shape=(rows, cols))


SIZE = 200
random.seed = 0
RANDOM_GAUSS_MATRIX_1 = random_matrix(rows=SIZE, cols=SIZE)
B_VECTOR = [random.random() for _ in range(SIZE)]


def profile_gauss_vector_solver(count):
    for _ in range(count):
        gauss_vector_solver(RANDOM_GAUSS_MATRIX_1.matrix, B_VECTOR)


def profile(text, func, *args):
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    print(f'{text} {t1 - t0:.3f}s')


profile('Reference Gauss vector solver(): ', profile_gauss_vector_solver, 5)

