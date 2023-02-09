# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.render.forms import sphere, cube
from ezdxf.addons.pycsg import CSG

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use the pycsg add-on (Constructive Solid Geometry).
#
# docs: https://ezdxf.mozman.at/docs/addons/pycsg.html
# ------------------------------------------------------------------------------

NLENGTH = 0.05


def main():
    doc = ezdxf.new()
    doc.layers.new("csg", dxfattribs={"color": 1})
    doc.layers.new("normals", dxfattribs={"color": 6})

    doc.set_modelspace_vport(6, center=(5, 0))
    msp = doc.modelspace()

    cube1 = cube().translate(-0.5, -0.5, -0.5)
    sphere1 = sphere(count=32, stacks=16, radius=0.5, quads=True)

    union = (CSG(cube1) + CSG(sphere1)).mesh()
    union.render_mesh(msp, dxfattribs={"layer": "csg", "color": 1})
    union.render_normals(
        msp, length=NLENGTH, relative=False, dxfattribs={"layer": "normals"}
    )

    subtract = (CSG(cube1) - CSG(sphere1)).mesh().translate(2.5)
    subtract.render_mesh(msp, dxfattribs={"layer": "csg", "color": 3})
    subtract.render_normals(
        msp, length=NLENGTH, relative=False, dxfattribs={"layer": "normals"}
    )

    intersection = (CSG(cube1) * CSG(sphere1)).mesh().translate(4)
    intersection.render_mesh(msp, dxfattribs={"layer": "csg", "color": 5})
    intersection.render_normals(
        msp, length=NLENGTH, relative=False, dxfattribs={"layer": "normals"}
    )

    doc.saveas(CWD / "csg_sphere.dxf")


if __name__ == "__main__":
    main()
