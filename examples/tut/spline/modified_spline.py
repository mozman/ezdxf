import ezdxf

dwg = ezdxf.readfile("AutoCAD_generated.dxf")

msp = dwg.modelspace()
spline = msp.query('SPLINE')[0]  # take the first spline
with spline.edit_data() as data:  # context manager
    data.fit_points.append((2250, 2500, 0))  # data.fit_points is a standard python list

    # As far as I tested this works without complaints from AutoCAD, but for the case of problems
    data.knot_values = []  # delete knot values, this could modify the geometry of the spline
    data.weights = []  # delete weights, this could modify the geometry of the spline
    data.control_points = []  # delete control points, this could modify the geometry of the spline

dwg.saveas("modified_spline.dxf")
