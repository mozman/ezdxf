# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from pathlib import Path
import math
import ezdxf
from ezdxf import zoom
from ezdxf.math import (
    Vec3, estimate_tangents, estimate_end_tangent_magnitude,
    global_bspline_interpolation, linspace, cubic_bezier_interpolation,
    bezier_to_bspline, fit_points_to_cad_cv,
)

DIR = Path('~/Desktop/Outbox').expanduser()
points = Vec3.list([(0, 0), (0, 10), (10, 10), (20, 10), (20, 0)])


def sine_wave(count: int, scale: float = 1.0):
    for t in linspace(0, math.tau, count):
        yield Vec3(t * scale, math.sin(t) * scale)


def setup():
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_lwpolyline(points, dxfattribs={'color': 5, 'layer': 'frame'})
    for p in points:
        msp.add_circle(p, radius=0.1, dxfattribs={'color': 1, 'layer': 'frame'})
    return doc, msp


# 1. Fit points from DXF file: Interpolation without any constraints
doc, msp = setup()
# First spline defined by control vertices interpolated from given fit points
s = global_bspline_interpolation(points, degree=3)
msp.add_spline(
    dxfattribs={
        'color': 4,
        'layer': 'Global Interpolation'
    }
).apply_construction_tool(s)
# Second spline defined only by fit points as reference, does not match the BricsCAD interpolation.
spline = msp.add_spline(
    points,
    degree=3,
    dxfattribs={
        'layer': 'BricsCAD B-spline',
        'color': 2
    }
)

zoom.extents(msp)
doc.saveas(DIR / 'fit-points-only.dxf')

# ------------------------------------------------------------------------------
# SPLINE from fit points WITH given end tangents.
# ------------------------------------------------------------------------------

# 2. Store fit points, start- and end tangent values in DXF file:
doc, msp = setup()
# Tangent estimation method: "Total Chord Length",
# returns sum of chords for m1 and m2
m1, m2 = estimate_end_tangent_magnitude(points, method='chord')
# Multiply tangent vectors by total chord length for global interpolation:
start_tangent = Vec3.from_deg_angle(100) * m1
end_tangent = Vec3.from_deg_angle(-100) * m2
# Interpolate control vertices from fit points and end derivatives as constraints
s = global_bspline_interpolation(points, degree=3,
                                 tangents=(start_tangent, end_tangent))
msp.add_spline(
    dxfattribs={
        'color': 4,
        'layer': 'Global Interpolation'
    }
).apply_construction_tool(s)
# Result matches the BricsCAD interpolation if fit points, start- and end
# tangents are stored explicit in the DXF file.
spline = msp.add_spline(
    points,
    degree=3,
    dxfattribs={
        'layer': 'BricsCAD B-spline',
        'color': 2
    }
)
spline.dxf.start_tangent = Vec3.from_deg_angle(100)
spline.dxf.end_tangent = Vec3.from_deg_angle(-100)

zoom.extents(msp)
doc.saveas(DIR / 'fit-points-and-tangents.dxf')

# 3. Need control vertices to render the B-spline but start- and
# end tangents are not stored in the DXF file like in scenario 1.
# Estimation of start- and end tangents is required, best result by:
# "5 Point Interpolation" from "The NURBS Book", Piegl & Tiller
doc, msp = setup()
tangents = estimate_tangents(points, method='5-points')
# Estimated tangent angles: (108.43494882292201, -108.43494882292201) degree
m1, m2 = estimate_end_tangent_magnitude(points, method='chord')
start_tangent = tangents[0].normalize(m1)
end_tangent = tangents[-1].normalize(m2)
# Interpolate control vertices from fit points and end derivatives as constraints
s = global_bspline_interpolation(points, degree=3,
                                 tangents=(start_tangent, end_tangent))
msp.add_spline(
    dxfattribs={
        'color': 4,
        'layer': 'Global Interpolation'
    }
).apply_construction_tool(s)
# Result does not matches the BricsCAD interpolation
# tangents angle: (101.0035408517495, -101.0035408517495) degree
msp.add_spline(
    points,
    degree=3,
    dxfattribs={
        'layer': 'BricsCAD B-spline',
        'color': 2
    }
)

