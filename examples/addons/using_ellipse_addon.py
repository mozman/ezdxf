# Purpose: examples for using Ellipse() add-on
# Created: 09.02.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from ezdxf.addons import Ellipse

NAME = 'ellipse.dxf'
dwg = ezdxf.new('R12')
msp = dwg.modelspace()


def render(ellipse):
    ellipse.render(msp)


for axis in [0.5, 0.75, 1., 1.5,  2., 3.]:
    render(Ellipse((0, 0), 5., axis, segments=200))

attribs = {
    'color': 1,
    'linetype': 'DASHDOT',
}

msp.add_line((-7, 0), (+7, 0), dxfattribs=attribs)
msp.add_line((0, -5), (0, +5), dxfattribs=attribs)

for rotation in [0, 30, 45, 60, 90]:
    render(Ellipse((20,0), 5., 2., rotation=rotation, segments=100))

for startangle in [0, 30, 45, 60, 90]:
    render(Ellipse((40, 0), 5., 2., startangle=startangle, endangle=startangle+90, rotation=startangle, segments=90))
    render(Ellipse((40, 0), 5., 2., startangle=startangle+180, endangle=startangle+270, rotation=startangle, segments=90))

dwg.saveas(NAME)
print("drawing '%s' created.\n" % NAME)
