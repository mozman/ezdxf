# Copyright (c) 2016-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.gfxattribs import GfxAttribs

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use subdivision and creases at a MESH entity.
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

doc = ezdxf.new("R2018")
msp = doc.modelspace()
mesh = msp.add_mesh(dxfattribs=GfxAttribs(color=6))
mesh.dxf.blend_crease = 1
mesh.dxf.subdivision_levels = 3


# The bigger the crease value the more the edge will be protected from
# subdivision.
crease = 3.0

with mesh.edit_data() as mesh_data:
    mesh_data.vertices = cube_vertices
    mesh_data.faces = cube_faces

    mesh_data.add_edge_crease(0, 1, crease)
    mesh_data.add_edge_crease(1, 2, crease)
    mesh_data.add_edge_crease(2, 3, crease)
    mesh_data.add_edge_crease(3, 0, crease)

doc.saveas(CWD / f"cube_mesh_crease_value_{int(crease)}.dxf")
