from typing import Iterable
from pathlib import Path
import math
import ezdxf
from ezdxf import zoom
from ezdxf.math import Vec3, estimate_tangents, linspace, estimate_end_tangent_magnitude
from ezdxf.math import local_cubic_bspline_interpolation, global_bspline_interpolation

DIR = Path('~/Desktop/Outbox').expanduser()


def sine_wave(count: int, scale: float = 1.0) -> Iterable[Vec3]:
    for t in linspace(0, math.tau, count):
        yield Vec3(t * scale, math.sin(t) * scale)


doc = ezdxf.new()
msp = doc.modelspace()

# Calculate 8 points on sine wave as interpolation data
data = list(sine_wave(count=8, scale=2.0))

# Reference curve as fine approximation
msp.add_lwpolyline(sine_wave(count=800, scale=2.0), dxfattribs={'color': 1, 'layer': 'Reference curve (LWPolyline)'})

# AutoCAD/BricsCAD interpolation
msp.add_spline(data, dxfattribs={'layer': 'BricsCAD B-spline', 'color': 2})

# tangent estimation method
METHOD = '5-p'

# create not normalized tangents (default is normalized)
tangents = estimate_tangents(data, METHOD, normalize=False)

# show tangents
for p, t in zip(data, tangents):
    msp.add_line(p, p + t, dxfattribs={'color': 5, 'layer': f'Estimated tangents ({METHOD})'})

# local interpolation: a normalized tangent vector for each data point is required,
s = local_cubic_bspline_interpolation(data, tangents=[t.normalize() for t in tangents])
# or set argument 'method' for automatic tangent estimation, default method is '5-points' interpolation
# s = local_cubic_bspline_interpolation(data, method=METHOD)
msp.add_spline(dxfattribs={'color': 3, 'layer': f'Local interpolation ({METHOD})'}).apply_construction_tool(s)

# global interpolation: take first and last vector from 'tangents' as start- and end tangent
m1, m2 = estimate_end_tangent_magnitude(data, method='chord')
s = global_bspline_interpolation(data, tangents=(tangents[0].normalize(m1), tangents[-1].normalize(m2)))
msp.add_spline(dxfattribs={'color': 4, 'layer': f'Global interpolation ({METHOD})'}).apply_construction_tool(s)

zoom.extends(msp, factor=1.1)
doc.saveas(DIR / f'sine-wave-{METHOD}.dxf')
