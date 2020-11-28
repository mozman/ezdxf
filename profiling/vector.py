# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import sys
import time
from ezdxf.acc import USE_C_EXT

if USE_C_EXT is False:
    print('C-extensions disabled or not available.')
    sys.exit(1)

from ezdxf.math.vector import Vec3
from ezdxf.acc.vector import Vec3 as CVec3


def profile_adding_vectors(VType, count):
    v = VType()
    inc = VType(1, 2, 3)
    for _ in range(count):
        v = v + inc


def profile_multiply_vectors(VType, count):
    v = VType(1, 2, 3)
    for _ in range(count):
        v = v * 123.0


def profile_normalize_vectors(VType, count):
    v = VType(10, 20, 30)
    for _ in range(count):
        v.normalize(3.0)


def profile1(func, *args):
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    return t1 - t0


def profile(text, func, pytype, cytype, *args):
    t_python = profile1(func, pytype, *args)
    t_cython = profile1(func, cytype, *args)
    ratio = t_python / t_cython
    print(f'Python - {text} {t_python:.3f}s')
    print(f'Cython - {text} {t_cython:.3f}s')
    print(f'Ratio {ratio:.3f}x')


RUNS = 1_000_000

print(f'Profiling Vec3 Python and Cython implementation:')
profile(f'adding {RUNS} vectors: ', profile_adding_vectors, Vec3, CVec3, RUNS)
profile(f'multiply {RUNS} vectors: ', profile_multiply_vectors, Vec3, CVec3, RUNS)
profile(f'normalize {RUNS} vectors: ', profile_normalize_vectors, Vec3, CVec3, RUNS)
