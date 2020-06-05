# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

from pathlib import Path
import math
import ezdxf
from ezdxf.math.bspline import rational_spline_from_ellipse

DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new()
msp = doc.modelspace()

ellipse = msp.add_ellipse(
    center=(1, 1),
    major_axis=(3, 0),
    ratio=0.5,
    start_param=math.pi / 8,
    end_param=math.pi,
    dxfattribs={'layer': 'ellipse'},
)

s = rational_spline_from_ellipse(ellipse.construction_tool())
spline = msp.add_spline(dxfattribs={'color': 1, 'layer': 'B-spline'})
spline.apply_construction_tool(s)

doc.set_modelspace_vport(2)

doc.saveas(DIR / 'ellipse.dxf')
