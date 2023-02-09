#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import math
import ezdxf
from ezdxf.math import UCS, Vec3
from ezdxf.layouts import Modelspace

# ------------------------------------------------------------------------------
# This example shows how to create a dimension in 3d space and as addition how
# to explode this dimension.
#
# tutorial: https://ezdxf.mozman.at/docs/tutorials/angular_dimension.html
# ------------------------------------------------------------------------------

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


def make_doc():
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    base = Vec3(0, 5)
    p1 = Vec3(-4, 3)
    p2 = Vec3(-1, 0)
    p4 = Vec3(4, 3)
    p3 = Vec3(1, 0)

    ucs = UCS(origin=(5, 7, -3)).rotate_local_x(math.radians(45))

    msp.add_line(p1, p2).transform(ucs.matrix)
    msp.add_line(p3, p4).transform(ucs.matrix)

    dim = msp.add_angular_dim_2l(
        base=base, line1=(p1, p2), line2=(p3, p4), dimstyle="EZ_CURVED"
    )
    dim.render(ucs=ucs)
    return doc


def explode_dim(msp: Modelspace):
    for dimension in msp.query("DIMENSION"):
        dimension.explode()  # type: ignore


if __name__ == "__main__":
    doc = make_doc()
    doc.saveas(CWD / "3d_dim.dxf")
    explode_dim(doc.modelspace())
    doc.saveas(CWD / "3d_dim_exploded.dxf")
