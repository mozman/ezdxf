# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
from pathlib import Path

import ezdxf
from ezdxf.render import forms
from ezdxf.addons import MengerSponge, openscad

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


def main(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()

    sponge = MengerSponge(level=3).mesh()
    sponge.flip_normals()  # important for OpenSCAD
    sphere = forms.sphere(
        count=32, stacks=16, radius=0.5, quads=True
    ).translate(0.25, 0.25, 1)
    sphere.flip_normals()  # important for OpenSCAD

    script = openscad.boolean_operation(openscad.DIFFERENCE, sponge, sphere)
    result = openscad.run(script)
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
