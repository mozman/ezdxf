# Copyright (C) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from ezdxf.addons import forms


def write_mesh(filename, mesh):
    dwg = ezdxf.new('R2000')
    mesh.render(dwg.modelspace())
    dwg.saveas(filename)


def build_cylinder(filename, sides=16):
    cylinder = forms.cylinder(sides)
    try:
        write_mesh(filename, cylinder)
    except IOError as e:
        print('ERROR: can not write "{0}": {1}'.format(e.filename, e.strerror))
    else:
        print('saving cylinder as "{}": done'.format(filename))


if __name__ == '__main__':
    build_cylinder("cylinder_16.dxf", sides=16)
