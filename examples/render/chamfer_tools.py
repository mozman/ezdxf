#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib

import ezdxf
from ezdxf.math import Vec3
from ezdxf.path import chamfer, chamfer2, fillet, polygonal_fillet, Path

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use the chamfer and fillet tools.
# ------------------------------------------------------------------------------


def chamfer_tool():
    doc = ezdxf.new()
    msp = doc.modelspace()

    for angle in range(-165, 180, 15):
        points = Vec3.list([(-100, 0), (0, 0), Vec3.from_deg_angle(angle, 100)])
        p = chamfer(points, length=3.0)
        msp.add_polyline3d(p.flattening(0))

    doc.saveas(CWD / "chamfer.dxf")


def chamfer2_tool():
    doc = ezdxf.new()
    msp = doc.modelspace()

    for angle in range(-165, 180, 15):
        points = Vec3.list([(-100, 0), (0, 0), Vec3.from_deg_angle(angle, 100)])
        p = chamfer2(points, a=3, b=6)
        msp.add_polyline3d(p.flattening(0))

    doc.saveas(CWD / "chamfer2.dxf")


def fillet_tool():
    doc = ezdxf.new()
    msp = doc.modelspace()

    for angle in range(-165, 180, 15):
        points = Vec3.list(
            [(-100, 0), (0, 0), Vec3.from_deg_angle(angle, 100)]
        )
        p = fillet(points, radius=10.0)
        msp.add_polyline3d(p.flattening(0.1))

    doc.saveas(CWD / "fillet.dxf")


def polygonal_fillet_tool():
    doc = ezdxf.new()
    msp = doc.modelspace()

    for angle in range(-165, 180, 15):
        points = Vec3.list(
            [(-100, 0), (0, 0), Vec3.from_deg_angle(angle, 100)]
        )
        p = polygonal_fillet(points, radius=10.0, count=16)
        msp.add_polyline3d(p.flattening(0))

    doc.saveas(CWD / "polygonal_fillet.dxf")


def square_with_single_edge_fillet():
    # This example creates a square with a fillet on a single corner.
    p = Path()
    p.line_to((10, 0))
    f = fillet(Vec3.list([(10, 0), (10, 10), (0, 10)]), radius=2)
    # combine the paths:
    p.append_path(f)
    p.close()

    doc = ezdxf.new()
    doc.modelspace().add_polyline2d(p.flattening(0.1))
    doc.saveas(CWD / "square_with_single_edge_fillet.dxf")


if __name__ == "__main__":
    chamfer_tool()
    chamfer2_tool()
    fillet_tool()
    polygonal_fillet_tool()
    square_with_single_edge_fillet()
