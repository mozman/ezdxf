# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import sys
import time

from datetime import datetime
from pathlib import Path
from ezdxf.acc import USE_C_EXT
from ezdxf.render.forms import ellipse

if USE_C_EXT is False:
    print("C-extension disabled or not available.")
    sys.exit(1)

from ezdxf.math._construct import (
    has_clockwise_orientation as py_has_clockwise_orientation,
)
from ezdxf.acc.construct2d import (
    has_clockwise_orientation as cy_has_clockwise_orientation,
)
from ezdxf.math._construct import (
    intersection_line_line_2d as py_intersection_line_line_2d,
)
from ezdxf.acc.construct import (
    intersection_line_line_2d as cy_intersection_line_line_2d,
)
from ezdxf.version import __version__
from ezdxf.acc.vector import Vec2


def open_log(name: str):
    parent = Path(__file__).parent
    p = parent / "logs" / Path(name + ".csv")
    if not p.exists():
        with open(p, mode="wt") as fp:
            fp.write(
                '"timestamp"; "pytime"; "cytime"; '
                '"python_version"; "ezdxf_version"\n'
            )
    log_file = open(p, mode="at")
    return log_file


def log(name: str, pytime: float, cytime: float):
    log_file = open_log(name)
    timestamp = datetime.now().isoformat()
    log_file.write(
        f'{timestamp}; {pytime}; {cytime}; "{sys.version}"; "{__version__}"\n'
    )
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
    print(f"Python - {text} {pytime:.3f}s")
    print(f"Cython - {text} {cytime:.3f}s")
    print(f"Ratio {ratio:.1f}x")
    log(log_name, pytime, cytime)


def profile_py_has_clockwise_orientation(vertices, count):
    for _ in range(count):
        py_has_clockwise_orientation(vertices)


def profile_cy_has_clockwise_orientation(vertices, count):
    for _ in range(count):
        cy_has_clockwise_orientation(vertices)


def profile_py_intersection_line_line_2d(count):
    line1 = [Vec2(0, 0), Vec2(2, 0)]
    line2 = [Vec2(1, -1), Vec2(1, 1)]

    for _ in range(count):
        py_intersection_line_line_2d(line1, line2)


def profile_cy_intersection_line_line_2d(count):
    line1 = [Vec2(0, 0), Vec2(2, 0)]
    line2 = [Vec2(1, -1), Vec2(1, 1)]
    for _ in range(count):
        cy_intersection_line_line_2d(line1, line2)


def profile_py_no_intersection_line_line_2d(count):
    line1 = [Vec2(0, 0), Vec2(2, 0)]
    line2 = [Vec2(0, 1), Vec2(2, 1)]
    for _ in range(count):
        py_intersection_line_line_2d(line1, line2)


def profile_cy_no_intersection_line_line_2d(count):
    line1 = [Vec2(0, 0), Vec2(2, 0)]
    line2 = [Vec2(0, 1), Vec2(2, 1)]
    for _ in range(count):
        cy_intersection_line_line_2d(line1, line2)


RUNS = 100_000
ellipse_vertices = list(ellipse(count=100, rx=10, ry=5))

print(f"Profiling 2D construction tools as Python and Cython implementations:")
profile(
    f"detect {RUNS}x clockwise orientation of {len(ellipse_vertices)} vertices:",
    "c2d_has_clockwise_orientation",
    profile_py_has_clockwise_orientation,
    profile_cy_has_clockwise_orientation,
    ellipse_vertices,
    RUNS,
)
profile(
    f"detect {RUNS}x real 2D line intersections:",
    "c2d_intersection_line_line_2d",
    profile_py_intersection_line_line_2d,
    profile_cy_intersection_line_line_2d,
    RUNS,
)
profile(
    f"detect {RUNS}x no 2D line intersections:",
    "c2d_no_intersection_line_line_2d",
    profile_py_no_intersection_line_line_2d,
    profile_cy_no_intersection_line_line_2d,
    RUNS,
)
