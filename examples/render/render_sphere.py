# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License

from pathlib import Path
import ezdxf

from ezdxf.render.forms import sphere

DIR = Path("~/Desktop/Outbox").expanduser()

doc = ezdxf.new()
doc.layers.new("form", dxfattribs={"color": 5})
doc.layers.new("csg", dxfattribs={"color": 1})
doc.layers.new("normals", dxfattribs={"color": 6})

doc.set_modelspace_vport(6, center=(5, 0))
msp = doc.modelspace()

sphere1 = sphere(count=32, stacks=16, radius=1, quads=True)

sphere1.render_polyface(msp, dxfattribs={"layer": "form"})
sphere1.render_normals(msp, dxfattribs={"layer": "normals"})

doc.saveas(DIR / "sphere.dxf")
