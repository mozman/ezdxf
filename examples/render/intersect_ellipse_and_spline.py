#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import ezdxf
from ezdxf import colors
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.math import intersect_polylines_2d, Vec2

DIR = Path("~/Desktop/Outbox").expanduser()
ENTITIES = "ENTITIES"
INTERSECTION_POINTS = "INTERSECTION_POINTS"
CURVE_APPROXIMATIONS = "CURVE_APPROXIMATIONS"


def main():
    doc = ezdxf.new()
    doc.layers.add(ENTITIES, color=colors.YELLOW)
    doc.layers.add(INTERSECTION_POINTS, color=colors.RED)
    doc.layers.add(CURVE_APPROXIMATIONS, color=colors.CYAN)
    msp = doc.modelspace()
    ellipse = msp.add_ellipse(
        center=(0, 0),
        major_axis=(3, 0),
        ratio=0.5,
        dxfattribs=GfxAttribs(layer=ENTITIES),
    )
    fit_points = [(-4, -4), (-2, -1), (2, 1), (4, 4)]
    spline = msp.add_spline_control_frame(
        fit_points, dxfattribs=GfxAttribs(layer=ENTITIES)
    )

    p1 = Vec2.list(ellipse.flattening(distance=0.001))
    p2 = Vec2.list(spline.flattening(distance=0.001))
    msp.add_lwpolyline(p1, dxfattribs=GfxAttribs(layer=CURVE_APPROXIMATIONS))
    msp.add_lwpolyline(p2, dxfattribs=GfxAttribs(layer=CURVE_APPROXIMATIONS))
    res = intersect_polylines_2d(p1, p2)
    for point in res:
        msp.add_circle(
            center=point,
            radius=0.1,
            dxfattribs=GfxAttribs(layer=INTERSECTION_POINTS),
        )
    doc.set_modelspace_vport(height=10)
    doc.saveas(DIR / "intersect_ellipse_and_spline.dxf")


if __name__ == "__main__":
    main()
