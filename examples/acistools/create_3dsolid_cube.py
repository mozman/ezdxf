#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.render import forms
from ezdxf.acis import api as acis

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

# R2000 and ACIS 700 works also with Autodesk Trueview!

# R2004 requirement
# 20800 ...
# @33 ... @14 ACIS 208.00 NT @24 ...
# asmheader $-1 -1 @12 208.0.4.7009
# End-of-ACIS-data

VERSION = "R2000"
doc = ezdxf.new(VERSION)
msp = doc.modelspace()

# create the ACIS body entity from the cube-mesh
body = acis.body_from_mesh(forms.cube())
# create the DXF 3DSOLID entity
solid3d = msp.add_3dsolid()
# set SAT data for DXF R2004
sat = acis.export_sat([body], doc.dxfversion)
solid3d.sat = sat


doc.set_modelspace_vport(5)
doc.saveas(DIR / f"acis_cube_{VERSION}.dxf")
with open(DIR / f"acis_cube_{VERSION}.sat", "wt") as fp:
    fp.writelines("\n".join(sat))

debugger = acis.AcisDebugger(body)
for e in debugger.entities.values():
    print(e)
    print("\n".join(debugger.entity_attributes(e, 2)))
print(f"{len(debugger.entities)} entities\n")
print("face link structure:")
for shell in debugger.filter_type("shell"):
    print("\n".join(debugger.face_link_structure(shell.face)))
    print("\nloop vertices:")
    for face in shell.faces():
        print(face)
        print(debugger.loop_vertices(face.loop))
