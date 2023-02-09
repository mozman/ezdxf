# Copyright (c) 2016-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create a MESH entity by adding faces as list of
# vertices.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/mesh.html
# ------------------------------------------------------------------------------

# 8 corner vertices
p = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (1, 1, 1),
    (0, 1, 1),
]

# The MESH entity requires the DXF R2000 or newer format.
doc = ezdxf.new("R2000")
msp = doc.modelspace()
mesh = msp.add_mesh()

with mesh.edit_data() as mesh_data:
    # The DXF format doesn't care about the face orientation, but it is a good
    # practice to use always the same orientation. The best choice is to use
    # outward pointing faces, the vertices are counter-clockwise oriented around the
    # normal vector of each face.
    mesh_data.add_face([p[0], p[1], p[2], p[3]])
    mesh_data.add_face([p[4], p[5], p[6], p[7]])
    mesh_data.add_face([p[0], p[1], p[5], p[4]])
    mesh_data.add_face([p[1], p[2], p[6], p[5]])
    mesh_data.add_face([p[3], p[2], p[6], p[7]])
    mesh_data.add_face([p[0], p[3], p[7], p[4]])
    mesh_data.optimize()

doc.saveas(CWD / "cube_mesh_2.dxf")
