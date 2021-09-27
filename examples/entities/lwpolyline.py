# Purpose: using lwpolyline
# Copyright (c) 2014-2021, Manfred Moitzi
# License: MIT License
import ezdxf


def tut_lwpolyline():
    doc = ezdxf.new("R2000")
    msp = doc.modelspace()

    points = [(0, 0), (3, 0), (6, 3), (6, 6)]
    msp.add_lwpolyline(points)

    doc.saveas("lwpolyline1.dxf")

    # Append points to a polyline::

    doc = ezdxf.readfile("lwpolyline1.dxf")
    msp = doc.modelspace()

    line = msp.query("LWPOLYLINE")[0]  # take first LWPolyline
    line.append_points([(8, 7), (10, 7)])

    doc.saveas("lwpolyline2.dxf")

    # Use context manager to edit polyline::

    doc = ezdxf.readfile("lwpolyline2.dxf")
    msp = doc.modelspace()

    line = msp.query("LWPOLYLINE")[0]  # take first LWPolyline

    with line.points() as points:  # points is a python standard list
        # del points[-2:]  # delete last 2 points
        # points.extend([(4, 7), (0, 7)])  # adding 2 other points
        # the same as one command
        points[-2:] = [(4, 7), (0, 7)]
    # implicit call of line.set_points(points) at context manager exit

    doc.saveas("lwpolyline3.dxf")

    # Each line segment can have a different start/end width, if omitted start/end width = 0::

    doc = ezdxf.new("AC1015")
    msp = doc.modelspace()

    # point format = (x, y, [start_width, [end_width, [bulge]]])

    points = [
        (0, 0, 0.1, 0.15),
        (3, 0, 0.5, 0.75),
        (6, 3, 0.3, 0.35),
        (6, 6, 0.4, 0.45),
    ]
    msp.add_lwpolyline(points)

    doc.saveas("lwpolyline4.dxf")

    # LWPolyline can also have curved elements, they are defined by the bulge value::

    doc = ezdxf.new("AC1015")
    msp = doc.modelspace()

    # point format = (x, y, [start_width, [end_width, [bulge]]])

    points = [
        (0, 0, 0, 0.05),
        (3, 0, 0.1, 0.2, -0.5),
        (6, 0, 0.1, 0.05),
        (9, 0),
    ]
    msp.add_lwpolyline(points)

    doc.saveas("lwpolyline5.dxf")


tut_lwpolyline()
