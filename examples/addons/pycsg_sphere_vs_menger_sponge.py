# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
from time import perf_counter
import ezdxf

from ezdxf.render.forms import sphere
from ezdxf.addons import MengerSponge
from ezdxf.addons.pycsg import CSG

DIR = Path("~/Desktop/Outbox").expanduser()

doc = ezdxf.new()
doc.layers.new("sponge", dxfattribs={"color": 5})
doc.layers.new("sphere", dxfattribs={"color": 6})

doc.set_modelspace_vport(6, center=(5, 0))
msp = doc.modelspace()

sponge1 = MengerSponge(level=3).mesh()
sphere1 = sphere(count=32, stacks=16, radius=0.5, quads=True).translate(
    0.25, 0.25, 1
)

t0 = perf_counter()
subtract = CSG(sponge1, meshid=1) - CSG(sphere1, meshid=2)
t1 = perf_counter()
# get mesh result by id
subtract.mesh(1).render_mesh(msp, dxfattribs={"layer": "sponge"})
subtract.mesh(2).render_mesh(msp, dxfattribs={"layer": "sphere"})

print(f"runtime: {t1-t0:.3f}s")
doc.saveas(DIR / "csg_sphere_vs_menger_sponge.dxf")
