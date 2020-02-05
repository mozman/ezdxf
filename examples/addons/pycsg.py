# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.addons.pycsg import CSG
from ezdxf.render.forms import cube, cylinder
from math import radians

DIR = Path('~/Desktop/Outbox').expanduser()


builder = cube()
builder.scale_uniform(2)
csg_cube = CSG.from_mesh_builder(builder).refine()

builder = cylinder(count=16, radius=0.5, top_center=(0, 0, 4))
builder.translate(0, 0, -2)
builder.rotate_x(radians(90))
csg_cylinder = CSG.from_mesh_builder(builder)

doc = ezdxf.new()
doc.set_modelspace_vport(6, center=(5, 0))
msp = doc.modelspace()

csg_cube.subtract(csg_cylinder).to_mesh_builder().render(msp)
m = csg_cube.union(csg_cylinder).to_mesh_builder()
m.translate(4)
m.render(msp)
m = csg_cube.intersect(csg_cylinder).to_mesh_builder()
m.translate(8)
m.render(msp)

doc.saveas(DIR / 'pycsg01.dxf')
