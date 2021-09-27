# Copyright (c) 2018-2021, Manfred Moitzi
# License: MIT License
import math
from pathlib import Path
import ezdxf
from ezdxf.render import forms
from itertools import cycle

DIR = Path("~/desktop/Outbox").expanduser()


def write_mesh(filename, mesh):
    doc = ezdxf.new("R2000")
    mesh.render_mesh(doc.modelspace())
    try:
        doc.saveas(filename)
    except IOError as e:
        print('ERROR: can not write "{0}": {1}'.format(e.filename, e.strerror))
    else:
        print('saving cylinder as "{}": done'.format(filename))


def write_mesh_as_3dface(filename, mesh):
    doc = ezdxf.new("R2000")
    msp = doc.modelspace()
    for vertices in mesh.faces_as_vertices():
        msp.add_3dface(vertices)

    try:
        doc.saveas(filename)
    except IOError as e:
        print('ERROR: can not write "{0}": {1}'.format(e.filename, e.strerror))
    else:
        print('saving mesh as "{}": done'.format(filename))


def build_rotation_form(filename, alpha=2 * math.pi, sides=16):
    profile = forms.spline_interpolation(
        [(0, 0.1), (1, 1), (3, 1.5), (5, 3)], subdivide=8
    )  # in xy-plane
    mesh = forms.rotation_form(sides, profile, angle=alpha, axis=(1, 0, 0))
    # write_mesh(filename, mesh)
    write_mesh_as_3dface(filename, mesh)


def build_cylinder(filename, sides=16):
    cylinder = forms.cylinder(sides)
    write_mesh(filename, cylinder)


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


if __name__ == "__main__":
    build_cylinder(DIR / "forms_cylinder_16.dxf", sides=16)
    build_rotation_form(DIR / "forms_rotate_profile_32.dxf", sides=32)
    create_gear(DIR / "gear.dxf")
