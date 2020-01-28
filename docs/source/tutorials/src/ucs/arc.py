# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import math
import ezdxf
from ezdxf.math import UCS, Vector
from pathlib import Path

OUT_DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new('R2010')
msp = doc.modelspace()

ucs = UCS(origin=(0, 2, 2)).rotate_local_x(math.radians(-45))

CENTER = (0, 0)
START_ANGLE = 45
END_ANGLE = 270

msp.add_arc(
    center=CENTER,
    radius=1,
    start_angle=START_ANGLE,
    end_angle=END_ANGLE,
    dxfattribs={'color': 6},
).transform_to_wcs(ucs)

msp.add_line(
    start=CENTER,
    end=Vector.from_deg_angle(START_ANGLE),
    dxfattribs={'color': 6},
).transform_to_wcs(ucs)

msp.add_line(
    start=CENTER,
    end=Vector.from_deg_angle(END_ANGLE),
    dxfattribs={'color': 6},
).transform_to_wcs(ucs)

ucs.render_axis(msp)
doc.saveas(OUT_DIR / 'ucs_arc.dxf')
