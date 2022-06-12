#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib

import ezdxf
from ezdxf.math import Vec3
from ezdxf.path import chamfer, chamfer2, fillet

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


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


if __name__ == "__main__":
    chamfer_tool()
    chamfer2_tool()
    fillet_tool()
