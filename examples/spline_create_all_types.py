# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import os
# os.environ["EZDXF_DISABLE_C_EXT"] = "1"
from pathlib import Path
import ezdxf
from ezdxf import zoom
from ezdxf.math import Vec3

DIR = Path('~/Desktop/outbox').expanduser()

points = Vec3.list([(1, 1), (4, 5), (7, 4), (10, 7), (12, 3), (7, 1)])
closed_points = list(points)
closed_points.append(closed_points[0])


def new_doc():
    doc = ezdxf.new()
    doc.layers.new("SPLINE", dxfattribs={'color': 1})
    doc.layers.new("EZDXF", dxfattribs={'color': 2})
    doc.layers.new("FLATTEN", dxfattribs={'color': 3})
    doc.layers.new("FRAME", dxfattribs={'color': 5})
    doc.layers.new("FIT", dxfattribs={'color': 1})
    msp = doc.modelspace()
    return doc, msp


def save(name):
    zoom.extents(msp)
    doc.saveas(DIR / name)


def add_control_polyline(spline):
    s = spline.construction_tool()
    msp.add_lwpolyline(s.flattening(0.01), dxfattribs={'layer': 'FLATTEN'})


def add_control_frame(spline):
    cpoints = spline.control_points
    msp.add_lwpolyline(cpoints, dxfattribs={'layer': 'FRAME'})
    for point in cpoints:
        msp.add_circle(point, radius=0.05, dxfattribs={'layer': 'FRAME'})


def add_fit_points(points):
    for point in points:
        msp.add_circle(point, radius=0.05, dxfattribs={'layer': 'FIT'})


# A B-spline is only defined by the control points and the knot values and the
# degree. The B-spline does not pass the control points.
# The examples always use a degree of 3, AutoCAD has a fixed upper limit of
# degree = 11.
# The created B-spline is always clamped if not stated otherwise.
# clamped means: the curve starts at the first control point and ends at the
# last control point.
#
# For the rest of the file I will sometimes use BricsCAD as synonym for AutoCAD,
# because that is the CAD application I use for research and testing.
# SPLINE means the DXF entity, B-spline means the algebraic curve.

# ------------------------------------------------------------------------------
# OPEN SPLINE from fit points WITHOUT given end tangents.
# tl;dr not recommended way to define B-splines!
#
# Sets only the fit points of the SPLINE entity and let the CAD application
# calculate the control points, the degree of this spline is always 3, the
# stored value for degree is ignored by AutoCAD.
#
# Problem:
# For a given set of fit points exist infinite solutions and the AutoCAD picks
# one without telling how its chosen. Therefore the result of this calculation
# of the control points is not reproducible (yet! I am working on it).
#
# Conclusion:
# This is the easiest way to define SPLINE entities, but also the least
# reliable, if you want the same rendering of the SPLINE in every
# CAD application.
# ------------------------------------------------------------------------------
doc, msp = new_doc()
msp.add_spline(fit_points=points, dxfattribs={'layer': 'SPLINE'})

# ezdxf provides a method to calculate the control points from the fit points
# without given end tangents like AutoCAD, but the result is not a perfect match.
spline = msp.add_cad_spline_control_frame(
    points, estimate='5-p', dxfattribs={'layer': 'EZDXF'})

add_fit_points(points)
add_control_frame(spline)
add_control_polyline(spline)
save(DIR / "open_spline_from_fit_points.dxf")

# ------------------------------------------------------------------------------
# OPEN SPLINE from fit points WITH given end tangents.
#
# Sets the fit points and the start- and end tangents of the SPLINE entity.
# Set tangents as vectors in curve direction, which goes from start- to
# end point. CAD applications do accept tangents as non unit vectors, but their
# magnitude is ignored.
#
# Conclusion:
# This is a more reliable way to define the SPLINE entity, but is also not
# guaranteed that other CAD application render the same curve as AutoCAD.
# ------------------------------------------------------------------------------
# noinspection PyRedeclaration
doc, msp = new_doc()
msp.add_spline(fit_points=points, dxfattribs={
    'start_tangent': (0, 1),
    'end_tangent': (-1, 0),
    'layer': 'SPLINE'
})

# ------------------------------------------------------------------------------
# Add SPLINE defined by CONTROL POINTS
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# RECOMMENDED: use ezdxf to calculate the control points
#
# The method add_cad_spline_control_frame() can calculate the control points
# with a perfect match to AutoCAD, if you provide the start- and end tangents.
# This is a reliable way to define the SPLINE entity by control points for any
# CAD application without any ambiguity.
# ------------------------------------------------------------------------------
spline = msp.add_cad_spline_control_frame(
    points, tangents=[(0, 1), (-1, 0)], dxfattribs={'layer': 'EZDXF'})
add_fit_points(points)
add_control_frame(spline)
save(DIR / "open_spline_from_fit_points_with_end_tangents.dxf")

# ------------------------------------------------------------------------------
# Add SPLINE defined by control points from fit points.
#
# Layout.add_spline_control_frame(), creates the control points from a simple
# global curve interpolation of the given fit points without end tangent
# constraints. This is similar to add_cad_spline_control_frame(), but does not
# care about replicating the same curve as AutoCAD would create.
# And because this method uses control points to define the SPLINE, the SPLINE
# looks always the same, no matter which CAD application renders the SPLINE.
# ------------------------------------------------------------------------------
doc, msp = new_doc()
spline = msp.add_spline_control_frame(fit_points=points,
                                      dxfattribs={'layer': 'SPLINE'})
add_fit_points(points)
add_control_frame(spline)
add_control_polyline(spline)
save(DIR / "open_spline_by_add_spline_control_frame.dxf")

# ------------------------------------------------------------------------------
# Define SPLINE only by control points
#
# This methods add SPLINE entities defined only by control points. These methods
# provides access to the mathematical base form, but may not very useful for
# practical construction work.
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# OPEN clamped SPLINE by control points
#
# This SPLINE starts at the first control point and ends at the last control
# point, but does not pass through the control points between these points.
# ------------------------------------------------------------------------------

doc, msp = new_doc()
spline = msp.add_open_spline(points, dxfattribs={'layer': 'SPLINE'})

add_control_frame(spline)
add_control_polyline(spline)
save(DIR / "open_clamped_spline_by_control_points.dxf")

# ------------------------------------------------------------------------------
# OPEN unclamped SPLINE by control points  **BROKEN**
# ------------------------------------------------------------------------------

doc, msp = new_doc()
spline = msp.add_spline(dxfattribs={'layer': 'SPLINE'})
spline.set_uniform(points)

add_control_frame(spline)
add_control_polyline(spline)
save(DIR / "open_unclamped_spline_by_control_points.dxf")
