# Copyright (c) 2022, Manfred Moitzi
# License: MIT License

from pathlib import Path
import math
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

closed_torus = torus(major_count=32, minor_count=16)
closed_torus.render_mesh(msp, dxfattribs={"layer": "form"})
closed_torus.render_normals(msp, dxfattribs={"layer": "normals"})

open_torus = torus(major_count=16, minor_count=16, end_angle=math.pi, caps=True)
open_torus.translate(5)
open_torus.render_mesh(msp, dxfattribs={"layer": "form"})
open_torus.render_normals(msp, dxfattribs={"layer": "normals"})

doc.saveas(DIR / "torus.dxf")
