# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import time
import pathlib
import math
import numpy as np

import ezdxf
from ezdxf.math import (
    global_bspline_interpolation,
    BoundingBox,
    BSpline,
)
from ezdxf.render import random_3d_path

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def profile_bspline_interpolation(count, path):
    for _ in range(count):
        global_bspline_interpolation(path)


def profile_vertex_calculation(count, spline, num):
    for _ in range(count):
        for t in np.linspace(0.0, spline.max_t, num):
            spline.point(t)


def profile(text, func, *args):
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    print(f"{text} {t1 - t0:.3f}s")


def export_path(path):
    doc = ezdxf.new()
    msp = doc.modelspace()
    bbox = BoundingBox(path)
    msp.add_polyline3d(path, dxfattribs={"layer": "Path", "color": 2})
    spline = msp.add_spline(dxfattribs={"layer": "B-spline", "color": 1})
    curve = global_bspline_interpolation(path)
    spline.apply_construction_tool(curve)
    doc.set_modelspace_vport(center=bbox.center, height=bbox.size[1])
    doc.saveas(CWD / "path1.dxf")


path = list(random_3d_path(100, max_step_size=10, max_heading=math.pi * 0.8))
export_path(path)

profile("B-spline interpolation 300x: ", profile_bspline_interpolation, 300, path)

spline = BSpline.from_fit_points(path, degree=3)
profile(
    "calculate 25x 1000 B-spline vertices: ",
    profile_vertex_calculation,
    25,
    spline,
    1000,
)
