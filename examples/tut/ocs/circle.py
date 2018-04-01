# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

# include-start
import ezdxf
from ezdxf.algebra import OCS

dwg = ezdxf.new('R2010')
msp = dwg.modelspace()

# For this example the OCS is rotated around x-axis about 45 degree
# OCS z-axis: x=0, y=1, z=1
# extrusion vector must not normalized here
ocs = OCS((0, 1, 1))
msp.add_circle(
    # You can place the 2D circle in 3D space
    # but you have to convert WCS into OCS
    center=ocs.wcs_to_ocs((0, 2, 2)),
    # center in OCS: (0.0, 0.0, 2.82842712474619)
    radius=1,
    dxfattribs={
        # here the extrusion vector should be normalized,
        # which is granted by using the ocs.uz
        'extrusion': ocs.uz,
        'color': 2,
    })
# mark center point of circle in WCS
msp.add_point((0, 2, 2), dxfattribs={'color': 2})
# include-end

print("center in OCS: {}".format(ocs.wcs_to_ocs((0, 2, 2))))
ocs.render_axis(msp)
dwg.saveas('ocs_circle.dxf')
