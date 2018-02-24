# Purpose: examples for using Spline() add-on
# Created: 09.02.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf
from ezdxf.addons import Spline
from ezdxf.algebra import Vector, Matrix44

next_frame = Matrix44.translate(0, 5, 0)
right_frame = Matrix44.translate(10, 0, 0)

NAME = 'spline.dxf'
dwg = ezdxf.new('R2000')
msp = dwg.modelspace()


def draw(points):
    for point in points:
        msp.add_circle(radius=0.1, center=point, dxfattribs={'color': 1})


spline_points = [Vector(p) for p in [(1., 1.), (2.5, 3.), (4.5, 2.), (6.5, 4.)]]

# fit points
draw(spline_points)
Spline(spline_points, color=3).render_as_fit_points(msp, method='distance')  # curve with definition points as fit points
Spline(spline_points, color=2).render_as_fit_points(msp, method='uniform')
spline = msp.add_spline(fit_points=spline_points, dxfattribs={'color': 4})
msp.add_text("Spline.render_as_fit_points() differs from AutoCAD fit point rendering", dxfattribs={'height': .1}).set_pos(spline_points[0])

# open uniform b-spline
spline_points = next_frame.transform_vectors(spline_points)
draw(spline_points)
msp.add_text("Spline.render_open_bspline() matches AutoCAD", dxfattribs={'height': .1}).set_pos(spline_points[0])
Spline(spline_points, color=3).render_open_bspline(msp, degree=3)  # B-spline defined by control points, open uniform knots
msp.add_open_spline(control_points=spline_points, degree=3, dxfattribs={'color': 4})

rbspline_points = right_frame.transform_vectors(spline_points)

# uniform b-spline
spline_points = next_frame.transform_vectors(spline_points)
draw(spline_points)
msp.add_text("Spline.render_uniform_bspline() matches AutoCAD", dxfattribs={'height': .1}).set_pos(spline_points[0])
Spline(spline_points, color=3).render_uniform_bspline(msp, degree=3)  # B-spline defined by control points, uniform knots
msp.add_uniform_spline(control_points=spline_points, degree=3, dxfattribs={'color': 4})

# closed b-spline
spline_points = next_frame.transform_vectors(spline_points)
draw(spline_points)
Spline(spline_points, color=3).render_closed_bspline(msp, degree=3)
msp.add_closed_spline(spline_points, degree=3)
msp.add_text("Spline.render_closed_bspline() matches AutoCAD", dxfattribs={'height': .1}).set_pos(spline_points[0])

# rational open uniform b-spline
spline_points = rbspline_points
weights = [1, 50, 50, 1]
draw(spline_points)
msp.add_text("Spline.render_open_rbspline() matches AutoCAD", dxfattribs={'height': .1}).set_pos(spline_points[0])
Spline(spline_points, color=3).render_open_rbspline(msp, weights=weights, degree=3)  # Rational B-spline defined by control points, open uniform knots
msp.add_rational_spline(control_points=spline_points, weights=weights, degree=3, dxfattribs={'color': 4})

# rational closed b-spline
spline_points = next_frame.transform_vectors(spline_points)
weights = [5, 25, 25, 5]
draw(spline_points)
msp.add_text("Spline.render_closed_rbspline() not supported by AutoCAD", dxfattribs={'height': .1}).set_pos(spline_points[0])
Spline(spline_points, color=3).render_closed_rbspline(msp, weights=weights, degree=3)  # closed Rational B-spline defined by control points, uniform knots


dwg.saveas(NAME)
print("drawing '%s' created.\n" % NAME)
