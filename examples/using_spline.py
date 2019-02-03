# Purpose: using splines
# Created: 13.04.2014
# Copyright (c) 2014 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.math.bspline import bspline_control_frame, bspline_control_frame_approx
from ezdxf.math import BSpline, Vector


def clone_spline():
    dwg = ezdxf.readfile("Spline_R2000_fit_spline.dxf")
    msp = dwg.modelspace()
    spline = msp.query('SPLINE')[0]  # take first spline
    # delete the existing spline from model space and drawing database
    msp.delete_entity(spline)
    # add a new spline
    msp.add_spline(spline.get_fit_points())
    dwg.saveas("Spline_R2000_clone_Spline.dxf")


def fit_spline():
    dwg = ezdxf.new('R2000')
    fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
    msp = dwg.modelspace()
    spline = msp.add_spline(fit_points)
    spline.dxf.start_tangent = (1, 0, 0)
    spline.dxf.end_tangent = (0, 1, 0)
    dwg.saveas("Spline_R2000_fit_spline.dxf")


def fit_spline_with_control_points():
    dwg = ezdxf.new('R2000')
    fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
    control_points = [(0, 0, 0), (1250, 1560, 0), (3130, 610, 0), (2250, 1250, 0)]
    msp = dwg.modelspace()
    spline = msp.add_spline(fit_points)
    spline.dxf.degree = 3
    spline.set_control_points(control_points)
    dwg.saveas("Spline_R2000_fit_spline_and_control_points.dxf")


def add_points_to_spline():
    dwg = ezdxf.readfile("Spline_R2000_fit_spline.dxf")
    msp = dwg.modelspace()
    spline = msp.query('SPLINE')[0]  # take first spline
    with spline.edit_data() as data:
        data.fit_points.append((3130, 610, 0))
        # As far I tested this works without complaints from AutoCAD, but for the case of problems
        data.control_points = []  # delete control points, this could modify the geometry of the spline
        data.knot_values = []  # delete knot values, this shouldn't modify the geometry of the spline
        data.weights = []  # delete weights, this could modify the geometry of the spline

    dwg.saveas("Spline_R2000_with_added_points.dxf")


def open_spline():
    dwg = ezdxf.new('R2000')
    control_points = [(0, 0, 0), (1250, 1560, 0), (3130, 610, 0), (2250, 1250, 0)]
    msp = dwg.modelspace()
    msp.add_open_spline(control_points, degree=3)
    dwg.saveas("Spline_R2000_open_spline.dxf")


def closed_spline():
    dwg = ezdxf.new('R2000')
    control_points = [(0, 0, 0), (1250, 1560, 0), (3130, 610, 0), (2250, 1250, 0)]
    msp = dwg.modelspace()
    msp.add_closed_spline(control_points, degree=3)
    dwg.saveas("Spline_R2000_closed_spline.dxf")


def rational_spline():
    dwg = ezdxf.new('R2000')
    control_points = [(0, 0, 0), (1250, 1560, 0), (3130, 610, 0), (2250, 1250, 0)]
    weights = [1, 10, 1, 1]
    msp = dwg.modelspace()
    msp.add_rational_spline(control_points, weights, degree=3)
    dwg.saveas("Spline_R2000_rational_spline.dxf")


def closed_rational_spline():
    dwg = ezdxf.new('R2000')
    control_points = [(0, 0, 0), (1250, 1560, 0), (3130, 610, 0), (2250, 1250, 0)]
    weights = [1, 10, 1, 1]
    msp = dwg.modelspace()
    msp.add_closed_rational_spline(control_points, weights, degree=3)
    dwg.saveas("Spline_R2000_closed_rational_spline.dxf")


def spline_control_frame_from_fit_points():
    dwg = ezdxf.new('R2000', setup=True)

    fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
    msp = dwg.modelspace()
    msp.add_polyline2d(fit_points, dxfattribs={'color': 2, 'linetype': 'DOT2'})

    def add_spline(degree=2, color=3):
        spline = bspline_control_frame(fit_points, degree=degree, method='distance')
        msp.add_polyline2d(spline.control_points, dxfattribs={'color': color, 'linetype': 'DASHED'})
        msp.add_open_spline(spline.control_points, degree=spline.degree, dxfattribs={'color': color})

    # add_spline(degree=2, color=3)
    add_spline(degree=3, color=4)

    msp.add_spline(fit_points, degree=3, dxfattribs={'color': 1})
    if dwg.validate():
        dwg.saveas("Spline_R2000_spline_control_frame_from_fit_points.dxf")


def spline_control_frame_approximation():
    dwg = ezdxf.new('R2000', setup=True)

    fit_points = Vector.list([(0, 0), (10, 20), (30, 10), (40, 10), (50, 0), (60, 20), (70, 50), (80, 70), (65, 75)])
    msp = dwg.modelspace()
    msp.add_polyline2d(fit_points, dxfattribs={'color': 2, 'linetype': 'DOT2'})

    spline = bspline_control_frame_approx(fit_points, count=7, degree=3, method='uniform')
    msp.add_polyline2d(spline.control_points, dxfattribs={'color': 3, 'linetype': 'DASHED'})
    msp.add_open_spline(spline.control_points, degree=spline.degree, dxfattribs={'color': 3})
    msp.add_spline(fit_points, degree=3, dxfattribs={'color': 1})
    if dwg.validate():
        dwg.saveas("Spline_R2000_spline_control_frame_approximation.dxf")


def spline_insert_knot():
    dwg = ezdxf.new('R2000', setup=True)
    msp = dwg.modelspace()

    def add_spline(control_points, color=3, knots=None):
        msp.add_polyline2d(control_points, dxfattribs={'color': color, 'linetype': 'DASHED'})
        msp.add_open_spline(control_points, degree=3, knots=knots, dxfattribs={'color': color})

    control_points = Vector.list([(0, 0), (10, 20), (30, 10), (40, 10), (50, 0), (60, 20), (70, 50), (80, 70)])
    add_spline(control_points, color=3, knots=None)

    bspline = BSpline(control_points, order=4)
    bspline.insert_knot(bspline.max_t/2)
    add_spline(bspline.control_points, color=4, knots=bspline.knot_values())

    if dwg.validate():
        dwg.saveas("Spline_R2000_spline_insert_knot.dxf")


if __name__ == '__main__':
    fit_spline()
    clone_spline()
    fit_spline_with_control_points()
    add_points_to_spline()
    open_spline()
    closed_spline()
    rational_spline()
    closed_rational_spline()
    spline_control_frame_from_fit_points()
    spline_control_frame_approximation()
    spline_insert_knot()
