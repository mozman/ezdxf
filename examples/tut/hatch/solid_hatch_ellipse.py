import ezdxf

dwg = ezdxf.new('AC1015')  # hatch requires the DXF R2000 (AC1015) format or later
msp = dwg.modelspace()  # adding entities to the model space

# important: major axis >= minor axis (ratio <= 1.)
msp.add_ellipse((0, 0), major_axis=(0, 10), ratio=0.5)  # minor axis length = major axis length * ratio

hatch = msp.add_hatch(color=2)  # by default a solid fill hatch with fill color=7 (white/black)
with hatch.edit_boundary() as boundary:  # edit boundary path (context manager)
    # every boundary path is always a 2D element
    edge_path = boundary.add_edge_path()
    # each edge path can contain line arc, ellipse and spline elements
    # important: major axis >= minor axis (ratio <= 1.)
    edge_path.add_ellipse((0, 0), major_axis=(0, 10), ratio=0.5)

dwg.saveas("solid_hatch_ellipse.dxf")
