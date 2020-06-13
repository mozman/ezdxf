# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable
import time
import ezdxf
from pathlib import Path
import math
from ezdxf.math import bspline_interpolation, BoundingBox
from ezdxf.render import random_3d_path
from geomdl import fitting
DIR = Path('~/Desktop/Outbox').expanduser()


def profile_ezdxf_interpolation(count, path):
    for _ in range(count):
        bspline_interpolation(path)


def profile_geomdl_interpolation(count, path):
    for _ in range(count):
        fitting.interpolate_curve(path, degree=3)


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

profile('ezdxf B-spline interpolation: ', profile_ezdxf_interpolation, 100, path)
profile('geomdl B-spline interpolation: ', profile_geomdl_interpolation, 100, path)
