# Purpose: examples for using EulerSpiral() add-on
# Created: 09.02.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from math import radians
import ezdxf
from ezdxf.render import EulerSpiral
from ezdxf.algebra import Matrix44


def four_c(curvature, length, rotation):
    spiral = EulerSpiral(curvature=curvature)
    render(spiral, length, tmatrix(2, 2, angle=rotation), dxfattribs={'color': 1})
    # scaling sx=-1 is mirror about y-axis
    render(spiral, length, tmatrix(2, 2, sx=-1, sy=1, angle=rotation), dxfattribs={'color': 2})
    # scaling sy=-1 is mirror about x-axis
    render(spiral, length, tmatrix(2, 2, sx=1, sy=-1, angle=rotation), dxfattribs={'color': 3})
    render(spiral, length, tmatrix(2, 2, sx=-1, sy=-1, angle=rotation), dxfattribs={'color': 4})


def render(spiral, length, matrix, dxfattribs):
    spiral.render_polyline(msp, length, segments=100, matrix=matrix, dxfattribs=dxfattribs)
    spiral.render_spline(msp, length, fit_points=10, matrix=matrix, dxfattribs={'color': 6, 'linetype': "DASHED"})


def tmatrix(dx, dy, sx=1, sy=1, angle=0):
    return Matrix44.chain(
        Matrix44.scale(sx=sx, sy=sy, sz=1),
        Matrix44.z_rotate(radians(angle)),
        Matrix44.translate(dx, dy, 0),
    )


NAME = 'euler_spiral.dxf'
dwg = ezdxf.new('R2000')
msp = dwg.modelspace()

msp.add_line((-20, 0), (20, 0), dxfattribs={'linetype': "PHANTOM"})
msp.add_line((0, -20), (0, 20), dxfattribs={'linetype': "PHANTOM"})
for rotation in [0, 30, 45, 60, 75, 90]:
    four_c(10., 25, rotation)

if dwg.validate(print_report=True):
    dwg.saveas(NAME)
    print("drawing '%s' created.\n" % NAME)
