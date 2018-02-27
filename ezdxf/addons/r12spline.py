# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
"""
DXF R12 Splines
===============

DXF R12 supports 2d B-splines, but Autodesk do not document the usage in the DXF Reference.
The base entity for splines in DXF R12 is the POLYLINE entity.

Transformed Into 3D Space
-------------------------

The spline itself is always in a plane, but as any 2d entity, the spline can be transformed into the 3d object
by elevation, extrusion and thickness/width.

Open Quadratic Spline with Fit Vertices
---------------------------------------

Example: 2D_SPLINE_QUADRATIC.dxf
expected knot vector: open uniform
degree: 2
order: 3

POLYLINE:
flags (70): 4 = SPLINE_FIT_VERTICES_ADDED
smooth type (75): 5 = QUADRIC_BSPLINE

Sequence of VERTEX
flags (70): SPLINE_VERTEX_CREATED = 8  # Spline vertex created by spline-fitting

This vertices are the curve vertices of the spline (fitted).

Frame control vertices appear after the curve vertices.

Sequence of VERTEX
flags (70): SPLINE_FRAME_CONTROL_POINT = 16

No control point at the starting point, but a control point at the end point,
last control point == last fit vertex

Open Cubic Spline with Fit Vertices
-----------------------------------

Example: 2D_SPLINE_CUBIC.dxf
expected knot vector: open uniform
degree: 3
order: 4

POLYLINE:
flags (70): 4 = SPLINE_FIT_VERTICES_ADDED
smooth type (75): 6 = CUBIC_BSPLINE

Sequence of VERTEX
flags (70): SPLINE_VERTEX_CREATED = 8  # Spline vertex created by spline-fitting

This vertices are the curve vertices of the spline (fitted).

Frame control vertices appear after the curve vertices.

Sequence of VERTEX
flags (70): SPLINE_FRAME_CONTROL_POINT = 16

No control point at the starting point, but a control point at the end point,
last control point == last fit vertex


"""


class R12Spline(object):
    pass
