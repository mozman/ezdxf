# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
# include-start
import ezdxf
from ezdxf.algebra import Vector, UCS

dwg = ezdxf.new('R2010')
msp = dwg.modelspace()

# center point of the pentagon should be (0, 2, 2), and the shape is
# rotated around x-axis about 45 degree, to accomplish this I use an
# UCS with z-axis (0, 1, 1) and an x-axis parallel to WCS x-axis.
ucs = UCS(
    origin=(0, 2, 2),  # center of pentagon
    ux=(1, 0, 0),  # x-axis parallel to WCS x-axis
    uz=(0, 1, 1),  # z-axis
)
# calculating corner points in local (UCS) coordinates
points = [Vector.from_deg_angle((360/5)*n) for n in range(5)]
# converting UCS into OCS coordinates
ocs_points = list(ucs.points_to_ocs(points))

# LWPOLYLINE accepts only 2D points and has an separated DXF attribute elevation.
# All points have the same z-axis (elevation) in OCS!
elevation = ocs_points[0].z

msp.add_lwpolyline(
    # LWPOLYLINE point format: (x, y, [start_width, [end_width, [bulge]]])
    # the z-axis would be start_width, so remove it
    points=[p[:2] for p in ocs_points],
    dxfattribs={
        'elevation': elevation,
        'extrusion': ucs.uz,
        'closed': True,
        'color': 2,
    })
# include-end

from ezdxf.algebra import OCS
OCS(ucs.uz).render_axis(msp)
ucs.render_axis(msp)
dwg.saveas('ocs_lwpolyline.dxf')
