# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
from pathlib import Path
import subprocess
from uuid import uuid4
import tempfile

import ezdxf
from ezdxf.render import forms
from ezdxf.render import MeshBuilder, MeshTransformer
from ezdxf.addons import MengerSponge, meshex

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

OPENSCAD = r"C:\Program Files\OpenSCAD\openscad.exe"
DXF_FILE = str(DIR / "OpenSCAD.dxf")

# This example shows the usage of the 'meshex' add-on to export/import meshes
# to/from OpenSCAD.

# IMPORTANT:
# OpenSCAD expects clockwise ordered face-vertices to create outward pointing
# normals, unlike any other application working with meshes which use
# counter-clockwise ordered vertices to create outward pointing normals.


def call_openscad(
    mesh1: MeshBuilder, mesh2: MeshBuilder, cmd="difference", prg=OPENSCAD
) -> MeshTransformer:
    """Executes the boolean operation `cmd` for the given meshes by OpenSCAD."""
    workdir = Path(tempfile.gettempdir())
    uuid = str(uuid4())
    off_path = workdir / f"ezdxf_{uuid}.off"
    scad_path = workdir / f"ezdxf_{uuid}.scad"
    s1 = meshex.scad_dumps(mesh1)  # returns a polyhedron definition as string
    s2 = meshex.scad_dumps(mesh2)  # returns a polyhedron definition as string

    scad_path.write_text(f"{cmd}(){{\n{s1}\n{s2}}}\n")
    subprocess.call(
        [
            prg,
            "--quiet",
            "--export-format",
            "off",  # The OFF format is more compact than the default STL format
            "-o",
            str(off_path),
            str(scad_path),
        ]
    )
    # Remove the OpenSCAD temp file:
    scad_path.unlink(missing_ok=True)

    new_mesh = MeshTransformer()
    # Import the OpenSCAD result from OFF file:
    if off_path.exists():
        new_mesh = meshex.off_loads(off_path.read_text())

    # Remove the OFF temp file:
    off_path.unlink(missing_ok=True)
    return new_mesh


def main(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()

    sponge = MengerSponge(level=3).mesh()
    sponge.flip_normals()  # important for OpenSCAD
    sphere = forms.sphere(
        count=32, stacks=16, radius=0.5, quads=True
    ).translate(0.25, 0.25, 1)
    sphere.flip_normals()  # important for OpenSCAD

    result = call_openscad(sponge, sphere, cmd="difference")
    print("Result has:")
    print(f"{len(result.vertices)} vertices")
    print(f"{len(result.faces)} faces")
    result.render_mesh(msp)

    # The exported mesh from OpenSCAD has outward pointing normals, so flipping
    # normals is not necessary!
    result.render_normals(msp, length=0.1, dxfattribs={"color": 3})

    doc.set_modelspace_vport(6, center=(5, 0))
    doc.saveas(filename)
    print(f"exported DXF file: '{filename}'")


if __name__ == "__main__":
    main(DXF_FILE)
