# Purpose: examples for using Clothoid() add-on
# Created: 09.02.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from ezdxf.addons import Clothoid


def four_c(A, length, rotation):
    render(Clothoid(start=(2, 2), length=length, paramA=A, rotation=rotation), dxfattribs={'color': 1})
    render(Clothoid(start=(2, 2), mirror='x', length=length, paramA=A, rotation=rotation), dxfattribs={'color': 2})
    render(Clothoid(start=(2, 2), mirror='y', length=length, paramA=A, rotation=rotation), dxfattribs={'color': 3})
    render(Clothoid(start=(2, 2), mirror='xy', length=length, paramA=A, rotation=rotation), dxfattribs={'color': 4})


def render(clothoid, dxfattribs):
    clothoid.render(msp, segments=100, dxfattribs=dxfattribs)
    clothoid.render_spline(msp, segments=10, dxfattribs={'color': 6, 'linetype': "DASHED"})


NAME = 'clothoid.dxf'
dwg = ezdxf.new('R2000')
msp = dwg.modelspace()

msp.add_line((-20, 0), (20, 0), dxfattribs={'linetype': "PHANTOM"})
msp.add_line((0, -20), (0, 20), dxfattribs={'linetype': "PHANTOM"})
for rotation in [0, 30, 45, 60, 75, 90]:
    four_c(10., 25, rotation)

if dwg.validate(print_report=True):
    dwg.saveas(NAME)
    print("drawing '%s' created.\n" % NAME)
