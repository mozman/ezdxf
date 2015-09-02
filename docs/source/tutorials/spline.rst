.. _tut_spline:

Tutorial for Spline
===================

Create a simple spline:

.. literalinclude:: ../../../examples/tut/spline/simple_spline.py

Add a fit point to a spline:

.. literalinclude:: ../../../examples/tut/spline/extended_spline.py

You can set additional `control points`, but if they do not fit the auto-generated AutoCAD values, they will be ignored
and don't mess around with `knot values`.

Solve problems of incorrect values after editing an AutoCAD generated file:

.. literalinclude:: ../../../examples/tut/spline/modified_spline.py

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

