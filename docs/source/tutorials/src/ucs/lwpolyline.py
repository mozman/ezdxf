# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
from pathlib import Path
OUT_DIR = Path('~/Desktop/Outbox').expanduser()

import math
import ezdxf
from ezdxf.math import Vector, UCS

doc = ezdxf.new('R2010')
msp = doc.modelspace()

# The center of the pentagon should be (0, 2, 2), and the shape is
# rotated around x-axis about -45 degree
ucs = UCS(origin=(0, 2, 2)).rotate_local_x(math.radians(-45))

msp.add_lwpolyline(
    # calculating corner points in UCS coordinates
    points=(Vector.from_deg_angle((360 / 5) * n) for n in range(5)),
    format='xy',  # ignore z-axis
    dxfattribs={
        'closed': True,
        'color': 1,
    }
).transform(ucs.matrix)

ucs.render_axis(msp)
doc.saveas(OUT_DIR / 'ucs_lwpolyline.dxf')
