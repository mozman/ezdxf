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
DEBUG = True

doc = ezdxf.new(VERSION)
msp = doc.modelspace()

menger = MengerSponge(length=3.0, level=1).mesh()
menger.translate(10, 0, 5)

body = acis.body_from_mesh(menger)
solid3d = msp.add_3dsolid()
acis.export_dxf(solid3d, [body])

doc.set_modelspace_vport(5, center=(10, 0))
doc.saveas(DIR / f"acis_menger_sponge_{VERSION}.dxf")

if DEBUG:
    debugger = acis.AcisDebugger(body)
    with open(DIR / "menger_sponge_entities.log", "wt") as fp:
        for e in debugger.entities.values():
            fp.write(f"\n{e}\n")
            fp.write("\n".join(debugger.entity_attributes(e, 2)))
        fp.write(f"{len(debugger.entities)} entities\n")

    with open(DIR / "menger_sponge_faces.log", "wt") as fp:
        fp.write("face link structure:\n")
        for shell in debugger.filter_type("shell"):
            fp.write("\n".join(debugger.face_link_structure(shell.face)))

    with open(DIR / "menger_sponge_loops.log", "wt") as fp:
        fp.write("face loop structure:\n")
        for shell in debugger.filter_type("shell"):
            for face in shell.faces():
                fp.write(str(face) + "\n")
                fp.write(debugger.loop_vertices(face.loop) + "\n")

    with open(DIR / "menger_sponge_coedges.log", "wt") as fp:
        fp.write("face coedge structure:\n")
        for face in debugger.filter_type("face"):
            fp.write(f"\nFace: {face}\n")
            fp.write("\n".join(debugger.coedge_structure(face, 4)))
