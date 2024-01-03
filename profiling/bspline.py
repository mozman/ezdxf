# Copyright (c) 2020-2024, Manfred Moitzi
# License: MIT License
import sys
import time
from datetime import datetime
from pathlib import Path
import numpy as np

from ezdxf.acc import USE_C_EXT
from ezdxf.version import __version__

# Python implementations:
from ezdxf.math._bspline import Basis, Evaluator

if USE_C_EXT is False:
    print("C-extension disabled or not available. (pypy3?)")
    print("Cython implementation == Python implementation.")
    CBasis = Basis
    CEvaluator = Evaluator
else:
    # Cython implementations:
    from ezdxf.acc.bspline import Basis as CBasis, Evaluator as CEvaluator

from ezdxf.render import random_3d_path
from ezdxf.math import fit_points_to_cad_cv

SPLINE_COUNT = 20
POINT_COUNT = 20
splines = [
    fit_points_to_cad_cv(random_3d_path(POINT_COUNT))
    for _ in range(SPLINE_COUNT)
]


class PySpline:
    def __init__(self, bspline, weights=None):
        self.basis = Basis(
            bspline.knots(), bspline.order, bspline.count, weights
        )
        self.evaluator = Evaluator(self.basis, bspline.control_points)

    def point(self, u):
        return self.evaluator.point(u)

    def points(self, t):
        return self.evaluator.points(t)

    def derivative(self, u, n):
        return self.evaluator.derivative(u, n)

    def derivatives(self, t, n):
        return self.evaluator.derivatives(t, n)


class CySpline(PySpline):
    def __init__(self, bspline, weights=None):
        self.basis = CBasis(
            bspline.knots(), bspline.order, bspline.count, weights
        )
        self.evaluator = CEvaluator(self.basis, bspline.control_points)


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
    py_version = sys.version.replace("\n", " ")
    log_file.write(
        f'{timestamp}; {pytime}; {cytime}; "{py_version}"; "{__version__}"\n'
    )
    log_file.close()


def bspline_points(cls, count):
    for curve in splines:
        spline = cls(curve)
        for u in np.linspace(0, spline.basis.max_t, count):
            spline.point(u)


def bspline_multi_points(cls, count):
    for curve in splines:
        spline = cls(curve)
        list(spline.points(np.linspace(0, spline.basis.max_t, count)))


def bspline_derivative(cls, count):
    for curve in splines:
        spline = cls(curve)
        for u in np.linspace(0, spline.basis.max_t, count):
            spline.derivative(u, 1)


def bspline_multi_derivative(cls, count):
    for curve in splines:
        spline = cls(curve)
        list(spline.derivatives(np.linspace(0, spline.basis.max_t, count), 1))


def bspline_points_rational(cls, count):
    for curve in splines:
        weights = [1.0] * curve.count
        spline = cls(curve, weights)
        for u in np.linspace(0, spline.basis.max_t, count):
            spline.point(u)


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


POINT_COUNT_1 = 10_000
print(f"Profiling BSpline Python and Cython implementation:")
profile(
    f"calc {POINT_COUNT_1}x single point for {SPLINE_COUNT} BSplines: ",
    bspline_points,
    PySpline,
    CySpline,
    POINT_COUNT_1,
)

profile(
    f"calc {POINT_COUNT_1}x single point for {SPLINE_COUNT} rational BSplines: ",
    bspline_points_rational,
    PySpline,
    CySpline,
    POINT_COUNT_1,
)

profile(
    f"calc {POINT_COUNT_1}x multi point for {SPLINE_COUNT} BSplines: ",
    bspline_multi_points,
    PySpline,
    CySpline,
    POINT_COUNT_1,
)

profile(
    f"calc {POINT_COUNT_1}x single point & derivative for {SPLINE_COUNT} BSplines: ",
    bspline_derivative,
    PySpline,
    CySpline,
    POINT_COUNT_1,
)

profile(
    f"calc {POINT_COUNT_1}x multi point & derivative for {SPLINE_COUNT} BSplines: ",
    bspline_multi_derivative,
    PySpline,
    CySpline,
    POINT_COUNT_1,
)
