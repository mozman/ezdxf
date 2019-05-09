# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import math
import ezdxf
from ezdxf.render import forms


def write_mesh(filename, mesh):
    doc = ezdxf.new('R2000')
    mesh.render(doc.modelspace())
    try:
        doc.saveas(filename)
    except IOError as e:
        print('ERROR: can not write "{0}": {1}'.format(e.filename, e.strerror))
    else:
        print('saving cylinder as "{}": done'.format(filename))


def build_rotation_form(filename, alpha=2*math.pi, sides=16):
    profile = forms.spline_interpolation([(0, 0.1), (1, 1), (3, 1.5), (5, 3)], subdivide=8)  # in xy-plane
    mesh = forms.rotation_form(sides, profile, angle=alpha, axis=(1, 0, 0))
    write_mesh(filename, mesh)


def build_cylinder(filename, sides=16):
    cylinder = forms.cylinder(sides)
    write_mesh(filename, cylinder)


def create_gear(filename, teeth=20, outside_radius=10, width=3, height=2):
    doc = ezdxf.new('R2000')
    msp = doc.modelspace()
    msp.add_lwpolyline(forms.gear(count=teeth, width=width, height=height, radius=outside_radius), dxfattribs={'closed': True})
    doc.saveas(filename)


if __name__ == '__main__':
    build_cylinder("forms_cylinder_16.dxf", sides=16)
    build_rotation_form("forms_rotate_profile_32.dxf", sides=32)
    create_gear('gear.dxf')