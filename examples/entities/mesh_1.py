# Copyright (c) 2016-2021 Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.render import MeshBuilder
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.math import Matrix44

DIR = Path("~/Desktop/Outbox").expanduser()


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
doc.saveas(DIR / "cube_mesh_1.dxf")
