# Purpose: examples for using Clothoid() add-on
# Created: 09.02.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from ezdxf.addons import Clothoid


def four_c(A, length, rotation):
    render(Clothoid(start=(2, 2), length=length, paramA=A, rotation=rotation, color=1))
    render(Clothoid(start=(2, 2), mirror='x', length=length, paramA=A, rotation=rotation, color=2))
    render(Clothoid(start=(2, 2), mirror='y', length=length, paramA=A, rotation=rotation, color=3))
    render(Clothoid(start=(2, 2), mirror='xy', length=length, paramA=A, rotation=rotation, color=4))


def render(clothoid):
    clothoid.render(msp)


NAME = 'clothoid.dxf'
dwg = ezdxf.new('R12')
msp = dwg.modelspace()

msp.add_line((-20,0), (20, 0), dxfattribs={'linetype': "DASHDOT2"})
msp.add_line((0, -20), (0, 20), dxfattribs={'linetype': "DASHDOT"})
for rotation in [0, 30, 45, 60, 75, 90]:
    four_c(10., 25, rotation)
dwg.saveas(NAME)
print("drawing '%s' created.\n" % NAME)
