import ezdxf

doc = ezdxf.new('R2004')  # hatch with true color requires DXF R2004 (AC1018) or later
msp = doc.modelspace()  # adding entities to the model space

# important: major axis >= minor axis (ratio <= 1.)
msp.add_ellipse((0, 0), major_axis=(0, 10), ratio=0.5)  # minor axis length = major axis length * ratio

hatch = msp.add_hatch()  # use default ACI fill color
hatch.rgb = (211, 40, 215)

# every boundary path is always a 2D element
edge_path = hatch.paths.add_edge_path()
# each edge path can contain line arc, ellipse and spline elements
# important: major axis >= minor axis (ratio <= 1.)
edge_path.add_ellipse((0, 0), major_axis=(0, 10), ratio=0.5)

doc.saveas("solid_rgb_hatch.dxf")
