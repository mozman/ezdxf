.. _tut_spline:

Tutorial for Spline
===================

Create a simple spline::

    import ezdxf

    dwg = ezdxf.new('AC1015')  # splines requires the DXF 2000 or newer format

    fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]
    msp = dwg.modelspace()
    msp.add_spline(fit_points)

    dwg.saveas("simple_spline.dxf")


Add a fit point to a spline::

    import ezdxf

    dwg = ezdxf.readfile("simple_spline.dxf")

    msp = dwg.modelspace()
    spline = msp.query('SPLINE')[0]  # take the first spline

    # use the context manager
    with spline.edit_data() as data: # data contains standard python lists
        data.fit_points.append((2250, 2500, 0))

        points = data.fit_points[:-1]  # pitfall: this creates a new list without a connection to the spline object
        points.append((3000, 3000, 0))  # has no effect for the spline object

        data.fit_points = points # replace points of fp, this way it works

    # the context manager calls automatically spline.set_fit_points(data.fit_points)

    dwg.saveas("extended_Spline.dxf")

You can set additional `control points`, but if they do not fit the auto-generated AutoCAD values, they will be ignored
and don't mess around with `knot values`.

Solve problems of incorrect values after editing an AutoCAD generated file::

    import ezdxf

    dwg = ezdxf.readfile("AutoCAD_generated.dxf")

    msp = dwg.modelspace()
    spline = msp.query('SPLINE')[0]  # take the first spline
    with spline.edit_data() as data:  # context manger
        data.fit_points.append((2250, 2500, 0))  # data.fit_points is a standard python list

        # As far as I tested this works without complaints from AutoCAD, but for the case of problems
        data.knot_values = []  # delete knot values, this shouldn't modify the geometry of the spline
        data.weights = []  # delete weights, this could modify the geometry of the spline
        data.control_points = []  # delete control points, this could modify the geometry of the spline

    dwg.saveas("modified_Spline.dxf")

Check if spline is closed or close/open spline, for a closed spline the last fit point is connected with the first
fit point::

    if spline.closed:
        # this spline is closed
        pass

    # close a spline
    spline.closed = True

    # open a spline
    spline.closed = False


Set start/end tangent::

    spline.dxf.start_tangent = (0, 1, 0) # in y direction
    spline.dxf.end_tangent = (1, 0, 0) # in x direction

Get count of fit points::

    # as stored in the DXF file
    count = spline.dxf.n_fit_points
    # or count by yourself
    count = len(spline.get_fit_points())

