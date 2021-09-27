# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.render.forms import cube, cylinder

DIR = Path("~/Desktop/Outbox").expanduser()

mycube = cube().scale_uniform(10).subdivide(2)
mycylinder = cylinder(12, radius=5, top_center=(0, 0, 10)).translate(0, 20)

doc = ezdxf.new()
msp = doc.modelspace()

mycube.render(msp, dxfattribs={"color": 1})
mycube.translate(20)
mycube.render_polyface(msp, dxfattribs={"color": 3})
mycube.translate(20)
mycube.render_3dfaces(msp, dxfattribs={"color": 5})

mycylinder.render(msp, dxfattribs={"color": 1})
mycylinder.translate(20)
mycylinder.render_polyface(msp, dxfattribs={"color": 3})
mycylinder.translate(20)
mycylinder.render_3dfaces(msp, dxfattribs={"color": 5})

doc.set_modelspace_vport(30, center=(30, 20))
doc.saveas(DIR / "meshes.dxf")
