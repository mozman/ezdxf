#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf import colors
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.math import intersect_polylines_2d, Vec2

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to calculate intersection points of arbitrary 2d
# polylines, an ellipse and a spline in this example.
#
# docs: https://ezdxf.mozman.at/docs/math/core.html#ezdxf.math.intersect_polylines_2d
# ------------------------------------------------------------------------------

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
    # create 2D polylines from the DXF entities:
    p1 = Vec2.list(ellipse.flattening(distance=0.001))
    p2 = Vec2.list(spline.flattening(distance=0.001))

    # add the 2D polylines as reference graphics:
    msp.add_lwpolyline(p1, dxfattribs=GfxAttribs(layer=CURVE_APPROXIMATIONS))
    msp.add_lwpolyline(p2, dxfattribs=GfxAttribs(layer=CURVE_APPROXIMATIONS))

    # the intersection calculation between these polylines:
    res = intersect_polylines_2d(p1, p2)

    # add intersection points as CIRCLE entities:
    for point in res:
        msp.add_circle(
            center=point,
            radius=0.1,
            dxfattribs=GfxAttribs(layer=INTERSECTION_POINTS),
        )
    doc.set_modelspace_vport(height=10)
    doc.saveas(CWD / "intersect_ellipse_and_spline.dxf")


if __name__ == "__main__":
    main()
