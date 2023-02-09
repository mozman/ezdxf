# Copyright (c) 2018-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.math import Vec3, ConstructionArc, UCS

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use the ConstructionArc class to create an ARC
# entity from various scenarios:
# - ARC from 3 points
# - ARC from 2 points and the enclosing angle
# - ARC from 2 points and a radius
#
# ConstructionArc: https://ezdxf.mozman.at/docs/math/core.html#constructionarc
# ------------------------------------------------------------------------------

doc = ezdxf.new("R2000")
modelspace = doc.modelspace()

# ------------------------------------------------------------------------------
# create a 2D arc in the xy-plane from center, radius, start- and end angle:
delta = 30
for count in range(12):
    modelspace.add_arc(
        center=(0, 0),
        radius=10 + count,
        start_angle=count * delta,  # in degrees
        end_angle=(count + 1) * delta,  # in degrees
    )
    # The curve is always drawn counter-clockwise from the start angle to the
    # end angle.

# ------------------------------------------------------------------------------
# create a 3D arc from 3 points in WCS
start_point_wcs = Vec3(3, 0, 0)
end_point_wcs = Vec3(0, 3, 0)
def_point_wcs = Vec3(0, 0, 3)

# create an UCS
ucs = UCS.from_x_axis_and_point_in_xy(
    origin=def_point_wcs,
    axis=start_point_wcs - def_point_wcs,
    point=end_point_wcs,
)

# transform construction points into the xy-plane of the UCS, to reduce the
# complexity of the problem
start_point_ucs = ucs.from_wcs(start_point_wcs)
end_point_ucs = ucs.from_wcs(end_point_wcs)
def_point_ucs = Vec3(0, 0)  # origin of UCS

# create the 2D arc in the xy-plane of the UCS
arc = ConstructionArc.from_3p(start_point_ucs, end_point_ucs, def_point_ucs)
arc.add_to_layout(modelspace, ucs, dxfattribs={"color": 1})  # red arc

arc = ConstructionArc.from_3p(end_point_ucs, start_point_ucs, def_point_ucs)
arc.add_to_layout(modelspace, ucs, dxfattribs={"color": 2})  # yellow arc

# ------------------------------------------------------------------------------
# create a 2D arc from 2 points and the enclosing angle in counter-clockwise
# orientation
p1 = Vec3(0, -18)
p2 = Vec3(0, +18)
arc = ConstructionArc.from_2p_angle(p1, p2, 90)
arc.add_to_layout(modelspace, dxfattribs={"color": 1})

# ------------------------------------------------------------------------------
# create the same arc in clockwise orientation
arc = ConstructionArc.from_2p_angle(p1, p2, 90, ccw=False)
arc.add_to_layout(modelspace, dxfattribs={"color": 2})

# ------------------------------------------------------------------------------
# create a 2D arc from 2 points and a radius in counter-clockwise orientation
p1 = Vec3(20, -18)
p2 = Vec3(20, +18)
arc = ConstructionArc.from_2p_radius(p1, p2, 100)
arc.add_to_layout(modelspace, dxfattribs={"color": 1})

# ------------------------------------------------------------------------------
# create a 2D arc from 2 points and a radius in clockwise orientation
arc = ConstructionArc.from_2p_radius(p1, p2, 100, ccw=False)
arc.add_to_layout(modelspace, dxfattribs={"color": 2})

# ------------------------------------------------------------------------------
# create a 2D arc from 2 points and a radius, overriding the default placement
# of the arc center point
arc = ConstructionArc.from_2p_radius(p1, p2, 100, center_is_left=False)
arc.add_to_layout(modelspace, dxfattribs={"color": 3})

arc = ConstructionArc.from_2p_radius(
    p1, p2, 100, ccw=False, center_is_left=False
)
arc.add_to_layout(modelspace, dxfattribs={"color": 4})

# saving DXF file
filename = CWD / "arcs.dxf"
doc.saveas(filename)
print(f"drawing {filename} created.")
