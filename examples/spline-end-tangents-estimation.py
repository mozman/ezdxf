# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import math
import ezdxf
from ezdxf import zoom
from ezdxf.math import (
    Vec3, estimate_tangents, estimate_end_tangent_magnitude, global_bspline_interpolation, linspace
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
msp.add_spline(dxfattribs={'color': 4, 'layer': 'Global Interpolation'}).apply_construction_tool(s)
# Second spline defined only by fit points as reference, does not match the BricsCAD interpolation.
spline = msp.add_spline(points, degree=3, dxfattribs={'layer': 'BricsCAD B-spline', 'color': 2})

zoom.extents(msp)
doc.saveas(DIR / 'fit-points-only.dxf')

# 2. Store fit points, start- and end tangent values in DXF file:
doc, msp = setup()
# Tangent estimation method: "Total Chord Length",
# returns sum of chords for m1 and m2
m1, m2 = estimate_end_tangent_magnitude(points, method='chord')
# Multiply tangent vectors by total chord length for global interpolation:
start_tangent = Vec3.from_deg_angle(100) * m1
end_tangent = Vec3.from_deg_angle(-100) * m2
# Interpolate control vertices from fit points and end derivatives as constraints
s = global_bspline_interpolation(points, degree=3, tangents=(start_tangent, end_tangent))
msp.add_spline(dxfattribs={'color': 4, 'layer': 'Global Interpolation'}).apply_construction_tool(s)
# Result matches the BricsCAD interpolation if fit points, start- and end
# tangents are stored explicit in the DXF file.
spline = msp.add_spline(points, degree=3, dxfattribs={'layer': 'BricsCAD B-spline', 'color': 2})
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
s = global_bspline_interpolation(points, degree=3, tangents=(start_tangent, end_tangent))
msp.add_spline(dxfattribs={'color': 4, 'layer': 'Global Interpolation'}).apply_construction_tool(s)
# Result does not matches the BricsCAD interpolation
# tangents angle: (101.0035408517495, -101.0035408517495) degree
msp.add_spline(points, degree=3, dxfattribs={'layer': 'BricsCAD B-spline', 'color': 2})

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
s = global_bspline_interpolation(points, degree=3, tangents=(start_tangent, end_tangent))
msp.add_spline(dxfattribs={'color': 4, 'layer': 'Global Interpolation'}).apply_construction_tool(s)
# Now result matches the BricsCAD interpolation - but only in this case
msp.add_spline(points, degree=3, dxfattribs={'layer': 'BricsCAD B-spline', 'color': 2})

zoom.extents(msp)
doc.saveas(DIR / 'theory-check.dxf')

# 1. If tangents are given (stored in DXF) the magnitude of the input tangents for the
#    interpolation function is "total chord length".
# 2. Without given tangents the magnitude is different, in this case: m1*1.3097943444804256,
#    but it is not a constant factor.
# The required information is the estimated start- and end tangent in direction and magnitude
