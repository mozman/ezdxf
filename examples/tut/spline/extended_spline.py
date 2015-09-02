import ezdxf

dwg = ezdxf.readfile("simple_spline.dxf")

msp = dwg.modelspace()
spline = msp.query('SPLINE')[0]  # take the first spline

# use the context manager
with spline.edit_data() as data:  # data contains standard python lists
    data.fit_points.append((2250, 2500, 0))

    points = data.fit_points[:-1]  # pitfall: this creates a new list without a connection to the spline object
    points.append((3000, 3000, 0))  # has no effect for the spline object

    data.fit_points = points  # replace points of fp, this way it works

# the context manager calls automatically spline.set_fit_points(data.fit_points)

dwg.saveas("extended_spline.dxf")
