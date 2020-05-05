# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import math
import random
import ezdxf
from ezdxf.math import linspace, Vector

DIR = Path('~/Desktop/Outbox/ezdxf').expanduser()

doc = ezdxf.new('R2000')
msp = doc.modelspace()


def transform(entity, sx=1, sy=1, sz=1, color=1, check=None):
    e = entity.copy()
    e.scale(sx, sy, sz)
    e.dxf.layer = f'scale {sx} {sy} {sz}'
    e.dxf.color = color
    msp.add_entity(e)
    if check:
        transform(check, sx, sy, sz, 6)


entity = msp.add_circle((0, 0, 0), radius=1)
control_polygon = msp.add_polyline3d(entity.vertices(linspace(0, 360, 16)), dxfattribs={'layer': 'check', 'color': 6})

axis = Vector.random()
angle = random.uniform(0, math.tau)

entity.rotate_axis(axis, angle)
entity.translate(2, 2, 2)

control_polygon.rotate_axis(axis, angle)
control_polygon.translate(2, 2, 2)


transform(entity, -1, 1, 1, 3, check=control_polygon)
transform(entity, -2, -2, 2, 3, check=control_polygon)
transform(entity, -3, -3, -3, 3, check=control_polygon)

doc.set_modelspace_vport(5)
doc.saveas(DIR / 'transform.dxf')
