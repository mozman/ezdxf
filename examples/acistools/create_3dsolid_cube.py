#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.render import forms
from ezdxf.acis import api as acis

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

VERSION = "R2010"
DEBUG = False
OPEN_SHELL = False

doc = ezdxf.new(VERSION)
msp = doc.modelspace()


# create the ACIS body entity from the cube-mesh
cube = forms.cube()
if OPEN_SHELL:
    cube.faces.pop()

body = acis.body_from_mesh(cube)
# create the DXF 3DSOLID entity
solid3d = msp.add_3dsolid()
acis.export_dxf(solid3d, [body])

doc.set_modelspace_vport(5)
doc.saveas(DIR / f"acis_cube_{VERSION}.dxf")
if solid3d.has_binary_data:
    with open(DIR / f"acis_cube_{VERSION}.sab.txt", "wt") as fp:
        fp.writelines("\n".join(acis.dump_sab_as_text(solid3d.sab)))
else:
    with open(DIR / f"acis_cube_{VERSION}.sat.txt", "wt") as fp:
        fp.writelines("\n".join(solid3d.sat))

if DEBUG:
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
