# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
from pathlib import Path
OUT_DIR = Path('~/Desktop/Outbox').expanduser()

import math
import ezdxf
from ezdxf.math import UCS

doc = ezdxf.new('R2010')
msp = doc.modelspace()

ucs = UCS()  # New default UCS
# All rotation angles in radians, and rotation
# methods always return a new UCS.
ucs = ucs.rotate_local_x(math.radians(-45))
circle = msp.add_circle(
    # Use UCS coordinates to place the 2d circle in 3d space
    center=(0, 0, 2),
    radius=1,
    dxfattribs={'color': 1}
)
circle.transform_to_wcs(ucs)

# mark center point of circle in WCS
msp.add_point((0, 0, 2), dxfattribs={'color': 1}).transform_to_wcs(ucs)

ucs.render_axis(msp)
doc.saveas(OUT_DIR / 'ucs_circle.dxf')
