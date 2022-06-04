#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.addons import MengerSponge
from ezdxf.acis import api as acis

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

VERSION = "R2010"
doc = ezdxf.new(VERSION)
msp = doc.modelspace()

# The Menger sponge can be opened by BricsCAD and DWG TrueView,
# but BricsCAD RECOVER finds an error:
# "Coedges out of order about edge"
# No idea how to fix this!

menger = MengerSponge(length=3.0, level=1).mesh()
menger.translate(10, 0, 5)
# create the ACIS body entity from the uv-sphere mesh (polyhedron)
body = acis.body_from_mesh(menger)
# create the DXF 3DSOLID entity
solid3d = msp.add_3dsolid()
acis.export_dxf(solid3d, [body])

doc.set_modelspace_vport(5, center=(10, 0))
doc.saveas(DIR / f"acis_menger_sponge_{VERSION}.dxf")
