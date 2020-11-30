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

from ezdxf.math.bezier4p import Bezier4P
from ezdxf.acc.bezier4p import Bezier4P as CBezier4P
from ezdxf.version import __version__

POINTS = [(0, 0), (1, 0), (1, 1), (0, 1)]


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


def bezier4p_points(Curve, count):
    c = Curve(POINTS)
    for _ in range(count):
        c.point(0.5)


def bezier4p_approximate(Curve, count):
    c = Curve(POINTS)
    for _ in range(count):
        list(c.approximate(32))


def bezier4p_flattening(Curve, count):
    c = Curve(POINTS)
    for _ in range(count):
        list(c.flattening(0.01))


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

print(f'Profiling Bezier4P Python and Cython implementation:')
profile(f'calc {RUNS} points of Bezier4P: ', bezier4p_points, Bezier4P, CBezier4P, RUNS)
profile(f'100.000x approximate 32 points of Bezier4P: ', bezier4p_approximate, Bezier4P, CBezier4P, 100_000)
profile(f'100.000x flattening (0.01) of Bezier4P: ', bezier4p_flattening, Bezier4P, CBezier4P, 100_000)
