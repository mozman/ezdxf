# Copyright (c) 2022, Manfred Moitzi
# License: MIT License

from pathlib import Path
import ezdxf

from ezdxf.render.forms import torus

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

doc = ezdxf.new()
doc.layers.new("form", dxfattribs={"color": 2})
doc.layers.new("normals", dxfattribs={"color": 6})

doc.set_modelspace_vport(6, center=(5, 0))
msp = doc.modelspace()

torus_mesh = torus(major_count=32, minor_count=16)
torus_mesh.render_mesh(msp, dxfattribs={"layer": "form"})
torus_mesh.render_normals(msp, dxfattribs={"layer": "normals"})

doc.saveas(DIR / "torus.dxf")
