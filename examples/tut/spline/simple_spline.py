import ezdxf

doc = ezdxf.new('AC1015')  # splines requires the DXF R2000 format or later

fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
msp = doc.modelspace()
msp.add_spline(fit_points)

doc.saveas("simple_spline.dxf")

