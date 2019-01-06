# Purpose: ARC example
# Created: 09.07.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.algebra import Vector, ConstructionArc, UCS

dwg = ezdxf.new('R2000')
modelspace = dwg.modelspace()

# create a 2D arcs in xy-plane
delta = 30
for count in range(12):
    modelspace.add_arc(center=(0, 0), radius=10+count, start_angle=count*delta, end_angle=(count+1)*delta)

# create a 3D arc from 3 points in WCS
start_point_wcs = Vector(3, 0, 0)
end_point_wcs = Vector(0, 3, 0)
def_point_wcs = Vector(0, 0, 3)

# create UCS
ucs = UCS.from_x_axis_and_point_in_xy(origin=def_point_wcs, axis=start_point_wcs-def_point_wcs, point=end_point_wcs)
start_point_ucs = ucs.from_wcs(start_point_wcs)
end_point_ucs = ucs.from_wcs(end_point_wcs)
def_point_ucs = Vector(0, 0)  # origin of UCS

# create arc in the xy-plane of the UCS
arc = ConstructionArc.from_3p(start_point_ucs, end_point_ucs, def_point_ucs)
arc.add_to_layout(modelspace, ucs, dxfattribs={'color': 1})  # red arc

arc = ConstructionArc.from_3p(end_point_ucs, start_point_ucs, def_point_ucs)
arc.add_to_layout(modelspace, ucs, dxfattribs={'color': 2})  # yellow arc

p1 = Vector(0, -18)
p2 = Vector(0, +18)
arc = ConstructionArc.from_2p_angle(p1, p2, 90)
arc.add_to_layout(modelspace, dxfattribs={'color': 1})

arc = ConstructionArc.from_2p_angle(p1, p2, 90, ccw=False)
arc.add_to_layout(modelspace, dxfattribs={'color': 2})

p1 = Vector(20, -18)
p2 = Vector(20, +18)
arc = ConstructionArc.from_2p_radius(p1, p2, 100)
arc.add_to_layout(modelspace, dxfattribs={'color': 1})

arc = ConstructionArc.from_2p_radius(p1, p2, 100, ccw=False)
arc.add_to_layout(modelspace, dxfattribs={'color': 2})

arc = ConstructionArc.from_2p_radius(p1, p2, 100, center_is_left=False)
arc.add_to_layout(modelspace, dxfattribs={'color': 3})

arc = ConstructionArc.from_2p_radius(p1, p2, 100, ccw=False, center_is_left=False)
arc.add_to_layout(modelspace, dxfattribs={'color': 4})

# saving DXF file
filename = 'using_arcs.dxf'
dwg.saveas(filename)
print("drawing '%s' created.\n" % filename)
