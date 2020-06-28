from typing import cast
from pathlib import Path
import ezdxf
from ezdxf.math import Vector, BSpline

DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.readfile('../../examples/addons/drawing/test_files/hatches_2.dxf')
msp = doc.modelspace()

hatch = cast('Hatch', msp.query('HATCH').first)
if hatch:
    for edge in hatch.paths[0].edges:
        if edge.EDGE_TYPE == 'SplineEdge':
            s = BSpline(control_points=edge.control_points, knots=edge.knot_values, order=edge.degree + 1)
            print(s.knots())
            c = s.to_nurbs_python_curve()
            print(c.knotvector)
            print(s)
            print(list(s.approximate(10)))
