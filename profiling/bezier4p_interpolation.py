# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import time
import ezdxf
import pathlib
import math
from ezdxf.math import cubic_bezier_interpolation, BoundingBox
from ezdxf.render import random_3d_path

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def profile_bezier_interpolation(count, path):
    for _ in range(count):
        curves = list(cubic_bezier_interpolation(path))


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
    for curve in cubic_bezier_interpolation(path):
        msp.add_polyline3d(
            curve.approximate(20), dxfattribs={"layer": "Bézier", "color": 1}
        )
    doc.set_modelspace_vport(center=bbox.center, height=bbox.size[1])
    doc.saveas(CWD / "path1.dxf")


path = list(random_3d_path(100, max_step_size=10, max_heading=math.pi * 0.8))
export_path(path)

profile("Cubic Bézier interpolation: ", profile_bezier_interpolation, 100, path)
