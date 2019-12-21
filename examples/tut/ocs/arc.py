# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.math import UCS, Vector

doc = ezdxf.new('R2010')
msp = doc.modelspace()


# include-start
ucs = UCS(origin=(0, 2, 2), ux=(1, 0, 0), uz=(0, 1, 1))
msp.add_arc(
    center=ucs.to_ocs((0, 0)),
    radius=1,
    start_angle=ucs.to_ocs_angle_deg(45),
    end_angle=ucs.to_ocs_angle_deg(270),
    dxfattribs={
        'extrusion': ucs.uz,
        'color': 1,
    })
center = ucs.to_wcs((0, 0))
msp.add_line(
    start=center,
    end=ucs.to_wcs(Vector.from_deg_angle(45)),
    dxfattribs={'color': 1},
)
msp.add_line(
    start=center,
    end=ucs.to_wcs(Vector.from_deg_angle(270)),
    dxfattribs={'color': 1},
)
# include-end

ucs.render_axis(msp)
doc.saveas('ocs_arc.dxf')
