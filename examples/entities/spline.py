# Copyright (c) 2014-2022, Manfred Moitzi
# License: MIT License
from typing import cast
import pathlib
import ezdxf
from ezdxf.math.bspline import fit_points_to_cad_cv
from ezdxf.math import BSpline, Vec3
from ezdxf.entities import Spline


CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create and edit SPLINE entities.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/spline.html
# tutorial: https://ezdxf.mozman.at/docs/tutorials/spline.html
# ------------------------------------------------------------------------------


def fit_spline():
    doc = ezdxf.new("R2000")
    fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
    msp = doc.modelspace()
    spline = msp.add_spline(fit_points)
    spline.dxf.start_tangent = (1, 0, 0)
    spline.dxf.end_tangent = (0, 1, 0)
    doc.saveas(CWD / "Spline_R2000_fit_spline.dxf")


def clone_spline():
    doc = ezdxf.readfile(CWD / "Spline_R2000_fit_spline.dxf")
    msp = doc.modelspace()
    spline = cast(Spline, msp.query("SPLINE").first)
    # delete the existing spline from model space and drawing database
    msp.delete_entity(spline)
    # add a new spline
    msp.add_spline(spline.fit_points)
    doc.saveas(CWD / "Spline_R2000_clone_Spline.dxf")


def fit_spline_with_control_points():
    doc = ezdxf.new("R2000")
    fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
    control_points = [
        (0, 0, 0),
        (1250, 1560, 0),
        (3130, 610, 0),
        (2250, 1250, 0),
    ]
    msp = doc.modelspace()
    spline = msp.add_spline(fit_points)
    spline.dxf.degree = 3
    spline.control_points = control_points
    doc.saveas(CWD / "Spline_R2000_fit_spline_and_control_points.dxf")


def add_points_to_spline():
    doc = ezdxf.readfile(CWD / "Spline_R2000_fit_spline.dxf")
    msp = doc.modelspace()
    spline = cast(Spline, msp.query("SPLINE").first)

    spline.fit_points.append((3130, 610, 0))
    # As far I tested this works without complaints from AutoCAD, but for the case of problems
    spline.control_points = (
        []
    )  # delete control points, this could modify the geometry of the spline
    spline.knots = (
        []
    )  # delete knot values, this shouldn't modify the geometry of the spline
    spline.weights = (
        []
    )  # delete weights, this could modify the geometry of the spline

    doc.saveas(CWD / "Spline_R2000_with_added_points.dxf")


def open_spline():
    doc = ezdxf.new("R2000")
    control_points = [
        (0, 0, 0),
        (1250, 1560, 0),
        (3130, 610, 0),
        (2250, 1250, 0),
    ]
    msp = doc.modelspace()
    msp.add_open_spline(control_points, degree=3)
    doc.saveas(CWD / "Spline_R2000_open_spline.dxf")


def rational_spline():
    doc = ezdxf.new("R2000")
    control_points = [
        (0, 0, 0),
        (1250, 1560, 0),
        (3130, 610, 0),
        (2250, 1250, 0),
    ]
    weights = [1, 10, 1, 1]
    msp = doc.modelspace()
    msp.add_rational_spline(control_points, weights, degree=3)
    doc.saveas(CWD / "Spline_R2000_rational_spline.dxf")


def spline_control_frame_from_fit_points():
    # The fit_points_to_cad_cv() function uses always the best method I
    # currently know of to calculate the control vertices from the fit points.
    # It is still not perfect if the start- and end tangent of the SPLINE are
    # not known.

    doc = ezdxf.new("R2000", setup=True)
    fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
    msp = doc.modelspace()
    msp.add_polyline2d(fit_points, dxfattribs={"color": 2, "linetype": "DOT2"})

    def add_spline(color=3):
        spline = fit_points_to_cad_cv(fit_points)
        msp.add_polyline2d(
            spline.control_points,
            dxfattribs={"color": color, "linetype": "DASHED"},
        )
        msp.add_open_spline(
            spline.control_points,
            degree=spline.degree,
            dxfattribs={"color": color},
        )

    add_spline(color=4)
    msp.add_spline(fit_points, degree=3, dxfattribs={"color": 1})
    doc.saveas(CWD / "Spline_R2000_spline_control_frame_from_fit_points.dxf")


def spline_insert_knot():
    doc = ezdxf.new("R2000", setup=True)
    msp = doc.modelspace()

    def add_spline(control_points, color=3, knots=None):
        msp.add_polyline2d(
            control_points, dxfattribs={"color": color, "linetype": "DASHED"}
        )
        msp.add_open_spline(
            control_points, degree=3, knots=knots, dxfattribs={"color": color}
        )

    control_points = Vec3.list(
        [
            (0, 0),
            (10, 20),
            (30, 10),
            (40, 10),
            (50, 0),
            (60, 20),
            (70, 50),
            (80, 70),
        ]
    )
    add_spline(control_points, color=3, knots=None)

    bspline = BSpline(control_points, order=4)
    bspline.insert_knot(bspline.max_t / 2)
    add_spline(bspline.control_points, color=4, knots=bspline.knots())

    doc.saveas(CWD / "Spline_R2000_spline_insert_knot.dxf")


if __name__ == "__main__":
    fit_spline()
    clone_spline()
    fit_spline_with_control_points()
    add_points_to_spline()
    open_spline()
    rational_spline()
    spline_control_frame_from_fit_points()
    spline_insert_knot()
