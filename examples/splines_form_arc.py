# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.math import rational_spline_from_arc

DIR = Path('~/Desktop/outbox').expanduser()

doc = ezdxf.new()
msp = doc.modelspace()


arc = msp.add_arc(
    center=(0, 0),
    radius=1.0,
    start_angle=15,
    end_angle=225,
    dxfattribs={'layer': 'arc'},
)

for s in rational_spline_from_arc(arc.dxf.center, arc.dxf.radius, arc.dxf.start_angle, arc.dxf.end_angle):
    spline = msp.add_spline(dxfattribs={'color': 1, 'layer': 'B-spline'})
    spline.apply_construction_tool(s)


doc.set_modelspace_vport(2)

doc.saveas(DIR / 'splines_from_arc.dxf')
