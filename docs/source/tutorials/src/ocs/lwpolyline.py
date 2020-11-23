# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.math import Vec3, UCS
from pathlib import Path

OUT_DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new('R2010')
msp = doc.modelspace()

# The center of the pentagon should be (0, 2, 2), and the shape is
# rotated around x-axis about 45 degree, to accomplish this I use an
# UCS with z-axis (0, 1, 1) and an x-axis parallel to WCS x-axis.
ucs = UCS(
    origin=(0, 2, 2),  # center of pentagon
    ux=(1, 0, 0),  # x-axis parallel to WCS x-axis
    uz=(0, 1, 1),  # z-axis
)
# calculating corner points in local (UCS) coordinates
points = [Vec3.from_deg_angle((360 / 5) * n) for n in range(5)]
# converting UCS into OCS coordinates
ocs_points = list(ucs.points_to_ocs(points))

# LWPOLYLINE accepts only 2D points and has an separated DXF attribute elevation.
# All points have the same z-axis (elevation) in OCS!
elevation = ocs_points[0].z

msp.add_lwpolyline(
    points=ocs_points,
    format='xy',  # ignore z-axis
    dxfattribs={
        'elevation': elevation,
        'extrusion': ucs.uz,
        'closed': True,
        'color': 1,
    })

from ezdxf.math import OCS

OCS(ucs.uz).render_axis(msp)
ucs.render_axis(msp)
doc.saveas(OUT_DIR / 'ocs_lwpolyline.dxf')
