# Purpose: using splines
# Created: 13.04.2014
# Copyright (c) 2014 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf


def clone_spline():
    dwg = ezdxf.readfile("Spline_R2000.dxf")
    msp = dwg.modelspace()
    spline = msp.query('SPLINE')[0]  # take first spline
    # delete the existing spline from model space and drawing database
    msp.delete_entity(spline)
    # add a new spline
    msp.add_spline(spline.get_fit_points())
    dwg.saveas("clone_Spline.dxf")


def fit_spline():
    dwg = ezdxf.new('AC1015')
    fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
    msp = dwg.modelspace()
    spline = msp.add_spline(fit_points)
    spline.dxf.start_tangent = (1, 0, 0)
    spline.dxf.end_tangent = (0, 1, 0)
    dwg.saveas("fit_spline.dxf")


def fit_spline_with_control_points():
    dwg = ezdxf.new('AC1015')
    fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
    control_points = [(0, 0, 0), (1250, 1560, 0), (3130, 610, 0), (2250, 1250, 0)]
    msp = dwg.modelspace()
    spline = msp.add_spline(fit_points)
    spline.set_control_points(control_points)
    dwg.saveas("fit_spline_and_control_points.dxf")


def add_points_to_spline():
    dwg = ezdxf.readfile("Spline_R2000.dxf")
    msp = dwg.modelspace()
    spline = msp.query('SPLINE')[0]  # take first spline
    with spline.fit_points() as fp:
        fp.append((800, 150, 0))

    # As far I tested this works without complaints from AutoCAD, but for the case of problems
    spline.set_knot_values([])  # delete knot values, this shouldn't modify the geometry of the spline
    spline.set_weights([])  # delete weights, this could modify the geometry of the spline
    spline.set_control_points([])  # delete control points, this could modify the geometry of the spline

    dwg.saveas("Spline_with_added_points.dxf")


if __name__ == '__main__':
    fit_spline()
