# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.addons.pycsg import CSG
from ezdxf.render.forms import cube, cylinder_2p

DIR = Path("~/Desktop/Outbox").expanduser()

cube1 = cube()
cylinder1 = cylinder_2p(
    count=32, base_center=(0, -1, 0), top_center=(0, 1, 0), radius=0.25
)

doc = ezdxf.new()
doc.set_modelspace_vport(6, center=(5, 0))
msp = doc.modelspace()

# build solid union
union = CSG(cube1) + CSG(cylinder1)
# convert to mesh and render mesh to modelspace
union.mesh().render_mesh(msp, dxfattribs={"color": 1})

# build solid difference
difference = CSG(cube1) - CSG(cylinder1)
# convert to mesh, translate mesh and render mesh to modelspace
difference.mesh().translate(1.5).render(msp, dxfattribs={"color": 3})

# build solid intersection
intersection = CSG(cube1) * CSG(cylinder1)
# convert to mesh, translate mesh and render mesh to modelspace
intersection.mesh().translate(2.75).render(msp, dxfattribs={"color": 5})

doc.saveas(DIR / "pycsg01.dxf")
