# Copyright (c) 2010-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.math import Vec3
from ezdxf.render import Bezier

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use the ezdxf.render.Bezier class.
# The DXF format does not support Bézier curves, therefore they can only be
# approximated by polylines.
#
# docs: https://ezdxf.mozman.at/docs/render/curves.html#bezier
# ------------------------------------------------------------------------------


def draw_control_point(msp, point, tangent1, tangent2=(0, 0)):
    tp1 = Vec3(point) + Vec3(tangent1)
    tp2 = Vec3(point) + Vec3(tangent2)
    attribs = {"color": 1}
    msp.add_circle(radius=0.05, center=point, dxfattribs=attribs)
    attribs["color"] = 2
    msp.add_line(point, tp1, dxfattribs=attribs)
    msp.add_line(point, tp2, dxfattribs=attribs)


def main():
    doc = ezdxf.new("R12")
    msp = doc.modelspace()

    bezier = Bezier()

    # define start point
    bezier.start((2, 4, 1), tangent=(0, 2, 0))
    draw_control_point(msp, (2, 4, 1), (0, 2, 0))

    # append first point
    bezier.append((6, 7, -3), tangent1=(-2, 0, 0), tangent2=(1, 2, 0))
    draw_control_point(msp, (6, 7, -3), (-2, 0, 0), (1, 2, 0))

    # tangent2 = -tangent1 = (+2, 0)
    bezier.append((12, 5, 2), tangent1=(-2, 0, 0))
    draw_control_point(msp, (12, 5, 2), (-2, 0, 0), (2, 0, 0))

    # for last point tangent2 is meaningless
    bezier.append((16, 9, 20), tangent1=(-0.5, -3, 0))
    draw_control_point(msp, (16, 9, 20), (-0.5, -3, 0))

    bezier.render(msp, dxfattribs={"color": 4})
    filename = CWD / "bezier.dxf"
    doc.saveas(filename)
    print(f"drawing {filename} created.")


if __name__ == "__main__":
    main()
