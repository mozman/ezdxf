# Copyright (c) 2022, Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.entities import Body

doc = ezdxf.readfile("3dsolids.dxf")
msp = doc.modelspace()

doc_out = ezdxf.new()
msp_out = doc_out.modelspace()

for e in msp.query("3DSOLID"):
    assert isinstance(e, Body)
    data = e.acis_data
    if data:
        for body in acis.load(data):
            for mesh in acis.mesh_from_body(body):
                mesh.render_mesh(msp_out)
doc_out.saveas("meshes.dxf")
