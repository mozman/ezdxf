#  Copyright (c) 2022-2024, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import pathlib
import ezdxf
from ezdxf import zoom, colors
from ezdxf.math import (
    Vec3,
    estimate_tangents,
    estimate_end_tangent_magnitude,
    global_bspline_interpolation,
    cubic_bezier_interpolation,
    bezier_to_bspline,
    fit_points_to_cad_cv,
    fit_points_to_cubic_bezier,
)
from ezdxf.render import random_2d_path

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

points: list[Vec3] = Vec3.list([(0, 0), (0, 10), (10, 10), (20, 10), (20, 0)])
closed_points: list[Vec3] = list(points)
closed_points.append(points[0])


def setup():
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_lwpolyline(points, dxfattribs={"color": colors.BLUE, "layer": "frame"})
    for p in points:
        msp.add_circle(
            p, radius=0.1, dxfattribs={"color": colors.RED, "layer": "frame"}
        )
    return doc, msp


def open_spline_from_fit_points_by_global_interpolation():
    # 1. Fit points from DXF file: Interpolation without any constraints
    doc, msp = setup()
    # First spline defined by control vertices interpolated from given fit points
    s = global_bspline_interpolation(points, degree=3)
    msp.add_spline(
        dxfattribs={"color": colors.CYAN, "layer": "Global Curve Interpolation"}
    ).apply_construction_tool(s)
    # Second spline defined only by fit points as reference, does not match the
    # BricsCAD interpolation.
    msp.add_spline(
        points,
        degree=3,
        dxfattribs={"layer": "BricsCAD B-spline", "color": colors.YELLOW},
    )

    zoom.extents(msp)
    doc.saveas(CWD / "concept-0-fit-points-only.dxf")


# ------------------------------------------------------------------------------
# SPLINE from fit points WITH given end tangents.
# ------------------------------------------------------------------------------
def open_spline_from_fit_points_and_estimated_end_tangents():
    # 2. Store fit points, start- and end tangent values in DXF file:
    doc, msp = setup()
    # Tangent estimation method: "Total Chord Length",
    # returns sum of chords for m1 and m2
    m1, m2 = estimate_end_tangent_magnitude(points, method="chord")
    # Multiply tangent vectors by total chord length for global interpolation:
    start_tangent = Vec3.from_deg_angle(100) * m1
    end_tangent = Vec3.from_deg_angle(-100) * m2
    # Interpolate control vertices from fit points and end derivatives as constraints
    s = global_bspline_interpolation(
        points, degree=3, tangents=(start_tangent, end_tangent)
    )
    msp.add_spline(
        dxfattribs={"color": colors.CYAN, "layer": "Global Interpolation"}
    ).apply_construction_tool(s)

    # Result matches the BricsCAD interpolation if fit points, start- and end
    # tangents are stored explicit in the DXF file.
    spline = msp.add_spline(
        points,
        degree=3,
        dxfattribs={"layer": "BricsCAD B-spline", "color": colors.YELLOW},
    )
    spline.dxf.start_tangent = Vec3.from_deg_angle(100)
    spline.dxf.end_tangent = Vec3.from_deg_angle(-100)

    zoom.extents(msp)
    doc.saveas(CWD / "concept-1-fit-points-and-tangents.dxf")


def open_spline_from_fit_points_and_5_point_tangent_estimation():
    # 3. Need control vertices to render the B-spline but start- and
    # end tangents are not stored in the DXF file like in scenario 1.
    # Estimation of start- and end tangents is required, best result by:
    # "5 Point Interpolation" from "The NURBS Book", Piegl & Tiller
    doc, msp = setup()
    tangents = estimate_tangents(points, method="5-points")
    # Estimated tangent angles: (108.43494882292201, -108.43494882292201) degree
    m1, m2 = estimate_end_tangent_magnitude(points, method="chord")
    start_tangent = tangents[0].normalize(m1)
    end_tangent = tangents[-1].normalize(m2)
    # Interpolate control vertices from fit points and end derivatives as constraints
    s = global_bspline_interpolation(
        points, degree=3, tangents=(start_tangent, end_tangent)
    )
    msp.add_spline(
        dxfattribs={"color": colors.CYAN, "layer": "Global Interpolation"}
    ).apply_construction_tool(s)
    # Result does not matches the BricsCAD interpolation
    # tangents angle: (101.0035408517495, -101.0035408517495) degree
    msp.add_spline(
        points,
        degree=3,
        dxfattribs={"layer": "BricsCAD B-spline", "color": colors.YELLOW},
    )

    zoom.extents(msp)
    doc.saveas(CWD / "concept-2-tangents-estimated.dxf")


