import ezdxf

dwg = ezdxf.new('AC1015')  # splines requires the DXF R2000 format or later

fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
msp = dwg.modelspace()
msp.add_spline(fit_points)

dwg.saveas("simple_spline.dxf")

