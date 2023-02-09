# Copyright (c) 2014-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


# ------------------------------------------------------------------------------
# This example shows the usage of the LWPOLYLINE entity, which is the default
# 2D polyline entity (LW stands for LightWeight).
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/lwpolyline.html
# circular arc segments: https://ezdxf.mozman.at/docs/dxfentities/lwpolyline.html#bulge-value
# tutorial: https://ezdxf.mozman.at/docs/tutorials/lwpolyline.html
# ------------------------------------------------------------------------------


def create_lwpolyline():
    doc = ezdxf.new("R2000")
    msp = doc.modelspace()

    points = [(0, 0), (3, 0), (6, 3), (6, 6)]
    msp.add_lwpolyline(points)
    doc.saveas(CWD / "lwpolyline1.dxf")


def append_points_to_lwpolyline():
    doc = ezdxf.readfile(CWD / "lwpolyline1.dxf")
    msp = doc.modelspace()

    pline = msp.query("LWPOLYLINE").first
    pline.append_points([(8, 7), (10, 7)])
    doc.saveas(CWD / "lwpolyline2.dxf")


def edit_lwpolyline():
    doc = ezdxf.readfile(CWD / "lwpolyline2.dxf")
    msp = doc.modelspace()

    pline = msp.query("LWPOLYLINE").first
    # edit by context manager:
    with pline.points() as points:  # points is a python standard list
        # del points[-2:]  # delete last 2 points
        # points.extend([(4, 7), (0, 7)])  # adding 2 other points
        # the same as one command
        points[-2:] = [(4, 7), (0, 7)]
    # implicit call of line.set_points(points) at context manager exit
    doc.saveas(CWD / "lwpolyline3.dxf")


def lwpolyline_width():
    doc = ezdxf.new("AC1015")
    msp = doc.modelspace()

    # Each line segment can have a different start/end width, if omitted
    # start/end width = 0.
    # point format = (x, y, [start_width, [end_width, [bulge]]])
    points = [
        (0, 0, 0.1, 0.15),
        (3, 0, 0.5, 0.75),
        (6, 3, 0.3, 0.35),
        (6, 6, 0.4, 0.45),
    ]
    msp.add_lwpolyline(points)
    doc.saveas(CWD / "lwpolyline_width.dxf")


def lwpolyline_with_circular_arcs():
    doc = ezdxf.new("AC1015")
    msp = doc.modelspace()

    # LWPolyline can also have curved elements, they are defined by the bulge value.
    # point format = (x, y, [start_width, [end_width, [bulge]]])

    points = [
        (0, 0, 0, 0.05),
        (3, 0, 0.1, 0.2, -0.5),
        (6, 0, 0.1, 0.05),
        (9, 0),
    ]
    msp.add_lwpolyline(points)
    doc.saveas(CWD / "lwpolyline_bulge.dxf")


if __name__ == "__main__":
    create_lwpolyline()
    append_points_to_lwpolyline()
    edit_lwpolyline()
    lwpolyline_width()
    lwpolyline_with_circular_arcs()
