# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable
import time
import ezdxf
from pathlib import Path
import math
from ezdxf.math import global_bspline_interpolation, linspace
from ezdxf.render import random_3d_path

DIR = Path('~/Desktop/Outbox').expanduser()

path = list(random_3d_path(100, max_step_size=10, max_heading=math.pi * 0.8))
spline = global_bspline_interpolation(path)


def profile_bspline_point_new(count, spline):
    for _ in range(count):
        for t in linspace(0, 1.0, 100):
            spline.point(t)


def profile_bspline_derivatives_new(count, spline):
    for _ in range(count):
        list(spline.derivatives(t=linspace(0, 1.0, 100)))


def profile(text, func, *args):
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    print(f'{text} {t1 - t0:.3f}s')


profile('B-spline point new 300x: ', profile_bspline_point_new, 300, spline)
profile('B-spline derivatives new 300x: ', profile_bspline_derivatives_new, 300, spline)
