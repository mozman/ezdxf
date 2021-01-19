#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import ezdxf
from ezdxf.render import make_path


doc = ezdxf.new()
msp = doc.modelspace()

ellipse = msp.add_ellipse(
    center=(1999.488177113287, -1598.02265357955, 0.0),
    major_axis=(629.968069297, 0.0, 0.0),
    ratio=0.495263197,
    start_param=-1.261396328799999,
    end_param=-0.2505454928,
    dxfattribs={
        'layer': "0",
        'linetype': "Continuous",
        'color': 3,
        'extrusion': (0.0, 0.0, -1.0),
    },
)

p = make_path(ellipse)
msp.add_lwpolyline(p.approximate(), dxfattribs={
    'layer': 'PathRendering',
    'color': 1,
})
doc.set_modelspace_vport(500, (2400, -1400))
doc.saveas('path_rendering.dxf')