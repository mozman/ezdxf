#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.render import forms
from ezdxf.acis import api as acis

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

doc = ezdxf.new("R2004")
msp = doc.modelspace()

# create the ACIS body entity from the cube-mesh
body = acis.body_from_mesh(forms.cube())
# create the DXF 3DSOLID entity
solid3d = msp.add_3dsolid()
# set SAT data for DXF R2004
solid3d.sat = acis.export_sat([body])

doc.set_modelspace_vport(5)
doc.saveas(DIR / "acis_cube_R2004.dxf")
