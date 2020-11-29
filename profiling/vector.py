# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import sys
import time
from datetime import datetime
from pathlib import Path
from ezdxf.acc import USE_C_EXT

if USE_C_EXT is False:
    print('C-extension disabled or not available.')
    sys.exit(1)

from ezdxf.math.vector import Vec3, Vec2
from ezdxf.acc.vector import Vec3 as CVec3, Vec2 as CVec2
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


def vec2_add(VType, count):
    v = VType(0, 0)
    inc = VType(1, 2)
    for _ in range(count):
        v = v + inc


def vec2_subtract(VType, count):
    v = VType(0, 0)
    dec = VType(1, 2)
    for _ in range(count):
        v = v - dec


def vec2_multiply(VType, count):
    v = VType(1, 2)
    for _ in range(count):
        v = v * 123.0


def vec2_normalize(VType, count):
    v = VType(10, 20)
    for _ in range(count):
        v.normalize(3.0)


def vec3_add(VType, count):
    v = VType()
    inc = VType(1, 2, 3)
    for _ in range(count):
        v = v + inc


def vec3_subtract(VType, count):
    v = VType()
    dec = VType(1, 2, 3)
    for _ in range(count):
        v = v - dec


def vec3_multiply(VType, count):
    v = VType(1, 2, 3)
    for _ in range(count):
        v = v * 123.0


def vec3_normalize(VType, count):
    v = VType(10, 20, 30)
    for _ in range(count):
        v.normalize(3.0)


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

print(f'Profiling Vec2/Vec3 Python and Cython implementation:')
profile(f'add {RUNS} Vec2: ', vec2_add, Vec2, CVec2, RUNS)
profile(f'subtract {RUNS} Vec2: ', vec2_subtract, Vec2, CVec2, RUNS)
profile(f'multiply {RUNS} Vec2: ', vec2_multiply, Vec2, CVec2, RUNS)
profile(f'normalize {RUNS} Vec2: ', vec2_normalize, Vec2, CVec2, RUNS)
profile(f'add {RUNS} Vec3: ', vec3_add, Vec3, CVec3, RUNS)
profile(f'subtract {RUNS} Vec3: ', vec3_subtract, Vec3, CVec3, RUNS)
profile(f'multiply {RUNS} Vec3: ', vec3_multiply, Vec3, CVec3, RUNS)
profile(f'normalize {RUNS} Vec3: ', vec3_normalize, Vec3, CVec3, RUNS)
