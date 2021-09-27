# Copyright (c) 2019-2021, Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.math import UCS, OCS


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
    main("using_ucs.dxf")
