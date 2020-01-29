import ezdxf

doc = ezdxf.new('R2000')  # hatch requires the DXF R2000 (AC1015) format or later
msp = doc.modelspace()  # adding entities to the model space

# important: major axis >= minor axis (ratio <= 1.)
# minor axis length = major axis length * ratio
msp.add_ellipse((0, 0), major_axis=(0, 10), ratio=0.5)

# by default a solid fill hatch with fill color=7 (white/black)
hatch = msp.add_hatch(color=2)

# every boundary path is always a 2D element
edge_path = hatch.paths.add_edge_path()
# each edge path can contain line arc, ellipse and spline elements
# important: major axis >= minor axis (ratio <= 1.)
edge_path.add_ellipse((0, 0), major_axis=(0, 10), ratio=0.5)

doc.saveas("solid_hatch_ellipse.dxf")
