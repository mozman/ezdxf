# Purpose: using lwpolyline
# Created: 13.04.2014
# Copyright (c) 2014 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf


def tut_lwpolyline():
    dwg = ezdxf.new('AC1015')
    msp = dwg.modelspace()

    points = [(0, 0), (3, 0), (6, 3), (6, 6)]
    msp.add_lwpolyline(points)

    dwg.saveas("lwpolyline1.dxf")

    # Append points to a polyline::

    dwg = ezdxf.readfile("lwpolyline1.dxf")
    msp = dwg.modelspace()

    line = msp.query('LWPOLYLINE')[0]  # take first LWPolyline
    line.append_points([(8, 7), (10, 7)])

    dwg.saveas("lwpolyline2.dxf")

    # Use context manager to edit polyline::

    dwg = ezdxf.readfile("lwpolyline2.dxf")
    msp = dwg.modelspace()

    line = msp.query('LWPOLYLINE')[0]  # take first LWPolyline

    with line.points() as points:  # points is a python standard list
        # del points[-2:]  # delete last 2 points
        # points.extend([(4, 7), (0, 7)])  # adding 2 other points
        # the same as one command
        points[-2:] = [(4, 7), (0, 7)]
    # implicit call of line.set_points(points) at context manager exit

    dwg.saveas("lwpolyline3.dxf")

    # Each line segment can have a different start/end width, if omitted start/end width = 0::

    dwg = ezdxf.new('AC1015')
    msp = dwg.modelspace()

    # point format = (x, y, [start_width, [end_width, [bulge]]])

    points = [(0, 0, .1, .15), (3, 0, .5, .75), (6, 3, .3, .35), (6, 6, .4, .45)]
    msp.add_lwpolyline(points)

    dwg.saveas("lwpolyline4.dxf")

    # LWPolyline can also have curved elements, they are defined by the bulge value::

    dwg = ezdxf.new('AC1015')
    msp = dwg.modelspace()

    # point format = (x, y, [start_width, [end_width, [bulge]]])

    points = [(0, 0, 0, .05), (3, 0, .1, .2, -.5), (6, 0, .1, .05), (9, 0)]
    msp.add_lwpolyline(points)

    dwg.saveas("lwpolyline5.dxf")


tut_lwpolyline()
