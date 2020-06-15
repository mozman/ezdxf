# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable
import time
import ezdxf
from pathlib import Path
import math
from ezdxf.math import bspline_interpolation, BoundingBox, linspace, BSpline
from ezdxf.render import random_3d_path
DIR = Path('~/Desktop/Outbox').expanduser()


def profile_bspline_interpolation(count, path):
    for _ in range(count):
        bspline_interpolation(path)


def profile_vertex_calculation(count, spline, num):
    for _ in range(count):
        for t in linspace(0.0, spline.max_t, num):
            spline.point(t)


def profile(text, func, *args):
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    print(f'{text} {t1 - t0:.3f}s')


def export_path(path):
    doc = ezdxf.new()
    msp = doc.modelspace()
    bbox = BoundingBox(path)
    msp.add_polyline3d(path, dxfattribs={'layer': 'Path', 'color': 2})
    spline = msp.add_spline(dxfattribs={'layer': 'B-spline', 'color': 1})
    curve = bspline_interpolation(path)
    spline.apply_construction_tool(curve)
    doc.set_modelspace_vport(center=bbox.center, height=bbox.size[1])
    doc.saveas(DIR / 'path1.dxf')


path = list(random_3d_path(100, max_step_size=10, max_heading=math.pi * 0.8))
export_path(path)

profile('B-spline interpolation 100x: ', profile_bspline_interpolation, 100, path)

spline = BSpline.from_fit_points(path, degree=3)
profile('calculate 25x 1000 B-spline vertices: ', profile_vertex_calculation, 25, spline, 1000)
