# Purpose: examples for using Bezier() add-ons
# Created: 09.02.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from algebra.vector import Vector
from ezdxf.addons import Bezier


def draw_control_point(point, tangent1, tangent2=(0, 0)):
    tp1 = Vector(point) + Vector(tangent1)
    tp2 = Vector(point) + Vector(tangent2)
    attribs = {
        'color': 1
    }
    msp.add_circle(radius=0.05, center=point, dxfattribs=attribs)
    attribs['color'] = 2
    msp.add_line(point, tp1, dxfattribs=attribs)
    msp.add_line(point, tp2, dxfattribs=attribs)


NAME = 'bezier.dxf'
dwg = ezdxf.new('R12')
msp = dwg.modelspace()

bezier = Bezier()

# define start point
bezier.start((2, 4, 1), tangent=(0, 2, 0))
draw_control_point((2, 4, 1), (0, 2, 0))

# append first point
bezier.append((6, 7, -3), tangent1=(-2, 0, 0), tangent2=(1, 2, 0))
draw_control_point((6, 7, -3), (-2, 0, 0), (1, 2, 0))

# tangent2 = -tangent1 = (+2, 0)
bezier.append((12, 5, 2), tangent1=(-2, 0, 0))
draw_control_point((12, 5, 2), (-2, 0, 0), (2, 0, 0))

# for last point tangent2 is meaningless
bezier.append((16, 9, 20), tangent1=(-0.5, -3, 0))
draw_control_point((16, 9, 20), (-0.5, -3, 0))

bezier.render(msp, dxfattribs={'color': 4})
dwg.saveas(NAME)
print("drawing '%s' created.\n" % NAME)
