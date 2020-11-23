# Created: 09.02.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2019, Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.render import Spline
from ezdxf.math import Vec3, Matrix44


next_frame = Matrix44.translate(0, 5, 0)
right_frame = Matrix44.translate(10, 0, 0)

NAME = 'spline.dxf'
doc = ezdxf.new('R2000')
msp = doc.modelspace()


def draw(points):
    for point in points:
        msp.add_circle(radius=0.1, center=point, dxfattribs={'color': 1})


spline_points = Vec3.list([(1., 1.), (2.5, 3.), (4.5, 2.), (6.5, 4.)])

# fit points
draw(spline_points)
Spline(spline_points).render_as_fit_points(msp, method='distance', dxfattribs={'color': 2})  # curve with definition points as fit points
Spline(spline_points).render_as_fit_points(msp, method='uniform', dxfattribs={'color': 3})
Spline(spline_points).render_as_fit_points(msp, method='centripetal', dxfattribs={'color': 4})  # distance ^ 1/2
Spline(spline_points).render_as_fit_points(msp, method='centripetal', power=1./3., dxfattribs={'color': 6})  # distance ^ 1/3

msp.add_spline(fit_points=spline_points, dxfattribs={'color': 1})
msp.add_text("Spline.render_as_fit_points() differs from AutoCAD fit point rendering", dxfattribs={'height': .1}).set_pos(spline_points[0])

# open uniform b-spline
spline_points = list(next_frame.transform_vertices(spline_points))
draw(spline_points)
msp.add_text("Spline.render_open_bspline() matches AutoCAD", dxfattribs={'height': .1}).set_pos(spline_points[0])
Spline(spline_points).render_open_bspline(msp, degree=3, dxfattribs={'color': 3})  # B-spline defined by control points, open uniform knots
msp.add_open_spline(control_points=spline_points, degree=3, dxfattribs={'color': 4})

rbspline_points = list(right_frame.transform_vertices(spline_points))

# uniform b-spline
spline_points = list(next_frame.transform_vertices(spline_points))
draw(spline_points)
msp.add_text("Spline.render_uniform_bspline() matches AutoCAD", dxfattribs={'height': .1}).set_pos(spline_points[0])
Spline(spline_points).render_uniform_bspline(msp, degree=3, dxfattribs={'color': 3})  # B-spline defined by control points, uniform knots
spline = msp.add_spline(dxfattribs={'color': 4})
spline.set_uniform(control_points=spline_points, degree=3)  # has no factory method

# closed b-spline
spline_points = list(next_frame.transform_vertices(spline_points))
draw(spline_points)
Spline(spline_points).render_closed_bspline(msp, degree=3, dxfattribs={'color': 3})
msp.add_closed_spline(spline_points, degree=3)
msp.add_text("Spline.render_closed_bspline() matches 'periodic closed' AutoCAD", dxfattribs={'height': .1}).set_pos(spline_points[0])

# rational open uniform b-spline
spline_points = rbspline_points
weights = [1, 50, 50, 1]
draw(spline_points)
Spline(spline_points).render_open_rbspline(msp, weights=weights, degree=3, dxfattribs={'color': 3})  # Rational B-spline defined by control points, open uniform knots
msp.add_rational_spline(control_points=spline_points, weights=weights, degree=3, dxfattribs={'color': 4})
msp.add_text("Spline.render_open_rbspline() matches AutoCAD", dxfattribs={'height': .1}).set_pos(spline_points[0])

# rational closed b-spline
spline_points = list(next_frame.transform_vertices(spline_points))
weights = [5, 25, 25, 5]
draw(spline_points)
Spline(spline_points).render_closed_rbspline(msp, weights=weights, degree=3, dxfattribs={'color': 3})  # closed Rational B-spline defined by control points, uniform knots
msp.add_closed_rational_spline(control_points=spline_points, weights=weights, degree=3, dxfattribs={'color': 4})
msp.add_text("Spline.render_closed_rbspline() matches 'periodic closed' AutoCAD", dxfattribs={'height': .1}).set_pos(spline_points[0])

doc.saveas(NAME)
print("drawing '%s' created.\n" % NAME)
