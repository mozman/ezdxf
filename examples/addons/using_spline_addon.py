# Purpose: examples for using Spline() addon
# Created: 09.02.2010, 2018 adapted for ezdxf
# Copyright (C) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from ezdxf.addons import Spline

NAME = 'spline.dxf'
dwg = ezdxf.new('R12')
msp = dwg.modelspace()

spline_points = [(0.0, 0.0), (2., 2.), (3., 2.), (5., 0.)]
Spline(spline_points, color=7).render(msp)

for point in spline_points:
    msp.add_circle(radius=0.1, center=point, dxfattribs={'color': 1})

dwg.saveas(NAME)
print("drawing '%s' created.\n" % NAME)
