# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import sys
import time

from datetime import datetime
from pathlib import Path
from ezdxf.acc import USE_C_EXT
from ezdxf.render.forms import ellipse

if USE_C_EXT is False:
    print('C-extension disabled or not available.')
    sys.exit(1)

# The Python implementation of has_clockwise_orientation() uses the
# Vec2() Cython implementation if possible, therefore not 100% pure Python:
from ezdxf.math._construct2d import has_clockwise_orientation as py_has_clockwise_orientation
from ezdxf.acc.construct2d import has_clockwise_orientation as cy_has_clockwise_orientation
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


def profile1(func, *args) -> float:
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    return t1 - t0


def profile(text, log_name, pyfunc, cyfunc, *args):
    pytime = profile1(pyfunc, *args)
    cytime = profile1(cyfunc, *args)
    ratio = pytime / cytime
    print(f'Python - {text} {pytime:.3f}s')
    print(f'Cython - {text} {cytime:.3f}s')
    print(f'Ratio {ratio:.1f}x')
    log(log_name, pytime, cytime)


def profile_py_has_clockwise_orientation(vertices, count):
    for _ in range(count):
        py_has_clockwise_orientation(vertices)


def profile_cy_has_clockwise_orientation(vertices, count):
    for _ in range(count):
        cy_has_clockwise_orientation(vertices)


RUNS = 100_000
ellipse_vertices = list(ellipse(count=100, rx=10, ry=5))

print(f'Profiling 2D construction tools as Python and Cython implementations:')
profile(f'detect {RUNS}x clockwise orientation of {len(ellipse_vertices)} vertices:',
        'c2d_has_clockwise_orientation',
        profile_py_has_clockwise_orientation,
        profile_cy_has_clockwise_orientation,
        ellipse_vertices,
        RUNS)
