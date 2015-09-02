import ezdxf

dwg = ezdxf.new('AC1015')  # hatch requires the DXF R2000 (AC1015) or newer format
msp = dwg.modelspace()  # adding entities to the model space

hatch = msp.add_hatch(color=2)  # by default a solid fill hatch with fill color 7 (white/black)
with hatch.edit_boundary() as boundary:  # edit boundary path (context manager)
    # every boundary path is always a 2D element
    # vertex format for the polyline path is: (x, y[, bulge])
    # bulge value 1 = an arc with diameter=10 (= distance to next vertex * bulge value)
    # bulge value > 0 ... arc is right of line
    # bulge value < 0 ... arc is left of line
    boundary.add_polyline_path([(0, 0, 1), (10, 0), (10, 10, -0.5), (0, 10)], is_closed=1)

dwg.saveas("solid_hatch_polyline_path_with_bulge.dxf")
