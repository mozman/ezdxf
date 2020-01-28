# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.math import OCS

doc = ezdxf.new('R2010')
msp = doc.modelspace()

# For this example the OCS is rotated around x-axis about 45 degree
# OCS z-axis: x=0, y=1, z=1
# extrusion vector must not normalized here
ocs = OCS((0, 1, 1))
msp.add_circle(
    # You can place the 2D circle in 3D space
    # but you have to convert WCS into OCS
    center=ocs.from_wcs((0, 2, 2)),
    # center in OCS: (0.0, 0.0, 2.82842712474619)
    radius=1,
    dxfattribs={
        # here the extrusion vector should be normalized,
        # which is granted by using the ocs.uz
        'extrusion': ocs.uz,
        'color': 1,
    })
# mark center point of circle in WCS
msp.add_point((0, 2, 2), dxfattribs={'color': 1})

print(f"center in OCS: {ocs.from_wcs((0, 2, 2))}")
ocs.render_axis(msp)
doc.saveas('ocs_circle.dxf')
