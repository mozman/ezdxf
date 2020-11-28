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


def profile_adding_vectors(count, VType):
    v = VType()
    inc = VType(1, 2, 3)
    for _ in range(count):
        v = v + inc


def profile_multiply_vectors(count, VType):
    v = VType(1, 2, 3)
    for _ in range(count):
        v = v * 123.0


def profile_normalize_vectors(count, VType):
    v = VType(10, 20, 30)
    for _ in range(count):
        v.normalize(3.0)


def profile(text, func, *args):
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    print(f'{text} {t1 - t0:.3f}s')


print(f'Profiling Vec3 Python and Cython implementation:')
profile('Adding Python vectors: ', profile_adding_vectors, 1000000, Vec3)
profile('Adding Cython vectors: ', profile_adding_vectors, 1000000, CVec3)
profile('Multiply Python vectors: ', profile_multiply_vectors, 1000000, Vec3)
profile('Multiply Cython vectors: ', profile_multiply_vectors, 1000000, CVec3)
profile('Normalize Python vectors: ', profile_normalize_vectors, 1000000, Vec3)
profile('Normalize Cython vectors: ', profile_normalize_vectors, 1000000, CVec3)