def check_open_spline_from_fit_points_and_5_point_tangent_estimation():
    # Theory Check:
    doc, msp = setup()
    m1, m2 = estimate_end_tangent_magnitude(points, method="chord")
    # Following values are calculated from a DXF file saved by Brics CAD
    # and SPLINE "Method" switched from "fit points" to "control vertices"
    # tangent vector = 2nd control vertex - 1st control vertex
    required_angle = 101.0035408517495  # angle of tangent vector in degrees
    required_magnitude = m1 * 1.3097943444804256  # magnitude of tangent vector
    start_tangent = Vec3.from_deg_angle(required_angle, required_magnitude)
    end_tangent = Vec3.from_deg_angle(-required_angle, required_magnitude)
    s = global_bspline_interpolation(
        points, degree=3, tangents=(start_tangent, end_tangent)
    )
    msp.add_spline(
        dxfattribs={"color": colors.CYAN, "layer": "Global Interpolation"}
    ).apply_construction_tool(s)
    # Now result matches the BricsCAD interpolation - but only in this case
    msp.add_spline(
        points,
        degree=3,
        dxfattribs={"layer": "BricsCAD B-spline", "color": colors.YELLOW},
    )

    zoom.extents(msp)
    doc.saveas(CWD / "concept-3-theory-check.dxf")


def open_spline_from_fit_points_with_end_tangents():
    # 1. If tangents are given (stored in DXF) the magnitude of the input tangents for the
    #    interpolation function is "total chord length".
    # 2. Without given tangents the magnitude is different, in this case: m1*1.3097943444804256,
    #    but it is not a constant factor.
    # The required information is the estimated start- and end tangent in direction and magnitude
    doc, msp = setup()

    # Given start- and end tangent:
    start_tangent = Vec3.from_deg_angle(100)
    end_tangent = Vec3.from_deg_angle(-100)

    # Create SPLINE defined by fit points only:
    spline = msp.add_spline(
        points,
        degree=2,  # degree is ignored by BricsCAD and AutoCAD, both use degree=3
        dxfattribs={
            "layer": "SPLINE from fit points by CAD applications",
            "color": colors.YELLOW,
        },
    )
    spline.dxf.start_tangent = start_tangent
    spline.dxf.end_tangent = end_tangent

    # Create SPLINE defined by control vertices from fit points:
    s = fit_points_to_cad_cv(points, tangents=[start_tangent, end_tangent])
    msp.add_spline(
        dxfattribs={
            "color": colors.CYAN,
            "layer": "SPLINE from control vertices by ezdxf",
        }
    ).apply_construction_tool(s)

    zoom.extents(msp)
    doc.saveas(CWD / "fit_points_to_cad_cv_with_tangents.dxf")


# ------------------------------------------------------------------------------
# SPLINE from fit points WITHOUT given end tangents.
# ------------------------------------------------------------------------------
# Cubic Bézier curve Interpolation:
#
# This works only for cubic B-splines (the most common used B-spline), and
# BricsCAD/AutoCAD allow only a degree of 2 or 3 for SPLINE entities defined
# only by fit points.
#
# Further research showed that quadratic B-splines defined by fit points are
# loaded into BricsCAD / AutoCAD as cubic B-splines. Addition to the statement
# above: BricsCAD and AutoCAD only use a degree of 3 for SPLINE entities defined
# only by fit points.
#
# http://help.autodesk.com/view/OARX/2018/ENU/?guid=OREF-AcDbSpline__setFitData_AcGePoint3dArray__AcGeVector3d__AcGeVector3d__AcGe__KnotParameterization_int_double
# Remark in the AutoCAD ObjectARX reference for AcDbSpline about construction
# of a B-spline from fit points:
# degree has no effect. A spline with degree=3 is always constructed when
# interpolating a series of fit points.
# Sadly this works only for short simple splines.
def spline_by_cubic_bezier_interpolation():
    doc, msp = setup()
    msp.add_spline(
        points,
        degree=2,
        dxfattribs={"layer": "BricsCAD B-spline", "color": colors.YELLOW},
    )
    bezier_curves = cubic_bezier_interpolation(points)
    s = bezier_to_bspline(bezier_curves)
    msp.add_spline(
        dxfattribs={
            "color": colors.MAGENTA,
            "layer": "Cubic Bezier Curve Interpolation",
        }
    ).apply_construction_tool(s)

    zoom.extents(msp)
    doc.saveas(CWD / "concept-4-cubic-bezier-curves.dxf")


