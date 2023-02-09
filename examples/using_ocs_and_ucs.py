# Copyright (c) 2019-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.math import UCS, OCS

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to place a 2D entity in 3D by using OCS coordinates.
#
# basic concept OCS: https://ezdxf.mozman.at/docs/concepts/ocs.html
# OCS: https://ezdxf.mozman.at/docs/math/core.html#ocs-class
# UCS: https://ezdxf.mozman.at/docs/math/core.html#ucs-class
# tutorial: https://ezdxf.mozman.at/docs/tutorials/ucs_transform.html
# ------------------------------------------------------------------------------


def main(filename):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    origin = (3, 3, 3)
    axis = (1, 0, -1)
    def_point = (3, 10, 4)

    ucs = UCS.from_z_axis_and_point_in_yz(origin, axis=axis, point=def_point)
    ucs.render_axis(msp, length=5)
    msp.add_point(location=def_point, dxfattribs={"color": 2})

    ocs = OCS(ucs.uz)
    msp.add_circle(
        center=ocs.from_wcs(origin),
        radius=1,
        dxfattribs={
            "color": 2,
            "extrusion": ucs.uz,
        },
    )
    doc.saveas(filename)


if __name__ == "__main__":
    main(CWD / "using_ucs.dxf")
