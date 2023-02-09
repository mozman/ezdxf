# Copyright (c) 2010-2021, Manfred Moitzi
# License: MIT License
import pathlib
from math import radians
import ezdxf
from ezdxf.render import EulerSpiral
from ezdxf.math import basic_transformation


CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use the ezdxf.render.EulerSpiral class.
# The DXF format does not support euler-spirals, therefore they can only be
# approximated by polylines.
#
# docs: https://ezdxf.mozman.at/docs/render/curves.html#eulerspiral
# ------------------------------------------------------------------------------

NAME = "euler_spiral.dxf"


def four_c(msp, curvature, length, rotation):
    spiral = EulerSpiral(curvature=curvature)
    render(
        msp,
        spiral,
        length,
        tmatrix(2, 2, angle=rotation),
        dxfattribs={"color": 1},
    )
    # scaling sx=-1 is mirror about y-axis
    render(
        msp,
        spiral,
        length,
        tmatrix(2, 2, sx=-1, sy=1, angle=rotation),
        dxfattribs={"color": 2},
    )
    # scaling sy=-1 is mirror about x-axis
    render(
        msp,
        spiral,
        length,
        tmatrix(2, 2, sx=1, sy=-1, angle=rotation),
        dxfattribs={"color": 3},
    )
    render(
        msp,
        spiral,
        length,
        tmatrix(2, 2, sx=-1, sy=-1, angle=rotation),
        dxfattribs={"color": 4},
    )


def render(msp, spiral, length, matrix, dxfattribs):
    spiral.render_polyline(
        msp, length, segments=100, matrix=matrix, dxfattribs=dxfattribs
    )
    spiral.render_spline(
        msp,
        length,
        fit_points=10,
        matrix=matrix,
        dxfattribs={"color": 6, "linetype": "DASHED"},
    )


def tmatrix(dx, dy, sx=1, sy=1, angle=0):
    return basic_transformation(
        move=(dx, dy), scale=(sx, sy, 1), z_rotation=radians(angle)
    )


def main(dxfversion="R2000"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()

    msp.add_line((-20, 0), (20, 0), dxfattribs={"linetype": "PHANTOM"})
    msp.add_line((0, -20), (0, 20), dxfattribs={"linetype": "PHANTOM"})
    for rotation in [0, 30, 45, 60, 75, 90]:
        four_c(msp, 10.0, 25, rotation)

    fname = CWD / f"euler_spiral_{dxfversion}.dxf"
    doc.saveas(fname)
    print(f"created: {fname}")


if __name__ == "__main__":
    main()