zoom.extents(msp)
doc.saveas(DIR / 'tangents-estimated.dxf')

# Theory Check:
doc, msp = setup()
m1, m2 = estimate_end_tangent_magnitude(points, method='chord')
# Following values are calculated from a DXF file saved by Brics CAD
# and SPLINE "Method" switched from "fit points" to "control vertices"
# tangent vector = 2nd control vertex - 1st control vertex
required_angle = 101.0035408517495  # angle of tangent vector in degrees
required_magnitude = m1 * 1.3097943444804256  # magnitude of tangent vector
start_tangent = Vec3.from_deg_angle(required_angle, required_magnitude)
end_tangent = Vec3.from_deg_angle(-required_angle, required_magnitude)
s = global_bspline_interpolation(points, degree=3,
                                 tangents=(start_tangent, end_tangent))
msp.add_spline(dxfattribs={
    'color': 4,
    'layer': 'Global Interpolation'}).apply_construction_tool(s)
# Now result matches the BricsCAD interpolation - but only in this case
msp.add_spline(points, degree=3,
               dxfattribs={'layer': 'BricsCAD B-spline', 'color': 2})

zoom.extents(msp)
doc.saveas(DIR / 'theory-check.dxf')

# 1. If tangents are given (stored in DXF) the magnitude of the input tangents for the
#    interpolation function is "total chord length".
# 2. Without given tangents the magnitude is different, in this case: m1*1.3097943444804256,
#    but it is not a constant factor.
# The required information is the estimated start- and end tangent in direction and magnitude

# ----------------------------------------------------------------------------
# Recommend way to create a SPLINE defined by control vertices from fit points
# with given end tangents:
# ----------------------------------------------------------------------------
doc, msp = setup()

# Given start- and end tangent:
start_tangent = Vec3.from_deg_angle(100)
end_tangent = Vec3.from_deg_angle(-100)

# Create SPLINE defined by fit points only:
spline = msp.add_spline(
    points,
    degree=2,  # degree is ignored by BricsCAD and AutoCAD, both use degree=3
    dxfattribs={
        'layer': 'SPLINE from fit points by CAD applications',
        'color': 2
    }
)
spline.dxf.start_tangent = start_tangent
spline.dxf.end_tangent = end_tangent

# Create SPLINE defined by control vertices from fit points:
s = fit_points_to_cad_cv(points, tangents=[start_tangent, end_tangent])
msp.add_spline(
    dxfattribs={
        'color': 4,
        'layer': 'SPLINE from control vertices by ezdxf'
    }
).apply_construction_tool(s)

zoom.extents(msp)
doc.saveas(DIR / 'fit_points_to_cad_cv_with_tangents.dxf')


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

doc, msp = setup()
msp.add_spline(points, degree=2,
               dxfattribs={'layer': 'BricsCAD B-spline', 'color': 2})
bezier_curves = cubic_bezier_interpolation(points)
s = bezier_to_bspline(bezier_curves)
msp.add_spline(
    dxfattribs={
        'color': 4,
        'layer': 'Cubic Bezier Curve Interpolation'
    }
).apply_construction_tool(s)

zoom.extents(msp)
doc.saveas(DIR / 'cubic-bezier-curves.dxf')

# ----------------------------------------------------------------------------
# Recommend way to create a SPLINE defined by control vertices from fit points
# without given end tangents:
# ----------------------------------------------------------------------------
doc, msp = setup()

# Create SPLINE defined by fit points only:
msp.add_spline(
    points,
    degree=2,  # degree is ignored by BricsCAD and AutoCAD, both use degree=3
    dxfattribs={
        'layer': 'SPLINE from fit points by CAD applications',
        'color': 2
    }
)

# Create SPLINE defined by control vertices from fit points:
msp.add_spline(
    dxfattribs={
        'color': 4,
        'layer': 'SPLINE from control vertices by ezdxf'
    }
).apply_construction_tool(fit_points_to_cad_cv(points))

zoom.extents(msp)
doc.saveas(DIR / 'fit_points_to_cad_cv_without_tangents.dxf')
