# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.render.forms import sphere

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to render a 3D sphere as MESH entity. The added
# face-normals show if the face-orientation follows the usual count-clockwise
# order to build outside pointing faces.
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new()
    doc.layers.new("mesh", dxfattribs={"color": 5})
    doc.layers.new("normals", dxfattribs={"color": 6})

    doc.set_modelspace_vport(6, center=(5, 0))
    msp = doc.modelspace()

    sphere1 = sphere(count=32, stacks=16, radius=1, quads=True)

    sphere1.render_mesh(msp, dxfattribs={"layer": "mesh"})
    sphere1.render_normals(msp, dxfattribs={"layer": "normals"})

    doc.saveas(CWD / "sphere.dxf")


if __name__ == "__main__":
    main()
