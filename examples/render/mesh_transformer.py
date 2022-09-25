# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf import colors
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.render import forms

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use MeshTransformer class.
# ------------------------------------------------------------------------------


def main():
    # cube and cylinder are MeshTransformer instances:
    cube = forms.cube().scale_uniform(10).subdivide(2)
    cylinder = forms.cylinder(12, radius=5, top_center=(0, 0, 10)).translate(
        0, 20
    )

    doc = ezdxf.new()
    msp = doc.modelspace()

    red = GfxAttribs(color=colors.RED)
    green = GfxAttribs(color=colors.GREEN)
    blue = GfxAttribs(color=colors.BLUE)

    # render the cube as MESH entity:
    cube.render_mesh(msp, dxfattribs=red)

    # translate the cube:
    cube.translate(20)

    # render the cube as POLYFACE entity, a POLYLINE entity in reality:
    cube.render_polyface(msp, dxfattribs=green)

    # translate the cube:
    cube.translate(20)

    # render the cube as 3DFACE entities:
    cube.render_3dfaces(msp, dxfattribs=blue)

    # render the cylinder as MESH entity:
    cylinder.render_mesh(msp, dxfattribs=red)

    # translate the cylinder:
    cylinder.translate(20)

    # render the cylinder as POLYFACE entity, a POLYLINE entity in reality:
    cylinder.render_polyface(msp, dxfattribs=green)

    # translate the cylinder:
    cylinder.translate(20)

    # render the cube as 3DFACE entities:
    cylinder.render_3dfaces(msp, dxfattribs=blue)

    doc.set_modelspace_vport(30, center=(30, 20))
    doc.saveas(CWD / "meshes.dxf")


if __name__ == "__main__":
    main()
