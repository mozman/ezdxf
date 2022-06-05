# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
from pathlib import Path
import subprocess
import ezdxf
import os

from ezdxf.render.forms import sphere
from ezdxf.render import MeshBuilder, MeshTransformer
from ezdxf.addons import MengerSponge, meshex

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

OPENSCAD = r"C:\Program Files\OpenSCAD\openscad.exe"
DXF_FILE = str(DIR / "OpenSCAD.dxf")

# This example shows the usage of the ezdxf.addons.meshex add-on to
# export/import meshes to/from OpenSCAD.

# IMPORTANT:
# OpenSCAD expects clockwise ordered face-vertices to create outward pointing
# normals, unlike any other application working with meshes which use
# counter-clockwise ordered vertices to create outward pointing normals.


def difference(
    mesh1: MeshBuilder, mesh2: MeshBuilder, cmd=OPENSCAD
) -> MeshTransformer:
    """Executes the boolean operation `mesh1` - `mesh2` by OpenSCAD."""
    off_filename = "ezdxf_temp.off"
    openscad_filename = "ezdxf_temp.scad"
    s1 = meshex.scad_dumps(mesh1)  # returns a polyhedron definition as string
    s2 = meshex.scad_dumps(mesh2)  # returns a polyhedron definition as string

    # Write the OpenSCAD script:
    with open(openscad_filename, "wt") as fp:
        fp.write(f"difference(){{\n{s1}\n{s2}}}\n")
    subprocess.call(
        [
            cmd,
            "--export-format",
            "off",  # The OFF format is more compact than the default STL format
            "-o",
            off_filename,
            openscad_filename,
        ]
    )
    # Remove the OpenSCAD temp file:
    if os.path.exists(openscad_filename):
        os.unlink(openscad_filename)

    new_mesh = MeshTransformer()
    # Import the OpenSCAD result from OFF file:
    if os.path.exists(off_filename):
        with open(off_filename, "rt") as fp:
            new_mesh = meshex.off_loads(fp.read())
        # Remove the OFF temp file:
        os.unlink(off_filename)
    return new_mesh


doc = ezdxf.new()
msp = doc.modelspace()


sponge = MengerSponge(level=3).mesh()
sponge.flip_normals()  # important for OpenSCAD
sphere = sphere(count=32, stacks=16, radius=0.5, quads=True).translate(
    0.25, 0.25, 1
)
sphere.flip_normals()  # important for OpenSCAD

result = difference(sponge, sphere)
print("Result has:")
print(f"{len(result.vertices)} vertices")
print(f"{len(result.faces)} faces")
result.render_mesh(msp)

# The exported mesh from OpenSCAD has outward pointing normals, so flipping
# normals is not necessary!
result.render_normals(msp, length=0.1, dxfattribs={"color": 3})

doc.set_modelspace_vport(6, center=(5, 0))
doc.saveas(DXF_FILE)
print(f"exported DXF file:{DXF_FILE}")
