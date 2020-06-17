from typing import Iterable
from pathlib import Path
import ezdxf
import math
from ezdxf.math import Vector, estimate_tangents, linspace
from ezdxf.math.bspline import local_cubic_bspline_interpolation, global_bspline_interpolation

DIR = Path('~/Desktop/Outbox').expanduser()


def sin_curve(count: int, scale: float = 1.0) -> Iterable[Vector]:
    for t in linspace(0, math.tau, count):
        yield Vector(t * scale, math.sin(t) * scale)


doc = ezdxf.new()
msp = doc.modelspace()
points = list(sin_curve(8, 2.0))
# Reference curve as fine approximation
msp.add_lwpolyline(sin_curve(800, 2.0), dxfattribs={'color': 1, 'layer': 'Reference curve (LWPolyline)'})

# AutoCAD/BricsCAD interpolation
msp.add_spline(points, dxfattribs={'layer': 'BricsCAD B-spline', 'color': 2})

# ezdxf interpolation
METHOD = 'diff'

tangents = estimate_tangents(points, METHOD, normalize=True)
# show tangents
for p, t in zip(points, tangents):
    msp.add_line(p, p + t, dxfattribs={'color': 5, 'layer': f'Estimated tangents ({METHOD})'})

bspline = local_cubic_bspline_interpolation(points, tangents=tangents)
msp.add_spline(dxfattribs={'color': 3, 'layer': f'Local interpolation ({METHOD})'}).apply_construction_tool(bspline)

s = global_bspline_interpolation(points, tangents=(tangents[0], tangents[-1]))
msp.add_spline(dxfattribs={'color': 4, 'layer': f'Global interpolation ({METHOD})'}).apply_construction_tool(s)

doc.set_modelspace_vport(5, center=(4, 1))
doc.saveas(DIR / 'B-spline.dxf')
