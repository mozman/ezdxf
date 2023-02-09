# Copyright (c) 2018-2022, Manfred Moitzi
# License: MIT License
import pathlib
from math import radians
import ezdxf
from ezdxf.render.forms import ellipse
from ezdxf.math import basic_transformation

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to get ellipses in DXF R12 files which does not support
# the ELLIPSE entity.
#
# docs:
# ellipse: https://ezdxf.mozman.at/docs/render/forms.html#ezdxf.render.forms.ellipse
# basic_transformation: https://ezdxf.mozman.at/docs/math/core.html#ezdxf.math.basic_transformation
# ------------------------------------------------------------------------------


def render(msp, points):
    msp.add_polyline2d(list(points))


def tmatrix(x, y, angle):
    return basic_transformation((x, y), z_rotation=radians(angle))


def main():

    doc = ezdxf.new("R12", setup=True)
    msp = doc.modelspace()

    for axis in [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]:
        render(msp, ellipse(200, rx=5.0, ry=axis))

    attribs = {
        "color": 1,
        "linetype": "DASHDOT",
    }

    msp.add_line((-7, 0), (+7, 0), dxfattribs=attribs)
    msp.add_line((0, -5), (0, +5), dxfattribs=attribs)

    for rotation in [0, 30, 45, 60, 90]:
        m = tmatrix(20, 0, rotation)
        render(msp, m.transform_vertices(ellipse(100, rx=5.0, ry=2.0)))

    for startangle in [0, 30, 45, 60, 90]:
        m = tmatrix(40, 0, startangle)
        render(
            msp,
            m.transform_vertices(
                ellipse(
                    90,
                    rx=5.0,
                    ry=2.0,
                    start_param=radians(startangle),
                    end_param=radians(startangle + 90),
                )
            ),
        )
        render(
            msp,
            m.transform_vertices(
                ellipse(
                    90,
                    rx=5.0,
                    ry=2.0,
                    start_param=radians(startangle + 180),
                    end_param=radians(startangle + 270),
                )
            ),
        )
    filename = CWD / "ellipse_r12.dxf"
    doc.saveas(filename)
    print(f"drawing {filename} created.")


if __name__ == "__main__":
    main()
