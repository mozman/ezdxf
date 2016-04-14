import ezdxf

dwg = ezdxf.new('AC1015')  # hatch requires the DXF R2000 (AC1015) format or later
msp = dwg.modelspace()  # adding entities to the model space

hatch = msp.add_hatch(color=2)  # by default a solid fill hatch with fill color=7 (white/black)
with hatch.edit_boundary() as boundary:  # edit boundary path (context manager)
    # every boundary path is always a 2D element
    # vertex format for the polyline path is: (x, y[, bulge])
    # there are no bulge values in this example
    boundary.add_polyline_path([(0, 0), (10, 0), (10, 10), (0, 10)], is_closed=1)

dwg.saveas("solid_hatch_polyline_path.dxf")
