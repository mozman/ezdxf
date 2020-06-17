from typing import Iterable
from pathlib import Path
import math
import ezdxf
from ezdxf.math import Vector, estimate_tangents, linspace
from ezdxf.math import local_cubic_bspline_interpolation, global_bspline_interpolation

DIR = Path('~/Desktop/Outbox').expanduser()


def sine_wave(count: int, scale: float = 1.0) -> Iterable[Vector]:
    for t in linspace(0, math.tau, count):
        yield Vector(t * scale, math.sin(t) * scale)


doc = ezdxf.new()
msp = doc.modelspace()

# Calculate 8 points on sin-curve as interpolation data
data = list(sine_wave(count=8, scale=2.0))

# Reference curve as fine approximation
msp.add_lwpolyline(sine_wave(count=800, scale=2.0), dxfattribs={'color': 1, 'layer': 'Reference curve (LWPolyline)'})

# AutoCAD/BricsCAD interpolation
msp.add_spline(data, dxfattribs={'layer': 'BricsCAD B-spline', 'color': 2})

# ezdxf interpolation
METHOD = 'diff'

# create not normalized tangents (default is normalized)
tangents = estimate_tangents(data, METHOD, normalize=False)

# show tangents
for p, t in zip(data, tangents):
    msp.add_line(p, p + t, dxfattribs={'color': 5, 'layer': f'Estimated tangents ({METHOD})'})

# local interpolation require normalized tangents
s = local_cubic_bspline_interpolation(data, tangents=[t.normalize() for t in tangents])
msp.add_spline(dxfattribs={'color': 3, 'layer': f'Local interpolation ({METHOD})'}).apply_construction_tool(s)

# global interpolation argument 'tangents' accepts only the start- and the end tangent
s = global_bspline_interpolation(data, tangents=(tangents[0], tangents[-1]))
msp.add_spline(dxfattribs={'color': 4, 'layer': f'Global interpolation ({METHOD})'}).apply_construction_tool(s)

doc.set_modelspace_vport(5, center=(4, 1))
doc.saveas(DIR / 'sine-wave.dxf')
