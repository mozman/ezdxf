# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import ezdxf
from pathlib import Path
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.math import global_bspline_interpolation

wave = [
    (0.0, 0.0), (0.897597901, 0.78183148), (1.79519580, 0.97492791), (2.69279370, 0.433883739),
    (3.59039160, -0.43388373), (4.48798950, -0.97492791), (5.38558740, -0.78183148), (6.28318530, 0.0)
]

DIR = Path('~/Desktop/Outbox').expanduser()
FILE = 'wave'
doc = ezdxf.new()
msp = doc.modelspace()
s = global_bspline_interpolation(wave)
msp.add_spline(dxfattribs={'color': 2}).apply_construction_tool(s)

fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])
backend = MatplotlibBackend(ax)
Frontend(RenderContext(doc), backend).draw_layout(msp)
fig.savefig(DIR / f'{FILE}.png', dpi=300)
