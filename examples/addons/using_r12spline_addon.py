# Purpose: examples for using R12Spline() add-on
# Created: 01.03.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from ezdxf.addons import R12Spline
from ezdxf.algebra import Vector, Matrix44

next_frame = Matrix44.translate(0, 7, 0)

NAME = 'r12spline.dxf'
SEGMENTS = 40
dwg = ezdxf.new('R12')
msp = dwg.modelspace()


def draw(points):
    for point in points:
        msp.add_circle(radius=0.1, center=point, dxfattribs={'color': 1})


spline_points = [Vector(p) for p in [(8.55, 2.96), (8.55, -.03), (2.75, -.03), (2.76, 3.05), (4.29, 1.78), (6.79, 3.05)]]

# open quadratic b-spline
draw(spline_points)
msp.add_text("Open Quadratic R12Spline", dxfattribs={'height': .1}).set_pos(spline_points[0])
R12Spline(spline_points, degree=2, closed=False).render(msp, segments=SEGMENTS, dxfattribs={'color': 3})
if dwg.dxfversion > 'AC1009':
    msp.add_open_spline(control_points=spline_points, degree=2, dxfattribs={'color': 4})

# open cubic b-spline
spline_points = next_frame.transform_vectors(spline_points)
draw(spline_points)
msp.add_text("Open Cubic R12Spline", dxfattribs={'height': .1}).set_pos(spline_points[0])
R12Spline(spline_points, degree=3, closed=False).render(msp, segments=SEGMENTS, dxfattribs={'color': 3})
if dwg.dxfversion > 'AC1009':
    msp.add_open_spline(control_points=spline_points, degree=3, dxfattribs={'color': 4})

# closed cubic b-spline
spline_points = next_frame.transform_vectors(spline_points)
draw(spline_points)
msp.add_text("Closed Cubic R12Spline", dxfattribs={'height': .1}).set_pos(spline_points[0])
R12Spline(spline_points, degree=3, closed=True).render(msp, segments=SEGMENTS, dxfattribs={'color': 3})
if dwg.dxfversion > 'AC1009':
    msp.add_closed_spline(control_points=spline_points, degree=3, dxfattribs={'color': 4})

dwg.saveas(NAME)
print("drawing '%s' created.\n" % NAME)
