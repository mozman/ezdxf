# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import sys
import time
import math
from datetime import datetime
from pathlib import Path
from ezdxf.acc import USE_C_EXT

if USE_C_EXT is False:
    print("C-extension disabled or not available.")
    sys.exit(1)

# Python implementations:
from ezdxf.math._bezier4p import (
    Bezier4P,
    cubic_bezier_arc_parameters,
    cubic_bezier_from_arc,
    cubic_bezier_from_ellipse,
)

# Cython implementations:
from ezdxf.acc.bezier4p import (
    Bezier4P as CBezier4P,
    cubic_bezier_arc_parameters as cython_arc_parameters,
    cubic_bezier_from_arc as cython_bezier_from_arc,
    cubic_bezier_from_ellipse as cython_bezier_from_ellipse,
)
from ezdxf.math import ConstructionEllipse, Vec3
from ezdxf.version import __version__

POINTS = Vec3.list([(0, 0), (1, 0), (1, 1), (0, 1)])


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
        list(c.flattening(0.001))


def bezier4p_arc_parameters(func, count):
    for _ in range(count):
        list(func(0, math.tau))


def bezier4p_from_arc(func, count):
    for _ in range(count):
        list(func(center=(1, 2), radius=1.0, start_angle=0, end_angle=360))


def bezier4p_from_ellipse(func, count):
    ellipse = ConstructionEllipse(
        center=(1, 2),
        major_axis=(2, 0),
        ratio=0.5,
        start_param=0,
        end_param=math.tau,
    )
    for _ in range(count):
        list(func(ellipse))


def profile1(func, *args) -> float:
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    return t1 - t0


def profile(text, func, pytype, cytype, *args):
    pytime = profile1(func, pytype, *args)
    cytime = profile1(func, cytype, *args)
    ratio = pytime / cytime
    print(f"Python - {text} {pytime:.3f}s")
    print(f"Cython - {text} {cytime:.3f}s")
    print(f"Ratio {ratio:.1f}x")
    log(func.__name__, pytime, cytime)


print(f"Profiling Bezier4P Python and Cython implementation:")
profile(
    f"calc 300.000x points of Bezier4P: ",
    bezier4p_points,
    Bezier4P,
    CBezier4P,
    300_000,
)
profile(
    f"10.000x approximate 32 points of Bezier4P: ",
    bezier4p_approximate,
    Bezier4P,
    CBezier4P,
    10_000,
)
profile(
    f"10.000x flattening (0.01) of Bezier4P: ",
    bezier4p_flattening,
    Bezier4P,
    CBezier4P,
    10_000,
)
profile(
    f"100.000x calc bezier arc parameters: ",
    bezier4p_arc_parameters,
    cubic_bezier_arc_parameters,
    cython_arc_parameters,
    100_000,
)
profile(
    f"20.000x calc bezier curve from arc: ",
    bezier4p_from_arc,
    cubic_bezier_from_arc,
    cython_bezier_from_arc,
    20_000,
)
profile(
    f"20.000x calc bezier curve from ellipse: ",
    bezier4p_from_ellipse,
    cubic_bezier_from_ellipse,
    cython_bezier_from_ellipse,
    20_000,
)
