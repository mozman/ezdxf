#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib

import ezdxf
from ezdxf.render import forms
from ezdxf import path

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how sweep a profile along a helix to create a MESH entity.
# ------------------------------------------------------------------------------


def make_bspline_tool(helix: path.Path):
    return next(path.to_bsplines_and_vertices(helix))


def main(filepath):
    doc = ezdxf.new()
    doc.layers.add("MESH", color=ezdxf.colors.YELLOW)
    doc.layers.add("SPLINE", color=ezdxf.colors.MAGENTA)
    msp = doc.modelspace()
    # sweeping a gear-profile
    gear = forms.gear(
        8, top_width=0.01, bottom_width=0.02, height=0.01, outside_radius=0.1
    )
    helix = path.helix(radius=2, pitch=1, turns=6)
    # along a helix spine
    sweeping_path = helix.flattening(0.1)
    mesh = forms.sweep(gear, sweeping_path, close=True, caps=True)
    # and render a mesh
    mesh.render_mesh(msp, dxfattribs={"layer": "MESH"})
    # add helix as SPLINE entity:
    spline = msp.add_spline(dxfattribs={"layer": "SPLINE"})
    tool = make_bspline_tool(helix)
    spline.apply_construction_tool(tool)
    # Enter the "REGEN" command in your CAD application if the SPLINE entity
    # is very "edgy".

    doc.saveas(filepath)


if __name__ == "__main__":
    main(CWD / "sweep_helix.dxf")
