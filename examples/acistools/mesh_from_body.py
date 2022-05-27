# Copyright (c) 2022, Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.acis import api as acis
from ezdxf.entities import Body

doc = ezdxf.readfile("3dsolids.dxf")
msp = doc.modelspace()

doc_out = ezdxf.new()
msp_out = doc_out.modelspace()

for e in msp.query("3DSOLID"):
    assert isinstance(e, Body)
    if e.has_binary_data:
        data = e.sab
    else:
        data = e.sat
    if data:
        for body in acis.load(data):
            for mesh in acis.mesh_from_body(body):
                mesh.render_mesh(msp_out)
            print(str(e) + " - face link structure:")
            dbg = acis.AcisDebugger(body)
            for shell in dbg.filter_type("shell"):
                print("\n".join(dbg.face_link_structure(shell.face, 2)))
                print("\nloop vertices:")
                for face in shell.faces():
                    print(face)
                    print(dbg.loop_vertices(face.loop, 2))
                print()

doc_out.saveas("meshes.dxf")
