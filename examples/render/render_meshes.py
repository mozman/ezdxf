# Copyright (c) 2018-2022, Manfred Moitzi
# License: MIT License
import math
import pathlib
import ezdxf
from ezdxf.render import forms, MeshBuilder
from itertools import cycle

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create 3D forms.
#
# docs:
# forms: https://ezdxf.mozman.at/docs/render/forms.html
# MeshBuilder: https://ezdxf.mozman.at/docs/render/mesh.html
# ------------------------------------------------------------------------------


def write_mesh(filename, mesh: MeshBuilder):
    """Write MeshBuilder object as a MESH entity."""
    doc = ezdxf.new("R2000")
    # MESH can represent ngons, no tessellation is applied:
    mesh.render_mesh(doc.modelspace())
    try:
        doc.saveas(filename)
    except IOError as e:
        print(str(e))
    else:
        print(f'saving as "{filename}" MESH: done')


def write_polyface(filename, mesh: MeshBuilder):
    """Write MeshBuilder object as a POLYFACE entity a subtype of POLYLINE."""
    doc = ezdxf.new("R2000")
    # POLYFACE can only represent triangles or quads, the required
    # tessellation of the mesh is done automatically:
    mesh.render_polyface(doc.modelspace())
    try:
        doc.saveas(filename)
    except IOError as e:
        print(str(e))
    else:
        print(f'saving as "{filename}" POLYFACE: done')


def write_3dfaces(filename, mesh: MeshBuilder):
    """Write MeshBuilder object as single 3DFACE entities."""
    doc = ezdxf.new("R2000")
    # 3DFACE can only represent triangles or quads, the required
    # tessellation of the mesh is done automatically:
    mesh.render_3dfaces(doc.modelspace())
    try:
        doc.saveas(filename)
    except IOError as e:
        print(str(e))
    else:
        print(f'saving as "{filename}" 3DFACES: done')


def build_rotation_form(alpha=2 * math.pi, sides=16):
    profile = forms.spline_interpolation(
        [(0, 0.1), (1, 1), (3, 1.5), (5, 3)], subdivide=8
    )  # in xy-plane
    return forms.rotation_form(sides, profile, angle=alpha, axis=(1, 0, 0))


def create_gear(
    filename, teeth=20, outside_radius=10, top_width=2, bottom_width=3, height=2
):
    doc = ezdxf.new("R2000")
    msp = doc.modelspace()
    vertices = zip(
        forms.gear(
            count=teeth,
            top_width=top_width,
            bottom_width=bottom_width,
            height=height,
            outside_radius=outside_radius,
        ),
        cycle(
            [0, 0.1, 0, 0.1]
        ),  # bulge values: top, down flank,  bottom, up flank
    )
    msp.add_lwpolyline(
        vertices,
        format="vb",
        close=True,
    )
    doc.saveas(filename)


def main():
    cylinder = forms.cylinder(16)
    write_mesh(CWD / "cylinder_mesh.dxf", cylinder)
    write_polyface(CWD / "cylinder_polyface.dxf", cylinder)
    write_3dfaces(CWD / "cylinder_3dfaces.dxf", cylinder)
    rotation_form = build_rotation_form(sides=32)
    write_mesh(CWD / "rotated_profile_mesh.dxf", rotation_form)
    write_polyface(CWD / "rotated_profile_polyface.dxf", rotation_form)
    write_3dfaces(CWD / "rotated_profile_3dfaces.dxf", rotation_form)
    create_gear(CWD / "gear.dxf")


if __name__ == "__main__":
    main()
