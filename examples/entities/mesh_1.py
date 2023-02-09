# Copyright (c) 2016-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.render import MeshBuilder
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.math import Matrix44


CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to add a MESH entity by setting vertices and faces.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/mesh.html
# ------------------------------------------------------------------------------


# 8 corner vertices
cube_vertices = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (1, 1, 1),
    (0, 1, 1),
]

# 6 cube faces
cube_faces = [
    [0, 3, 2, 1],
    [4, 5, 6, 7],
    [0, 1, 5, 4],
    [1, 2, 6, 5],
    [3, 7, 6, 2],
    [0, 4, 7, 3],
]
# The DXF format doesn't care about the face orientation, but it is a good
# practice to use always the same orientation. The best choice is to use
# outward pointing faces, the vertices are counter-clockwise oriented around the
# normal vector of each face.

# The MESH entity requires the DXF R2000 or newer format.
doc = ezdxf.new("R2018")
msp = doc.modelspace()
mesh = msp.add_mesh(dxfattribs=GfxAttribs(color=6))
with mesh.edit_data() as mesh_data:
    mesh_data.vertices = cube_vertices
    mesh_data.faces = cube_faces

# Add the same mesh as PolyFaceMesh:
mesh_builder = MeshBuilder.from_mesh(mesh)
mesh_builder.render_polyface(
     msp,
     dxfattribs=GfxAttribs(color=6),
     matrix=Matrix44.translate(5, 0, 0),
 )
doc.saveas(CWD / "cube_mesh_1.dxf")
