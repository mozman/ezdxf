# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.addons.pycsg import CSG
from ezdxf.render.forms import cube, cylinder
from math import radians

DIR = Path('~/Desktop/Outbox').expanduser()


builder = cube().scale_uniform(2).subdivide()
csg_cube = CSG(builder)

builder = cylinder(count=16, radius=0.5, top_center=(0, 0, 4)).translate(0, 0, -2).rotate_x(radians(90))
csg_cylinder = CSG(builder)

doc = ezdxf.new()
doc.set_modelspace_vport(6, center=(5, 0))
msp = doc.modelspace()

csg_cube.subtract(csg_cylinder).mesh().render(msp)
csg_cube.union(csg_cylinder).mesh().translate(4).render(msp)
csg_cube.intersect(csg_cylinder).mesh().translate(8).render(msp)

doc.saveas(DIR / 'pycsg01.dxf')
