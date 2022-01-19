# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf import colors
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.render import forms

DIR = Path("~/Desktop/Outbox").expanduser()

cube = forms.cube().scale_uniform(10).subdivide(2)
cylinder = forms.cylinder(12, radius=5, top_center=(0, 0, 10)).translate(0, 20)

doc = ezdxf.new()
msp = doc.modelspace()

red = GfxAttribs(color=colors.RED)
green = GfxAttribs(color=colors.GREEN)
blue = GfxAttribs(color=colors.BLUE)

cube.render(msp, dxfattribs=red)
cube.translate(20)
cube.render_polyface(msp, dxfattribs=green)
cube.translate(20)
cube.render_3dfaces(msp, dxfattribs=blue)

cylinder.render(msp, dxfattribs=red)
cylinder.translate(20)
cylinder.render_polyface(msp, dxfattribs=green)
cylinder.translate(20)
cylinder.render_3dfaces(msp, dxfattribs=blue)

doc.set_modelspace_vport(30, center=(30, 20))
doc.saveas(DIR / "meshes.dxf")