# ----------------------------------------------------------------------------
# A better way to create a SPLINE defined by control vertices from fit points
# without given end tangents for SHORT B-splines.
# ----------------------------------------------------------------------------
# This section was removed, because the solution to get the same curve as CAD
# applications was a different approach, not an unknown tangent estimation,
# see this answer on stackoverflow: https://stackoverflow.com/a/74863330/6162864
# This is the visual check for that:
# ----------------------------------------------------------------------------
def check_visually_fit_points_to_cad_cv():
    doc = ezdxf.new()
    doc.layers.add("CAD", color=colors.RED)
    doc.layers.add("EZDXF", color=colors.YELLOW)
    msp = doc.modelspace()
    msp.add_spline(points, dxfattribs={"layer": "CAD"})

    spline = msp.add_spline(dxfattribs={"layer": "EZDXF"})
    spline.apply_construction_tool(fit_points_to_cad_cv(points))

    doc.saveas(CWD / "check_spline_from_fit_points.dxf")


# ------------------------------------------------------------------------------
# Closed SPLINE from fit points WITHOUT given end tangents.
# ------------------------------------------------------------------------------
# IMPORTANT: first points == last point is required
def closed_spline_from_fit_points():
    doc, msp = setup()
    # Create closed SPLINE defined by fit points only:
    msp.add_spline(
        closed_points,
        dxfattribs={
            "layer": "SPLINE from fit points by CAD applications",
            "color": colors.YELLOW,
        },
    )
    # spline.closed = True  # ignored if first points != last point

    # Create SPLINE defined by control vertices from fit points:
    msp.add_spline(
        dxfattribs={
            "color": colors.MAGENTA,
            "layer": "Cubic Bezier Curve Interpolation",
        }
    ).apply_construction_tool(fit_points_to_cubic_bezier(closed_points))

    # The fit_points_to_cad_cv() function creates the same result as CAD applications:
    msp.add_spline(
        dxfattribs={"color": colors.CYAN, "layer": "fit_points_to_cad_cv()"}
    ).apply_construction_tool(fit_points_to_cad_cv(closed_points))

    zoom.extents(msp)
    doc.saveas(CWD / "closed_spline_from_fit_points.dxf")


# ------------------------------------------------------------------------------
# Closed SPLINE from fit points WITH given end tangents.
# ------------------------------------------------------------------------------
# IMPORTANT: first points == last point is required
def closed_spline_from_fit_points_with_tangent():
    doc, msp = setup()
    # Create closed SPLINE defined by fit points only:
    spline = msp.add_spline(
        closed_points,
        dxfattribs={
            "layer": "SPLINE from fit points by CAD applications",
            "color": colors.RED,
        },
    )
    spline.closed = True  # ignored for splines from fit points

    tangents = estimate_tangents(points, method="5-points")
    # Remark: TrueView 2022 works only with normalized tangents
    start_tangent = tangents[0].normalize()
    # same tangent for start- and end-point
    end_tangent = start_tangent

    spline.dxf.start_tangent = start_tangent
    spline.dxf.end_tangent = end_tangent

    # Create SPLINE defined by control vertices from fit points:
    msp.add_spline(
        dxfattribs={"color": colors.YELLOW, "layer": "fit_points_to_cad_cv()"}
    ).apply_construction_tool(
        fit_points_to_cad_cv(closed_points, [start_tangent, end_tangent])
    )

    zoom.extents(msp)
    doc.saveas(CWD / "closed_spline_from_fit_points_with_tangent_estimation.dxf")


# ------------------------------------------------------------------------------
# Random walk open SPLINE from fit points
# ------------------------------------------------------------------------------
def random_walk_open_spline():
    doc = ezdxf.new()
    msp = doc.modelspace()
    walk = list(random_2d_path(10))

    msp.add_spline(
        walk,
        dxfattribs={
            "layer": "SPLINE from fit points by CAD applications",
            "color": colors.RED,
        },
    )

    msp.add_spline(
        dxfattribs={
            "color": colors.YELLOW,
            "layer": "EZDXF fit_points_to_cad_cv",
        }
    ).apply_construction_tool(fit_points_to_cad_cv(walk))

    zoom.extents(msp, 1.1)
    doc.saveas(CWD / "random_walk.dxf")


if __name__ == "__main__":
    open_spline_from_fit_points_by_global_interpolation()
    open_spline_from_fit_points_and_estimated_end_tangents()
    open_spline_from_fit_points_and_5_point_tangent_estimation()
    open_spline_from_fit_points_with_end_tangents()
    spline_by_cubic_bezier_interpolation()
    check_visually_fit_points_to_cad_cv()
    closed_spline_from_fit_points()
    closed_spline_from_fit_points_with_tangent()
    random_walk_open_spline()
