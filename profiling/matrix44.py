# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import sys
import time
import random
from datetime import datetime
from pathlib import Path
from ezdxf.acc import USE_C_EXT

if USE_C_EXT is False:
    print('C-extension disabled or not available.')
    sys.exit(1)

from ezdxf.math.matrix44 import Matrix44
from ezdxf.acc.matrix44 import Matrix44 as CMatrix44
from ezdxf.version import __version__


def open_log(name: str):
    parent = Path(__file__).parent
    p = parent / 'logs' / Path(name + '.csv')
    if not p.exists():
        with open(p, mode='wt') as fp:
            fp.write(
                '"timestamp"; "pytime"; "cytime"; '
                '"python_version"; "ezdxf_version"\n')
    log_file = open(p, mode='at')
    return log_file


def log(name: str, pytime: float, cytime: float):
    log_file = open_log(name)
    timestamp = datetime.now().isoformat()
    log_file.write(
        f'{timestamp}; {pytime}; {cytime}; "{sys.version}"; "{__version__}"\n')
    log_file.close()


def m44_default_ctor(m44, count):
    for _ in range(count):
        m44()


def m44_numbers_ctor(m44, count):
    numbers = list(range(16))
    for _ in range(count):
        m44(numbers)


def m44_copy_matrix(m44, count):
    m1 = m44(range(16))
    for _ in range(count):
        m2 = m1.copy()


def m44_multiply_matrix(m44, count):
    m1 = m44(range(16))
    m2 = m44(range(16))
    for _ in range(count):
        res = m1 * m2


def m44_create_scale_matrix(m44, count):
    for _ in range(count):
        m44.scale(1, 2, 3)


def m44_create_translate_matrix(m44, count):
    for _ in range(count):
        m44.translate(1, 2, 3)


def m44_chain_matrix(m44, count):
    m1 = m44.scale(1, 2, 3)
    m2 = m44.translate(1, 2, 3)
    m3 = m44.z_rotate(3.1415 / 2.0)
    for _ in range(count):
        res = m44.chain(m1, m2, m3)


def m44_transform_vector(m44, count):
    t = m44(range(16))
    for _ in range(count):
        res = t.transform((1, 2, 3))


def m44_transform_10_vectors(m44, count):
    vectors = [(1, 2, 3)] * 10
    t = m44(range(16))
    for _ in range(count):
        res = tuple(t.transform_vertices(vectors))


def m44_transform_direction(m44, count):
    t = m44(range(16))
    for _ in range(count):
        res = t.transform_direction((1, 2, 3))


def random16():
    params = list(range(16))
    random.shuffle(params)
    return params


def m44_determinant(m44, count):
    m = m44(random16())
    for _ in range(count):
        m.determinant()


def m44_inverse(m44, count):
    m = m44(random16())
    for _ in range(count):
        m.inverse()


def profile1(func, *args) -> float:
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    return t1 - t0


def profile(text, func, pytype, cytype, *args):
    pytime = profile1(func, pytype, *args)
    cytime = profile1(func, cytype, *args)
    ratio = pytime / cytime
    print(f'Python - {text} {pytime:.3f}s')
    print(f'Cython - {text} {cytime:.3f}s')
    print(f'Ratio {ratio:.1f}x')
    log(func.__name__, pytime, cytime)


RUNS = 1_000_000
RUN2 = 200_000

print(f'Profiling Matrix44 Python and Cython implementation:')
profile(f'create {RUNS} default Matrix44: ',
        m44_default_ctor, Matrix44, CMatrix44, RUNS)
profile(f'create {RUNS} Matrix44 from numbers: ',
        m44_numbers_ctor, Matrix44, CMatrix44, RUNS)
profile(f'copy {RUNS} Matrix44: ',
        m44_copy_matrix, Matrix44, CMatrix44, RUNS)
profile(f'multiply {RUN2} Matrix44: ',
        m44_multiply_matrix, Matrix44, CMatrix44, RUN2)
profile(f'create {RUNS} scale Matrix44: ',
        m44_create_scale_matrix, Matrix44, CMatrix44, RUNS)
profile(f'create {RUNS} translate Matrix44: ',
        m44_create_translate_matrix, Matrix44, CMatrix44, RUNS)
profile(f'{RUN2}x chain 3x Matrix44: ',
        m44_chain_matrix, Matrix44, CMatrix44, RUN2)
profile(f'transform {RUNS} vectors: ',
        m44_transform_vector, Matrix44, CMatrix44, RUNS)
profile(f'transform {RUNS} directions: ',
        m44_transform_direction, Matrix44, CMatrix44, RUNS)
profile(f'transform {RUNS}x 10 vectors: ',
        m44_transform_10_vectors, Matrix44, CMatrix44, RUNS)
profile(f'{RUNS} determinant Matrix44: ',
        m44_determinant, Matrix44, CMatrix44, RUNS)
profile(f'{RUN2} inverse Matrix44: ',
        m44_inverse, Matrix44, CMatrix44, RUN2)
